import os

import pytest

from squirrel.commands import watch
from squirrel.exceptions import PluginNotSetupCorrectlyError, ProjectNotSetupCorrectlyError
from squirrel import plugin

from .fixtures import test_directory, initialized


def test_pre_daemon_setup_before_init(test_directory):
    with pytest.raises(ProjectNotSetupCorrectlyError) as e:
        watch.pre_daemon_setup(os.getcwd())
    assert e.type == ProjectNotSetupCorrectlyError


def test_pre_daemon_setup_after_init(initialized):
    project_files, ignores, plugin_manager = watch.pre_daemon_setup(
        os.getcwd())
    assert isinstance(plugin_manager, plugin.PluginManager)
    assert plugin_manager.loaded
    assert ignores == {
        'dir': set(),
        'file': [],
        'ignore': set()
    }
    assert type(project_files) == set


def test_pre_daemon_setup_wrong_plugin_name(initialized, mocker):
    mocker.patch(
        'squirrel.commands.watch.get_data_from_project_file',
        return_value={'project-type': 'not_a_plugin'}
    )
    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        watch.pre_daemon_setup(os.getcwd())

    assert e.type == PluginNotSetupCorrectlyError


def test_pre_daemon_setup_plugin_not_found(initialized, mocker):
    mocker.patch(
        'squirrel.commands.watch.get_data_from_project_file',
        return_value={'project-type': 'text'}
    )
    mocker.patch(
        'squirrel.plugin.importlib.import_module',
        side_effect=ImportError
    )
    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        watch.pre_daemon_setup(os.getcwd())
    assert e.type == PluginNotSetupCorrectlyError
    assert str(e.value) == f'Could not load {"text"!r}'


def test_pre_daemon_setup_pip_deps_not_met(initialized, mocker):
    mocker.patch(
        'squirrel.commands.watch.get_data_from_project_file',
        return_value={'project-type': 'text'}
    )
    mocker.patch(
        'squirrel.plugin.PluginManager.verify_pip_deps',
        return_value=False
    )
    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        watch.pre_daemon_setup(os.getcwd())
    assert e.type == PluginNotSetupCorrectlyError
    assert str(
        e.value) == f'Could not satisfy the pip requirements of {"text"!r}'


def test_pre_daemon_setup_sys_deps_not_met(initialized, mocker):
    mocker.patch(
        'squirrel.commands.watch.get_data_from_project_file',
        return_value={'project-type': 'text'}
    )
    mocker.patch(
        'squirrel.plugin.PluginManager.verify_sys_deps',
        return_value=False
    )
    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        watch.pre_daemon_setup(os.getcwd())
    assert e.type == PluginNotSetupCorrectlyError
    assert str(e.value) == f'Could not satisfy sys requirements of {"text"!r}'
