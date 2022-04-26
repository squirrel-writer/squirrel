import os

from ..delete_module import delete_project
from ..vars import DIRECTORY_NAME


def delete_command(args):
    wd = os.getcwd()
    path = os.path.join(wd, DIRECTORY_NAME)
    return delete_project(path, warning_msg=None, yes=False, delete_ignore=True)
