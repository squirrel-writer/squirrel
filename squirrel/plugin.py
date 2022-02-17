import pkgutil
import importlib
import subprocess
from os import path
from glob import iglob, glob

from watchdog.events import PatternMatchingEventHandler
import yaml

from .vars import logger, PLUGIN_PATH
from .exceptions import PluginNotSetupCorrectlyError


class Plugin:
    """Hold all the metadata of the plugin as well as the module"""

    def __init__(self, name, description, authors, version, deps, module=None):
        self.name = name
        self.description = description
        self.authors = authors
        self.version = version
        self.deps = deps

        self.module = module

    @property
    def pip_deps(self):
        return self.deps.get('pip', ())

    @property
    def sys_deps(self):
        return self.deps.get('sys', ())


class PluginManager:

    def __init__(self, project_type, logger=logger):
        self.project_type = project_type

        self.plugin_module_path = f'squirrel.plugins.{self.project_type}.{self.project_type}'
        self.root_plugin_path = path.join(PLUGIN_PATH, self.project_type)
        self.yaml_plugin_path = path.join(
            self.root_plugin_path, f'{self.project_type}.yaml')

        try:
            yaml_config_file = pkgutil.get_data(
                __name__, self.yaml_plugin_path)
        except FileNotFoundError:
            raise PluginNotSetupCorrectlyError(
                f'Could not find {self.yaml_plugin_path!r}!')

        yaml_metadata = self.parse_yaml_config(
            yaml_config_file, self.project_type)

        self.selected_plugin = Plugin(*yaml_metadata.values())

        self.logger = logger
        self.loaded = False

    @staticmethod
    def parse_yaml_config(config_file, project_type):
        """Returns the metadata available of a plugin from a yaml file.
        Raises PluginNotSetupCorrectlyError when there's a problem with yaml."""
        try:
            data = yaml.safe_load(config_file)
        except yaml.YAMLError as e:
            raise PluginNotSetupCorrectlyError(
                f'Could not parse {project_type!r}\'s yaml config {e}')

        try:
            name = data['name']
        except KeyError:
            raise PluginNotSetupCorrectlyError(
                f'{"name"!r} field not found in yaml config')

        try:
            version = data['version']
        except KeyError:
            raise PluginNotSetupCorrectlyError(
                f'{"version"!r} field not found in yaml config')

        deps = data.get('deps', {})
        if deps is None:
            deps = {}

        authors = data.get('authors', [])
        if authors is None:
            authors = []

        yaml_metadata = {
            'name': name,
            'description': data.get('description', ''),
            'authors': authors,
            'version': version,
            'deps': deps
        }
        return yaml_metadata

    def verify_pip_deps(self) -> bool:
        for dep in self.selected_plugin.pip_deps:
            if not self.verify_pip_dep(dep):
                self.logger.error(
                    f'• {dep!r} was not found in your pip packages')
                return False
        return True

    @staticmethod
    def verify_pip_dep(dep) -> bool:
        if importlib.util.find_spec(dep) is None:
            return False
        return True

    def verify_sys_deps(self) -> bool:
        for dep in self.selected_plugin.sys_deps:
            present = self.verify_sys_dep(dep)
            if not present:
                self.logger.error(f'• {dep!r} was not found on your system')
                return False
        return True

    @staticmethod
    def verify_sys_dep(dep) -> bool:
        try:
            subprocess.run(f'command -v {dep}',
                           shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def load(self):
        """Loads the module declared in the xml project file.
        The module must have a get_count(files: list) -> int function.
        Raises PluginNotSetupCorrectlyError when there's a problem with using the plugin."""
        if not self.verify_pip_deps():
            raise PluginNotSetupCorrectlyError(
                f'Could not satisfy the pip requirements of {self.selected_plugin.name!r}'
            )

        if not self.verify_sys_deps():
            raise PluginNotSetupCorrectlyError(
                f'Could not satisfy sys requirements of {self.selected_plugin.name!r}'
            )

        try:
            plugin = importlib.import_module(self.plugin_module_path)
            self.loaded = True
        except (ImportError, AttributeError):
            raise PluginNotSetupCorrectlyError(
                f'Could not load {self.project_type!r}')

        self.logger.debug(f'{self.project_type!r} was loaded')

        self.selected_plugin.module = plugin
        return plugin

    @staticmethod
    def get_files(wd, ignores):
        """Function to find all non-ignored files i project directory"""
        ignore = ignores.get('ignore')
        project_files = set()
        for file in iglob('**/*', recursive=True):
            if path.isfile(file):
                file_path = path.join(wd, file)
                project_files.add(file_path)
        project_files.difference_update(ignore)
        return project_files

    @staticmethod
    def import_ignores(wd, file, logger):
        """Function to read ignore file and store extensions, dir and files
         to a dictionary"""
        ignores = {
            'dir': set(),
            'file': [],
            'ignore': set(),
        }
        try:
            with open(file, 'r') as file:
                tmp_ignore = []
                tmp_dir = []
                for line in file.readlines():
                    add_line = line.strip()
                    if add_line.startswith('#') or add_line == '':
                        continue
                    elif add_line.endswith('/'):
                        # Add ignored folders and sub folders
                        # to be passed to Handler()
                        tmp_dir.extend(
                            glob(f'{add_line}/**/', recursive=True,))
                        # Add files inside ignored folder/subfolder
                        # to be passed to get_files()
                        tmp_ignore.extend(
                            glob(f'{add_line}**', recursive=True))
                    elif add_line.startswith('*'):
                        # Add extensions to be passed to Handler()
                        ignores['file'].append(add_line)
                        # Add all files with current extension
                        # to be past to get_files()
                        tmp_ignore.extend(
                            glob(f'**/{add_line}', recursive=True))
                    else:
                        # Add file to be passed to Handler()
                        ignores['file'].append(path.join(wd, add_line))
                        # Add all ignored files to be passed to get_files()
                        tmp_ignore.extend(
                            glob(add_line))

            # Comprehension to add full path to dir for use in Handler()
            {ignores['dir'].add(path.join(wd, f)) for f in tmp_dir}
            # Comprehension to add full path to file for use in get_files()
            {ignores['ignore'].add(path.join(wd, f)) for f in tmp_ignore}
        except FileNotFoundError:
            logger.debug(f'{__name__} No ignore file found <{file}>')
        return ignores


class Handler(PatternMatchingEventHandler):

    def __init__(self, ignores):
        """Set the patterns for PatternMatchingEventHandler"""
        # 'ignore_patterns' ignore hidden files, at least on unix filesystems
        # List used to store modified and created files
        self.files = set()
        self.ignores = ignores
        std_ignore = ['.*', '~*', '*~']
        ignore = std_ignore + self.ignores.get('file')
        PatternMatchingEventHandler.__init__(
            self, ignore_patterns=ignore, ignore_directories=True)

    def add_watch(self, file):
        """Method to make sure only one event of each file gets processed"""
        if self.not_hidden_folder(file) and self.not_ignored_folder(file):
            self.files.add(file)

    def not_hidden_folder(self, file):
        """Checks for hidden folders"""
        path = file.split('/')
        for dir in path:
            if dir.startswith('.'):
                return False
                break
        return True

    def not_ignored_folder(self, file):
        if f'{path.split(file)[0]}/' \
                not in self.ignores.get('dir'):
            return True

    def on_created(self, event):
        """Event is created, you can process it now"""
        self.add_watch(event.src_path)

    def on_modified(self, event):
        """Event is modified, you can process it now"""
        self.add_watch(event.src_path)
