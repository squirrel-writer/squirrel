import importlib
import subprocess
import logging

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .xml import get_data_from_project_file


class Plugin():

    def load_module():
        """Loads the module declared in the xml project file.
        The module must have a get_count(files: list) -> int function"""
        project_type = get_data_from_project_file()['project-type']
        return importlib.import_module(f'squirrel.plugins.{project_type}')

    def get_files(path):
        find_output = subprocess.run(
        f'find {path} -type f -not -path "*/[@.]*"',
        shell=True,
        capture_output=True,
        text=True)
        return find_output.stdout.strip().split('\n')

class Handler(PatternMatchingEventHandler):

    def __init__(self):
        """Set the patterns for PatternMatchingEventHandler"""
        # 'ignore_patterns' ignore hidden files, atleast on unix filesystems
        # List used to store modified and created files
        self.files = []
        PatternMatchingEventHandler.__init__(
            self, ignore_patterns=['.*', '~*', '*~'], ignore_directories=True)

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
        # if statement to prevent 'files' to have more than one item of each file
        if self.not_hidden_folder(event.src_path):
            if event.src_path not in self.files:
                self.files.append(event.src_path)

  
    def on_modified(self, event):
        """Event is modified, you can process it now"""
        # if statement to prevent 'files' to have more than one item of each file
        if self.not_hidden_folder(event.src_path):
            if event.src_path not in self.files:
                self.files.append(event.src_path)