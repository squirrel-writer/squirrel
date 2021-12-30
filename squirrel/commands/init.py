import os
import shutil
import xml.etree.ElementTree as ET

from ..xml import build_project
from ..vars import logger, console
from ..vars import DIRECTORY_NAME

def init(args):
    """The entrypoint of init subcommands"""
    logger.debug(f'{args}')

    dict_args = vars(args)

    wd = os.getcwd()
    path = os.path.join(wd, DIRECTORY_NAME)

    if not os.path.isdir(path):
        logger.debug('Initializing new project')
        build_project(dict_args, path)
    else:
        logger.debug('Previous project found')
        if _reset_project_folder(path):
            build_project(dict_args, path)


def _delete_project_folder(path, warning_msg=None):
        if warning_msg is None:
            warning_msg = 'This command will delete your 🐿️  project folde\n'\
                'proceed? (y/n)'

        try:
            while (a := console.input(warning_msg)) not in ('y', 'n'):
                pass
        except KeyboardInterrupt:
            a = 'n'

        if a == 'y':
            shutil.rmtree(path)
            return True
        return False

def _reset_project_folder(path):
        warning_str = 'A 🐿️  is already present.\n[red bold]This action will reset all your data'\
            ' proceed? (y/n)'

        return _delete_project_folder(path, warning_msg=warning_str)

