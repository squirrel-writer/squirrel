import os
import xml.etree.ElementTree as ET

from .vars import logger
from .vars import DIRECTORY_NAME, PROJECT_FILENAME, WATCH_FILENAME

def build_project(data: dict, path):
    files = [
        os.path.join(path, PROJECT_FILENAME),
        os.path.join(path, WATCH_FILENAME)
    ]
    os.mkdir(path)

    for file in files:
        with open(file, 'w') as f:
            pass

    build_project_file(data, files[0])
    build_watch_file(files[1])


def build_project_file(data: dict, file):
    squirrel = ET.Element('squirrel', name=f"{data.get('name', '')}")

    path = ET.SubElement(squirrel, 'path', src=f'{os.path.dirname(file)}')

    description = ET.SubElement(squirrel, 'description')
    description.text = data.get('description', '')

    due_date = ET.SubElement(squirrel, 'due-date')
    due_date.text = data.get('due', '').strftime('%d/%m/%Y')

    goal = ET.SubElement(squirrel, 'goal')
    goal.text = str(data.get('goal', 0))

    project_type = ET.SubElement(squirrel, 'project-type')
    project_type.text = data.get('project-type', '')

    tree = ET.ElementTree(squirrel)
    ET.indent(tree)
    tree.write(file)

def build_watch_file(file):
    pass

def update_project_file(data: dict):
    path = os.path.join(DIRECTORY_NAME, PROJECT_FILENAME)
    tree = ET.parse(path)
    squirrel = tree.getroot()

    if (name := dir_args.get('name')) is not None:
        squirrel.set('name', name)

    if (desc := dir_args.get('description')) is not None:
        try:
            squirrel.find('description').text = desc
        except AttributeError as e:
            logger.error('[bold red blink]description[/] element was not found in the xml file'\
                         ' try initializing the project again', extra={'markup': True})

    if (goal := dir_args.get('goal')) is not None:
        try:
            squirrel.find('goal').text = goal
        except AttributeError as e:
            logger.error('goal element was not found in the xml file'\
                          ' try initializing the project again')

    if (due := dir_args.get('due')) is not None:
        try:
            squirrel.find('due-date').text = due
        except AttributeError as e:
            logger.error('due-date element was not found in the xml file'\
                          'try init project again')

    tree.write(path)

def get_data_from_project_file():
    path = os.path.join(DIRECTORY_NAME, PROJECT_FILENAME)
    tree = ET.parse(path)
    squirrel = tree.getroot()

    data = {
        'name': squirrel.attrib['name'],
        'path': squirrel.find('path').attrib['src'],
        'description': squirrel.find('description').text,
        'goal': squirrel.find('goal').text,
        'due-date': squirrel.find('due-date').text,
        'project-type': squirrel.find('project-type').text
    }
    return data


