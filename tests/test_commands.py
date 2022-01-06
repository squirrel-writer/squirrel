import os

import pytest

from squirrel.squirrel import _main
from squirrel import xml


@pytest.fixture
def test_directory(tmp_path):
    cwd = os.getcwd()
    d = tmp_path / 'test_directory'
    d.mkdir()
    os.chdir(str(d))

    yield True

    #teardown
    os.chdir(cwd)


@pytest.fixture
def initialized(test_directory):
    _main(['init'])


def test_set_command(initialized):
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


def test_init_command():
    pass
