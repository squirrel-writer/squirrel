import os

import pytest

from .fixtures import initialized, test_directory, watching
from squirrel.squirrel import _main
from squirrel.vars import DIRECTORY_NAME, project_file_path, watch_file_path, watch_daemon_pidfile_path, watch_daemon_logfile_path
from squirrel import xml


def test_init(test_directory):
    return_code = _main(['init', '-n', 'xmltest', '--goal', '10000'])
    assert return_code == 0

    assert xml.get_data_from_project_file() == {
        'name': 'xmltest',
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'description': None,
        'goal': str(10000),
        'due-date': None,
        'project-type': 'text'
    }

    # Reinitialize the project with no parameter
    return_code = _main(['init', '-y'])
    assert return_code == 0

    assert xml.get_data_from_project_file() == {
        'name': None,
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'description': None,
        'goal': '0',
        'due-date': None,
        'project-type': 'text'
    }


def test_correct_set_command(initialized):
    return_code = _main(['set',
                         '-p', 'texcount',
                         '-n', 'test2',
                         '-g', '15',
                         '--due', '01/01/2022'
                         ])
    assert return_code == 0

    project_data = xml.get_data_from_project_file()
    assert project_data['project-type'] == 'texcount'
    assert project_data['name'] == 'test2'
    assert project_data['goal'] == '15'
    assert project_data['due-date'] == '01/01/2022'


def test_incorrect_set_command(test_directory):
    """Test the set command when the project is not initialized"""
    return_code = _main(['set', '-p', 'texcount'])
    assert return_code != 0


def test_watch_command_after_init(watching):
    # test if log file was created
    assert os.path.isfile(watch_daemon_logfile_path)
    # test if pidfile was created
    assert os.path.isfile(watch_daemon_pidfile_path)


def test_watch_command_before_init(test_directory):
    # If a watche was started without initializing the project
    # it should return a non 0 return code
    return_code = _main(['watch', 'start'])
    assert return_code != 0


def test_overview_before_init(test_directory):
    return_code = _main(['overview'])
    assert return_code != 0

    return_code = _main(['overview', '--graph'])
    assert return_code != 0


def test_overview_after_init(initialized):
    return_code = _main(['overview'])
    assert return_code == 0
