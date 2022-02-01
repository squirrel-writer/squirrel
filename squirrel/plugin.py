import importlib
from os import path
from glob import iglob, glob

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .xml import get_data_from_project_file


class Plugin():

    @staticmethod
    def load_module():
        """Loads the module declared in the xml project file.
        The module must have a get_count(files: list) -> int function"""
        project_type = get_data_from_project_file()['project-type']
        return importlib.import_module(f'squirrel.plugins.{project_type}')

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
                        # Add extentions to be passed to Handler()
                        ignores['file'].append(add_line)
                        # Add all files with current extention
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
        # 'ignore_patterns' ignore hidden files, atleast on unix filesystems
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
