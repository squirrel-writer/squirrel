import importlib

from .xml import get_data_from_project_file


def load_module():
    """Loads the module declared in the xml project file.
    The module must have a get_count(files: list) -> int function"""
    project_type = get_data_from_project_file()['project-type']
    return importlib.import_module(f'squirrel.plugins.{project_type}')
