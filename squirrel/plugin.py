import importlib
import os
import logging

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
        # Ignores have to be converted to tuple and remove '*' at the beginning of ext
        ignores_ext = tuple(i[1:] for i in ignores.get('ext'))
        ignores_file = tuple(ignores.get('file'))
        ignores_dir = tuple(i[:-1] for i in ignores.get('dir_full'))
        project_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file.endswith(ignores_ext) \
                        and not file.startswith('.') \
                        and file not in ignores_file \
                        and root not in ignores_dir:
                    project_files.append(os.path.join(root, file))
        return project_files

    @staticmethod
    def import_ignores(wd, file):
        """Function to read ignore file and store extensions, dir and files
         to a dictionary"""
        ignores = {
            'ext': [],
            'dir': [],
            'dir_full': [],
            'file': []
            }
        with open(file, 'r') as file:
            for line in file.readlines():
                add_line = line.strip()
                if add_line.startswith('#') or add_line == '':
                    continue
                elif add_line.startswith('*'):
                    ignores['ext'].append(add_line)
                elif add_line.endswith('/'):
                    ignores['dir'].append(add_line)
                    ignores['dir_full'].append(''.join(f'{wd}/{add_line}'))
                else:
                    ignores['file'].append(add_line)
        return ignores


class Handler(PatternMatchingEventHandler):

    def __init__(self):
        """Set the patterns for PatternMatchingEventHandler"""
        # 'ignore_patterns' ignore hidden files, atleast on unix filesystems
        # List used to store modified and created files
        self.files = []
        PatternMatchingEventHandler.__init__(
            self, ignore_patterns=['.*', '~*', '*~'], ignore_directories=True)

    def append_watch(self, file):
        """Method to make sure only one event of each file gets processed"""
        if self.not_hidden_folder(file):
            if file not in self.files:
                self.files.append(file)

    def not_hidden_folder(self, file):
        """Checks for hidden folders"""
        path = file.split('/')
        for dir in path:
            if dir.startswith('.'):
                return False
                break
        return True

    def on_created(self, event):
        """Event is created, you can process it now"""
        self.append_watch(event.src_path)

    def on_modified(self, event):
        """Event is modified, you can process it now"""
        self.append_watch(event.src_path)
