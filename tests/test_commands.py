import os

import pytest

from .fixtures import initialized, test_directory, watching
from squirrel.squirrel import _main
from squirrel.vars import project_file_path, watch_file_path, watch_daemon_pidfile_path, watch_daemon_logfile_path
from squirrel import xml


def test_correct_set_command(initialized):
    _main(['set',
           '-p', 'texcount',
           '-n', 'test2',
           '-g', '15',
           '--due', '01/01/2022'
           ])

    project_data = xml.get_data_from_project_file()
    assert project_data['project-type'] == 'texcount'
    assert project_data['name'] == 'test2'
    assert project_data['goal'] == '15'
    assert project_data['due-date'] == '01/01/2022'


def test_incorrect_set_command(test_directory):
    """Test the set command when the project is not initialized"""
    with pytest.raises(SystemExit) as e:
        _main(['set', '-p', 'texcount'])

    assert e.type == SystemExit
    assert e.value.code != 0


def test_init_file_creation(test_directory):
    _main(['init', '-n', 'test_name'])
    try:
        with open(project_file_path, 'r') as f:
            project = f.read()

        with open(watch_file_path, 'r') as f:
            watch = f.read()
    except FileNotFoundError:
        pytest.fail('file projects were not created')

    # remove any whitespace to be able to create a
    # test string without not worrying about indentation and stuff
    project = ''.join(project.split())
    watch = ''.join(watch.split())

    assert project == f'<?xmlversion=\'1.0\'encoding=\'utf-8\'?>' \
        '<squirrelname="test_name">' \
        f'<pathsrc="{os.getcwd()}/.squirrel"/>' \
        '<description/>' \
        '<due-date/>' \
        '<goal>0</goal>' \
        '<project-type>text</project-type>' \
        '</squirrel>'

    assert watch == '<?xmlversion=\'1.0\'encoding=\'utf-8\'?>'\
        '<squirrel><!--Thisisafilegeneratedbysquirrel.Modifyitatyourownrisk.--></squirrel>'


def test_watch_command_after_init(watching):
    # test if log file was created
    assert os.path.isfile(watch_daemon_logfile_path)
    # test if pidfile was created
    assert os.path.isfile(watch_daemon_pidfile_path)


def test_watch_command_before_init(test_directory):
    pass
