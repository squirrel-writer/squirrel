import importlib
import os
from glob import iglob

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
    def get_files(path, ignores):
        """Function to find all non-ignored files i project directory"""
        ignore_file = ignores.get('file')
        ignore_dir = ignores.get('dir')
        project_files = []
        for file in iglob('**/*[!f"{set(ignore_file)}"]', recursive=True):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                if file_path.rsplit('/', 1)[0] not in ignore_dir:
                    project_files.append(file_path)
        return project_files

    @staticmethod
    def import_ignores(wd, file, logger):
        """Function to read ignore file and store extensions, dir and files
         to a dictionary"""
        ignores = {
            'dir': [],
            'file': []
            }
        try:
            with open(file, 'r') as file:
                for line in file.readlines():
                    add_line = line.strip()
                    if add_line.startswith('#') or add_line == '':
                        continue
                    elif add_line.endswith('/'):
                        ignores['dir'].append(''.join(f'{wd}/{add_line}'))
                    else:
                        ignores['file'].append(add_line)
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
        if f'{"".join(file.rsplit("/", 1)[:-1])}/' \
                not in self.ignores.get('dir'):
            return True

    def on_created(self, event):
        """Event is created, you can process it now"""
        self.add_watch(event.src_path)

    def on_modified(self, event):
        """Event is modified, you can process it now"""
        self.add_watch(event.src_path)
