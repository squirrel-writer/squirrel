import argparse
from datetime import datetime

from .parsers import *
from ..commands import init, watch, set_command, overview


def setup_parsers():
    """Sets up all of the argparsers"""
    main_parser = _setup_main_parser()
    subparsers = _setup_subparsers(main_parser)
    init_parser = _setup_init_parser(subparsers)
    watch_parser = _setup_watch_parser(subparsers)
    set_parser = _setup_set_parser(subparsers)
    overview_parser = _setup_overview_parser(subparsers)

    init_parser.set_defaults(func=init)
    watch_parser.set_defaults(func=watch)
    set_parser.set_defaults(func=set_command)
    overview_parser.set_defaults(func=overview)
    return main_parser


def _setup_main_parser():
    main_parser = argparse.ArgumentParser(
        prog=MainParserData.prog,
        description=MainParserData.desc,
    )
    main_parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s 0.1',
        help='Show the version of the program',
    )
    return main_parser

def _setup_subparsers(parent_parser):
    return parent_parser.add_subparsers(
        title=SubparsersData.title,
        help=SubparsersData.help,
        required=True,
    )

def _setup_init_parser(subparsers):
    init_parser = subparsers.add_parser(
        InitParserData.name,
        description=InitParserData.desc,
        help=InitParserData.help,
    )

    init_parser.add_argument(
        '-n',
        '--name',
        metavar='name',
        action='store',
        type=str,
        help='specify a name for the project',
    )

    init_parser.add_argument(
        '-d',
        '--description',
        metavar='description',
        action='store',
        type=str,
        help='specify a description for the project'
    )

    init_parser.add_argument(
        '-g',
        '--goal',
        metavar='goal',
        action='store',
        type=int,
        help='specify your target number of words to reach'
    )

    init_parser.add_argument(
        '--due',
        metavar='due-date',
        action='store',
        type=_valid_date,
        help='specify the due date of the project a.k.a deadline'
    )

    return init_parser

def _setup_watch_parser(subparsers):
    watch_parser = subparsers.add_parser(
        WatchParserData.name,
        description=WatchParserData.desc,
        help=WatchParserData.help,
    )

    watch_parser.add_argument(
        '-d',
        '--deamon',
        action='store_true',
        help='deamonizes the watcher to run in the background'
    )
    return watch_parser


def _setup_set_parser(subparsers):
    set_parser = subparsers.add_parser(
        SetParserData.name,
        description=SetParserData.desc,
        help=SetParserData.help
    )

    set_parser.add_argument(
        '-d',
        '--description',
        metavar='description',
        action='store',
        type=str,
        help='set or change the description'
    )

    set_parser.add_argument(
        '-n',
        '--name',
        metavar='name',
        action='store',
        type=str,
        help='set a name for the project',
    )

    set_parser.add_argument(
        '-g',
        '--goal',
        metavar='goal',
        action='store',
        type=int,
        help='set or change your target number of words to reach'
    )

    set_parser.add_argument(
        '--due',
        metavar='due-date',
        action='store',
        type=_valid_date,
        help='set or change the due date of the project a.k.a deadline'
    )

    return set_parser


def _setup_overview_parser(subparsers):
    overview_parser = subparsers.add_parser(
        OverviewParserData.name,
        description=OverviewParserData.desc,
        help=OverviewParserData.help
    )
    return overview_parser


def _valid_date(s):
    try:
        return datetime.strptime(s, '%d/%m/%Y')
    except ValueError:
        msg = "not a valid date: dd/mm/YYYY"
        raise argparse.ArgumentTypeError(msg)
