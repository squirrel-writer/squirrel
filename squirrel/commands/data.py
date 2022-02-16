from datetime import date

from squirrel import xml
from squirrel.vars import logger, console, DEFAULT_DATE_FORMAT, DEFAULT_DATETIME_FORMAT
from squirrel.exceptions import ProjectNotSetupCorrectlyError


def data(args):
    logger.debug(args)

    if args.today:
        if args.format is not None:
            return _today(format=args.format)
        return _today()
    elif args.all:
        if args.format is not None:
            return _all(format=args.format)
        return _all()

    return False


def _today(format=DEFAULT_DATETIME_FORMAT):
    today = date.today()
    try:
        watches, _ = xml.get_watches_entry(today)
    except FileNotFoundError:
        return False
    if watches is not None:
        try:
            for dt, count in xml.get_day_watches(watches):
                console.print(f'{dt.strftime(format)}, {count}')
        except ProjectNotSetupCorrectlyError as e:
            logger.error(e)
            return False
    return True


def _all(format=DEFAULT_DATE_FORMAT):
    try:
        watches = xml.get_watches_data()
    except (ProjectNotSetupCorrectlyError, FileNotFoundError):
        return False

    for watch in watches:
        console.print(f'{watch[0].strftime(format)}, {watch[2]}')
    return True
