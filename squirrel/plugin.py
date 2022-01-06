import importlib
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

class Handler(PatternMatchingEventHandler):
    files = []

    def __init__(self, patterns):
        # Set the patterns for PatternMatchingEventHandler
        PatternMatchingEventHandler.__init__(
            self, patterns=patterns, ignore_patterns=['.*'], ignore_directories=True)
  
    def on_created(self, event):
        # Event is created, you can process it now
        if event.src_path not in self.files:
            self.files.append(event.src_path)
            logging.info
             

  
    def on_modified(self, event):
        # Event is modified, you can process it now
        if event.src_path not in self.files:
            self.files.append(event.src_path) 