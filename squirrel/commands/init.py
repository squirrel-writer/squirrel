import os

from ..xml import build_project
from ..vars import logger, console
from ..vars import DIRECTORY_NAME
from ..delete_module import delete_project


def init(args):
    """The entrypoint of init subcommands"""
    logger.debug(f'{args}')

    dict_args = vars(args)

    wd = os.getcwd()
    path = os.path.join(wd, DIRECTORY_NAME)

    initialized = False
    if not os.path.isdir(path):
        logger.debug('Initializing new project')
        initialized = build_project(dict_args, path)
    else:
        logger.debug('Previous project found')
        if _reset_project_folder(path, yes=args.y):
            initialized = build_project(dict_args, path)

    if initialized:
        console.print('Project Initialized!')
        return True
    console.print('Project initialization failed')
    return False


def _reset_project_folder(path, yes=False):
    warning_str = 'A 🐿️  is already present.\n[red bold]'\
        'This action will reset all your data\nproceed? (y/n)'

    return delete_project(path, warning_msg=warning_str, yes=yes, delete_ignore=False)
