import os
import shutil
import logging
import xml.etree.ElementTree as ET

def init(args):
    """The entrypoint of init subcommands"""
    logging.debug(f'{args}')

    dict_args = vars(args)

    wd = os.getcwd()
    path = os.path.join(wd, '.squirrel')

    if not os.path.isdir(path):
        logging.debug('Initializing new project')
        _create_project_folder(path, dict_args)
    else:
        logging.debug('Previous project found; reseting')
        if _reset_project_folder(path):
            _create_project_folder(path, dict_args)

def _create_project_folder(path, data):
    files = [
        os.path.join(path, 'squirrel-project.xml'),
        os.path.join(path, 'watch-data.xml')
    ]
    os.mkdir(path)

    for file in files:
        with open(file, 'w') as f:
            pass

    _create_squirrel_project_xml(data, files[0])
    _create_watch_data_xml(files[1])


def _create_squirrel_project_xml(data: dict, file):
    squirrel = ET.Element('squirrel', name=f"{data.get('name', '')}")

    path = ET.SubElement(squirrel, 'path', src=f'{os.path.dirname(file)}')

    description = ET.SubElement(squirrel, 'description')
    description.text = data.get('description', '')

    due_date = ET.SubElement(squirrel, 'due-date')
    due_date.text = data.get('due', '').strftime('%d/%m/%Y')

    goal = ET.SubElement(squirrel, 'goal')
    goal.text = data.get('goal', '')

    project_type = ET.SubElement(squirrel, 'project-type')
    goal.text = data.get('project-type', '')

    tree = ET.ElementTree(squirrel)
    ET.indent(tree)
    tree.write(file)


def _create_watch_data_xml(path):
    pass


def _delete_project_folder(path, warning_msg=None):
        if warning_msg is None:
            warning_msg = 'This command will delete your 🐿️  project folde\n'\
                'proceed? (y/n)'

        while (a := input(warning_msg)) not in ('y', 'n'):
            pass

        if a == 'y':
            shutil.rmtree(path)
            return True
        return False

def _reset_project_folder(path):
        warning_str = 'A 🐿️ is already present; This action will reset all your data\n'\
            'proceed? (y/n)'

        return _delete_project_folder(path, warning_msg=warning_str)

