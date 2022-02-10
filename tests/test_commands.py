import os

import pytest

from .fixtures import initialized, test_directory, watching, one_watch_added
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


def test_watch_command_after_init(watching):
    # test if log file was created
    assert os.path.isfile(watch_daemon_logfile_path)
    # test if pidfile was created
    assert os.path.isfile(watch_daemon_pidfile_path)


def test_overview_after_init(initialized):
    return_code = _main(['overview'])
    assert return_code == 0


@pytest.mark.parametrize(
    "args",
    [
        ['set', '-p', 'texcount'],
        ['watch', 'start'],
        ['overview'],
        ['overview', '--graph'],
        ['data', '--today'],
        ['data', '--all']
    ]
)
def test_commands_before_init(args, test_directory, capsys):
    """All commands (except init):
    * return an non zero return code.
    * spit out some error."""
    return_code = _main(args)
    out, err = capsys.readouterr()

    assert return_code != 0
    assert err != ''


@pytest.mark.parametrize(
    'args',
    [
        ['data', '--today'],
        ['data', '--all']
    ]

)
def test_data_command_after_init(args, initialized, capsys):
    return_code = _main(args)
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == ''


def test_data_today_after_watch(one_watch_added, capsys):
    return_code = _main(['data', '--today'])
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == f'{one_watch_added[1]}, {one_watch_added[0]}\n'


def test_data_all_after_watch(one_watch_added, capsys):
    return_code = _main(['data', '--all'])
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == f"{one_watch_added[1].date().strftime('%d/%m/%Y')}, {one_watch_added[0]}\n"
