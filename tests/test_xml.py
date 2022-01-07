import os

from .fixtures import test_directory
from squirrel import xml
from squirrel.vars import DIRECTORY_NAME
from squirrel.squirrel import _main


def test_get_data_from_project_file(test_directory):
    _main(['init', '-n', 'xmltest', '--goal', '10000'])

    assert xml.get_data_from_project_file() == {
        'name': 'xmltest',
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'description': None,
        'goal': str(10000),
        'due-date': None,
        'project-type': 'text'
    }

    # Reinitialize the project with no parameter
    _main(['init', '-y'])

    assert xml.get_data_from_project_file() == {
        'name': None,
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'description': None,
        'goal': '0',
        'due-date': None,
        'project-type': 'text'
    }

