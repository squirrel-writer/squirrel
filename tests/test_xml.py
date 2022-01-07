import os

from .fixtures import test_directory, initialized
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


def test_update_project_file(initialized):
    xml.update_project_file({
        'name': 'test_update_project_file',
        'goal': 666,
        'description': None,
        'due': None,
        'project-type': None,
    })

    assert xml.get_data_from_project_file() == {
        'name': 'test_update_project_file',
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'goal': '666',
        'description': None,
        'due-date': None,
        'project-type': 'text',
    }

    xml.update_project_file({
        'name': 'test_when_not_all_args_are_passed',
        'goal': 666,
    })

    assert xml.get_data_from_project_file() == {
        'name': 'test_when_not_all_args_are_passed',
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'goal': '666',
        'description': None,
        'due-date': None,
        'project-type': 'text',
    }
