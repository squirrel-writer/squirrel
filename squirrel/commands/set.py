from ..vars import logger
from ..xml import update_project_file


def set_command(args):
    logger.debug(args)
    dir_args = vars(args)
    update_project_file(dir_args)
