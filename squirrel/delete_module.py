import os
import shutil
from .vars import IGNORE_FILENAME


def delete_project(path, warning_msg=None, yes=False, delete_ignore=False):
    if warning_msg is None:
        warning_msg = 'This command will delete your 🐿️  project folder\n'\
            'proceed? (y/n)'

    if not yes:
        try:
            while (a := input(warning_msg)) not in ('y', 'n'):
                pass
        except KeyboardInterrupt:
            a = 'n'
    else:
        a = 'y'

    if a == 'y':
        if delete_ignore is True and os.path.exists(IGNORE_FILENAME):
            os.remove(IGNORE_FILENAME)
        shutil.rmtree(path)
        return True
    return False
