import os
from datetime import datetime, date, timedelta

import pytest

from .fixtures import test_directory, initialized, one_watch_added
from squirrel import xml
from squirrel.vars import project_file_path, DIRECTORY_NAME, watch_file_path
from squirrel.squirrel import _main
from squirrel.exceptions import ProjectNotSetupCorrectlyError


def test_get_watches_data_before_init(test_directory):
    with pytest.raises(FileNotFoundError) as e:
        xml.get_watches_data()
    assert e.type == FileNotFoundError


def test_get_watches_data_after_init(initialized):
    watches = xml.get_watches_data()
    assert len(watches) == 0


def test_get_watches_data_after_watch(one_watch_added):
    watches = xml.get_watches_data()
    assert len(watches) == 1
    assert watches == [
        (one_watch_added[1].date(), 0, one_watch_added[0])
    ]


def test_get_watches_entry_before_init(test_directory):
    with pytest.raises(FileNotFoundError) as e:
        xml.get_watches_entry(date.today())

    assert e.type == FileNotFoundError


def test_get_watches_entry_after_init(initialized):
    watches_tag, root = xml.get_watches_entry(date.today())
    assert watches_tag is None
    assert root is not None


def test_get_watches_entry_after_watch(one_watch_added):
    date_of_watch = one_watch_added[1].date()
    watches_tag, root = xml.get_watches_entry(date_of_watch)
    assert watches_tag is not None
    assert len(watches_tag) == 1
    assert watches_tag[0].text == str(one_watch_added[0])

    unavailable_date = date_of_watch - timedelta(days=1)
    watches_tag, root = xml.get_watches_entry(unavailable_date)
    assert watches_tag is None
    assert root is not None


def test_add_watch_entry_before_init(test_directory):
    with pytest.raises(ProjectNotSetupCorrectlyError) as e:
        xml.add_watch_entry(1, datetime.now())
    assert e.type == ProjectNotSetupCorrectlyError


def test_add_watch_entry_after_init(initialized):
    datetime_of_watch = datetime.now()
    assert xml.add_watch_entry(1, datetime_of_watch)
    watches_tag, _ = xml.get_watches_entry(datetime_of_watch.date())
    assert watches_tag is not None
    assert len(watches_tag) == 1
    assert watches_tag[0].text == str(1)


def test_add_watch_entry_after_watch(one_watch_added):
    datetime_of_watch = datetime.now()
    assert not xml.add_watch_entry(1, datetime_of_watch)

    assert xml.add_watch_entry(2, datetime_of_watch)


def test_get_data_from_project_file(test_directory):
    with pytest.raises(FileNotFoundError) as e:
        xml.get_data_from_project_file()
    assert e.type == FileNotFoundError

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
    _main(['init', '-y'])

    assert xml.get_data_from_project_file() == {
        'name': None,
        'path': os.path.join(os.getcwd(), DIRECTORY_NAME),
        'description': None,
        'goal': None,
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


@pytest.mark.parametrize(
    'args,expected',
    [
        ({
            'name': 'test_building_project',
            'description': None,
            'goal': None,
            'due': None,
            'project_type': None,
            'y': False,
        }, (
            lambda cwd: f'<?xmlversion=\'1.0\'encoding=\'utf-8\'?>'
            '<squirrelname="test_building_project">'
            f'<pathsrc="{cwd}/.squirrel"/>'
            '<description/>'
            '<due-date/>'
            '<goal/>'
            '<project-type>text</project-type>'
            '</squirrel>',
            '<?xmlversion=\'1.0\'encoding=\'utf-8\'?>'
            '<squirrel><!--Thisisafilegeneratedbysquirrel.Modifyitatyourownrisk.--></squirrel>'
        )),
        ({
            'name': 'test_building_project',
            'description': 'description here',
            'goal': 10000,
            'due': date.today(),
            'project_type': 'texcount',
            'y': False,
        }, (
            lambda cwd: f'<?xmlversion=\'1.0\'encoding=\'utf-8\'?>'
            '<squirrelname="test_building_project">'
            f'<pathsrc="{cwd}/.squirrel"/>'
            '<description>descriptionhere</description>'
            f'<due-date>{date.today().strftime("%Y-%m-%d")}</due-date>'
            '<goal>10000</goal>'
            '<project-type>texcount</project-type>'
            '</squirrel>',
            '<?xmlversion=\'1.0\'encoding=\'utf-8\'?>'
            '<squirrel><!--Thisisafilegeneratedbysquirrel.Modifyitatyourownrisk.--></squirrel>'
        ))
    ]
)
def test_build_project(args, expected, test_directory):
    path = os.path.join(os.getcwd(), DIRECTORY_NAME)
    xml.build_project(args, path)

    try:
        with open(project_file_path, 'r') as f:
            project = f.read()

        with open(watch_file_path, 'r') as f:
            watch = f.read()
    except FileNotFoundError:
        pytest.fail('file projects were not created')

    # remove any whitespace to be able to create a
    # test string without worrying about indentation and stuff
    project = ''.join(project.split())
    watch = ''.join(watch.split())

    assert project == expected[0](os.getcwd())
    assert watch == expected[1]


def test_parse_before_init(test_directory):
    with pytest.raises(FileNotFoundError) as e:
        xml.parse(os.path.join(os.getcwd(), project_file_path))

    assert e.type == FileNotFoundError
