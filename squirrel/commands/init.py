import os
import shutil

from ..xml import build_project
from ..vars import logger, console
from ..vars import DIRECTORY_NAME


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


def _delete_project_folder(path, warning_msg=None, yes=False):
    if warning_msg is None:
        warning_msg = 'This command will delete your 🐿️  project foldre\n'\
            'proceed? (y/n)'

    if not yes:
        try:
            while (a := console.input(warning_msg)) not in ('y', 'n'):
                pass
        except KeyboardInterrupt:
            a = 'n'
    else:
        a = 'y'

    if a == 'y':
        shutil.rmtree(path)
        return True
    return False


def _reset_project_folder(path, yes=False):
    warning_str = 'A 🐿️  is already present.\n[red bold]'\
        'This action will reset all your data proceed? (y/n)'

    return _delete_project_folder(path, warning_msg=warning_str, yes=yes)
