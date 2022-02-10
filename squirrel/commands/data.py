from datetime import date

from squirrel import xml
from squirrel.vars import logger, console
from squirrel.exceptions import ProjectNotSetupCorrectlyError


def data(args):
    logger.debug(args)

    if args.today:
        return _today()
    elif args.all:
        return _all()
    return False


def _today():
    today = date.today()
    try:
        watches, _ = xml.get_watches_entry(today)
    except FileNotFoundError:
        return False
    if watches is not None:
        try:
            for dt, count in xml.get_day_watches(watches):
                console.print(f'{dt}, {count}')
        except ProjectNotSetupCorrectlyError as e:
            logger.error(e)
            return False
    return True


def _all():
    try:
        watches = xml.get_watches_data()
    except (ProjectNotSetupCorrectlyError, FileNotFoundError):
        return False

    for watch in watches:
        console.print(f'{watch[0]}, {watch[2]}')
    return True
