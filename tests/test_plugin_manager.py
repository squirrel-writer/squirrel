import os
import types

import pytest
from squirrel import plugin
from squirrel.vars import PLUGIN_PATH
from squirrel.exceptions import PluginNotSetupCorrectlyError


@pytest.mark.parametrize(
    "plugin_name", [
        'example_plugin',
        'text'
    ]
)
def test_plugin_manager(plugin_name):
    plugin_manager = plugin.PluginManager(plugin_name)

    root_plugin_path = os.path.join(PLUGIN_PATH, plugin_name)
    yaml_plugin_path = os.path.join(root_plugin_path, f'{plugin_name}.yaml')
    plugin_module_path = f'squirrel.plugins.{plugin_name}.{plugin_name}'
    assert plugin_manager.project_type == plugin_name
    assert plugin_manager.root_plugin_path == root_plugin_path
    assert plugin_manager.yaml_plugin_path == yaml_plugin_path
    assert plugin_manager.plugin_module_path == plugin_module_path


def test_plugin_manager_with_nonexistant_plugin():
    plugin_name = 'not_really_a_plugin'
    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        plugin.PluginManager(plugin_name)

    root_plugin_path = os.path.join(PLUGIN_PATH, plugin_name)
    yaml_plugin_path = os.path.join(root_plugin_path, f'{plugin_name}.yaml')

    assert e.type == PluginNotSetupCorrectlyError
    assert str(e.value) == f'Could not find {yaml_plugin_path!r}!'


@pytest.mark.parametrize(
    'plugin_name',
    [
        'text'
    ]
)
def test_load_plugin(plugin_name):
    plugin_manager = plugin.PluginManager(plugin_name)
    imported_plugin = plugin_manager.load()
    assert isinstance(imported_plugin, types.ModuleType)
    assert callable(imported_plugin.get_count)


@pytest.mark.parametrize(
    'plugin_name',
    [
        'example_plugin'
    ]
)
def test_load_plugin_with_deps_not_met(plugin_name):
    plugin_manager = plugin.PluginManager(plugin_name)
    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        plugin_manager.load()
    assert e.type == PluginNotSetupCorrectlyError


def test_parse_yaml_config():
    metadata = plugin.PluginManager.parse_yaml_config(b"""
                                           name: test_plugin
                                           authors:
                                            - squirrel,<mail@mail.com>
                                           description: text here
                                           version: 0.0.0
                                           deps:
                                            sys:
                                              - command1
                                              - command2
                                            pip:
                                              - python_package
                                              - python_module
                                           """, 'test_plugin')
    assert metadata == {
        'name': 'test_plugin',
        'authors': ['squirrel,<mail@mail.com>'],
        'description': 'text here',
        'version': '0.0.0',
        'deps': {
            'sys': ['command1', 'command2'],
            'pip': ['python_package', 'python_module']
        }
    }

    metadata = plugin.PluginManager.parse_yaml_config(b"""
                                           name: test_plugin
                                           authors:
                                            - squirrel,<mail@mail.com>
                                           description: text here
                                           version: 0.0.0
                                           deps:
                                           """, 'test_plugin')
    assert metadata == {
        'name': 'test_plugin',
        'authors': ['squirrel,<mail@mail.com>'],
        'description': 'text here',
        'version': '0.0.0',
        'deps': {}
    }

    metadata = plugin.PluginManager.parse_yaml_config(b"""
                                           name: test_plugin
                                           authors:
                                            - squirrel,<mail@mail.com>
                                           description: text here
                                           version: 0.0.0
                                           """, 'test_plugin')
    assert metadata == {
        'name': 'test_plugin',
        'authors': ['squirrel,<mail@mail.com>'],
        'description': 'text here',
        'version': '0.0.0',
        'deps': {}
    }

    metadata = plugin.PluginManager.parse_yaml_config(b"""
                                           name: test_plugin
                                           authors:
                                            - squirrel,<mail@mail.com>
                                           version: 0.0.0
                                           deps:
                                            sys:
                                              - command
                                            pip:
                                              - python_package
                                           """, 'test_plugin')
    assert metadata == {
        'name': 'test_plugin',
        'authors': ['squirrel,<mail@mail.com>'],
        'description': '',
        'version': '0.0.0',
        'deps': {
            'sys': ['command'],
            'pip': ['python_package']
        }
    }

    metadata = plugin.PluginManager.parse_yaml_config(b"""
                                           name: test_plugin
                                           description: text here
                                           version: 0.0.0
                                           deps:
                                            sys:
                                              - command
                                            pip:
                                              - python_package
                                           """, 'test_plugin')
    assert metadata == {
        'name': 'test_plugin',
        'authors': [],
        'description': 'text here',
        'version': '0.0.0',
        'deps': {
            'sys': ['command'],
            'pip': ['python_package']
        }
    }

    metadata = plugin.PluginManager.parse_yaml_config(b"""
                                           name: test_plugin
                                           authors:
                                           description: text here
                                           version: 0.0.0
                                           deps:
                                            sys:
                                              - command
                                            pip:
                                              - python_package
                                           """, 'test_plugin')
    assert metadata == {
        'name': 'test_plugin',
        'authors': [],
        'description': 'text here',
        'version': '0.0.0',
        'deps': {
            'sys': ['command'],
            'pip': ['python_package']
        }
    }

    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        metadata = plugin.PluginManager.parse_yaml_config(b"""
                                               authors:
                                                - squirrel,<mail@mail.com>
                                               description: text here
                                               version: 0.0.0
                                               """, 'test_plugin')
    assert e.type == PluginNotSetupCorrectlyError
    assert str(e.value) == f'{"name"!r} field not found in yaml config'

    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        metadata = plugin.PluginManager.parse_yaml_config(b"""
                                               name: test_plugin
                                               authors:
                                                - squirrel,<mail@mail.com>
                                               description: text here
                                               """, 'test_plugin')
    assert e.type == PluginNotSetupCorrectlyError
    assert str(e.value) == f'{"version"!r} field not found in yaml config'

    with pytest.raises(PluginNotSetupCorrectlyError) as e:
        metadata = plugin.PluginManager.parse_yaml_config(b"""
                                                          authors:
                                                            * sldkj
                                                            * skdjf
                                               """, 'test_plugin')
    assert e.type == PluginNotSetupCorrectlyError
    assert f'Could not parse {"test_plugin"!r}\'s yaml config' in str(e.value)


@pytest.mark.parametrize(
    'dep, expected',
    [
        ('cd', True),
        ('yes', True),
        ('not_really_a_command', False)
    ]
)
def test_verify_sys_dep(dep, expected):
    assert plugin.PluginManager.verify_sys_dep(dep) == expected


@pytest.mark.parametrize(
    'dep, expected',
    [
        ('math', True),
        ('subprocess', True),
        ('panda', False),
    ]
)
def test_verify_sys_dep(dep, expected):
    assert plugin.PluginManager.verify_pip_dep(dep) == expected
