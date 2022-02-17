import os
from datetime import date

import pytest
import yaml

from squirrel.squirrel import _main
from squirrel.exceptions import PluginNotSetupCorrectlyError, ProjectNotSetupCorrectlyError
from squirrel.vars import DIRECTORY_NAME, project_file_path, watch_file_path, watch_daemon_pidfile_path, watch_daemon_logfile_path
from squirrel import xml

from .fixtures import initialized, test_directory, watching, one_watch_added


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
        'goal': None,
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
    assert project_data['due-date'] == date(year=2022, month=1, day=1)


def test_watch_command_log_and_pid_file_creation(watching):
    # test if log file was created
    assert os.path.isfile(watch_daemon_logfile_path)
    # test if pidfile was created
    assert os.path.isfile(watch_daemon_pidfile_path)


def test_watch_when_yaml_plugin_file_not_available(initialized, mocker, caplog):
    # Similate that the yaml config is not present
    mocker.patch(
        'squirrel.plugin.pkgutil.get_data',
        side_effect=FileNotFoundError
    )

    return_code = _main(['watch', 'start'])

    assert return_code != 0
    assert type(caplog.records[-1]) != PluginNotSetupCorrectlyError


def test_watch_when_yaml_plugin_file_unparsable(initialized, mocker, caplog):
    # Similate yaml config is unparsable
    mocker.patch(
        'squirrel.plugin.yaml.safe_load',
        side_effect=yaml.YAMLError
    )

    return_code = _main(['watch', 'start'])

    assert return_code != 0
    assert type(caplog.records[-1].msg) == PluginNotSetupCorrectlyError


def test_watch_when_plugin_unimportable(initialized, mocker, caplog):
    mocker.patch(
        'squirrel.commands.watch.get_data_from_project_file',
        return_value={'project-type': 'text'}
    )

    # similate plugin is unimportable
    mocker.patch(
        'squirrel.plugin.importlib.import_module',
        side_effect=ImportError
    )

    return_code = _main(['watch', 'start'])

    assert return_code != 0
    assert str(caplog.records[-1].msg) == f'Could not load {"text"!r}'


@pytest.mark.skip(reason='Cannot test this on github actions')
def test_watch_status_when_watching(watching, capsys):
    return_code = _main(['watch', 'status'])
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == '● squirreld watcher is running\n'


def test_watch_status_when_not_watching(capsys):
    return_code = _main(['watch', 'status'])
    out, err = capsys.readouterr()

    assert return_code != 0
    assert err == ''
    assert out == '● squirreld watcher is not running\n'


@pytest.mark.parametrize(
    'args',
    [
        ['overview'],
        ['overview', '--graph']
    ]
)
def test_overview_after_init(args, initialized, capsys):
    return_code = _main(args)
    _, err = capsys.readouterr()
    assert return_code == 0
    assert err == ''


@pytest.mark.parametrize(
    'args',
    [
        ['overview'],
        ['overview', '--graph']
    ]
)
def test_overview_when_watch_file_not_parsable(args, initialized, mocker, capsys):
    mocker.patch(
        'squirrel.commands.overview.get_watches_data',
        side_effect=ProjectNotSetupCorrectlyError
    )

    return_code = _main(args)
    out, err = capsys.readouterr()
    assert return_code != 0
    assert err != ''


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
    assert out == f'{one_watch_added[1].strftime("%Y-%m-%d %H:%M:%S")}, {one_watch_added[0]}\n'


@pytest.mark.parametrize(
    'args',
    [
        ['data', '--today', '-f', '%d/%m/%Y %H:%M:%S'],
        ['data', '-t', '-f', '%d-%m-%Y %H:%M'],
    ]
)
def test_data_today_with_custom_format(args, one_watch_added, capsys):
    return_code = _main(args)
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == f'{one_watch_added[1].strftime(args[-1])}, {one_watch_added[0]}\n'


def test_data_all_after_watch(one_watch_added, capsys):
    return_code = _main(['data', '--all'])
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == f"{one_watch_added[1].date().strftime('%Y-%m-%d')}, {one_watch_added[0]}\n"


@pytest.mark.parametrize(
    'args',
    [
        ['data', '--all', '-f', '%d/%m/%Y'],
        ['data', '--all', '-f', '%d-%m-%Y']
    ]
)
def test_data_all_with_custom_format(args, one_watch_added, capsys):
    return_code = _main(args)
    out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ''
    assert out == f"{one_watch_added[1].date().strftime(args[-1])}, {one_watch_added[0]}\n"
