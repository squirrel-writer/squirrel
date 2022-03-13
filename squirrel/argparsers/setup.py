import argparse

import dateutil.parser

from .parsers import (MainParserData, SubparsersData,
                      InitParserData, WatchParserData, WatchSubparsersData,
                      StartWatchParserData, StatusWatchParserData, StopWatchParserData,
                      SetParserData, OverviewParserData, DataParserData)
from ..commands import init_cmd, set_cmd, overview_cmd, watch_cmd, data_cmd
from ..commands.watch import status, stop
from ..vars import DEFAULT_DATE_FORMAT


def setup_parsers():
    """Sets up all of the argparsers"""
    main_parser = _setup_main_parser()
    subparsers = _setup_subparsers(main_parser)
    _setup_init_parser(subparsers)
    _setup_set_parser(subparsers)
    _setup_overview_parser(subparsers)
    _setup_watch_parser(subparsers)
    _setup_data_parser(subparsers)

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
        version='%(prog)s 0.0.4',
        help='Show the version of the program',
    )

    main_parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Activate debug mode'
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

    init_parser.add_argument(
        '-p',
        '--project-type',
        metavar='project-type',
        action='store',
        type=str,
        help='specify the project type'
    )

    init_parser.add_argument(
        '-y',
        action='store_true',
        help='ignore input prompts'
    )
    init_parser.set_defaults(func=init_cmd)

    return init_parser


def _setup_watch_parser(subparsers):
    watch_parser = subparsers.add_parser(
        WatchParserData.name,
        description=WatchParserData.desc,
        help=WatchParserData.help,
    )

    subparsers = watch_parser.add_subparsers(
        title=WatchSubparsersData.title,
        help=WatchSubparsersData.help,
        required=True,
    )

    start_parser = subparsers.add_parser(
        StartWatchParserData.name,
        description=StartWatchParserData.desc,
        help=StartWatchParserData.help
    )
    start_parser.add_argument(
        '-d',
        '--daemon',
        action='store_true',
        help='daemonizes the watcher to run in the background'
    )
    start_parser.add_argument(
        '--delay',
        type=int,
        default=3,
        help='Specify a delay (in minutes) when watching files.'
        '\nDefaults 3 minutes.'
    )
    start_parser.set_defaults(func=watch_cmd)

    status_parser = subparsers.add_parser(
        StatusWatchParserData.name,
        description=StatusWatchParserData.desc,
        help=StatusWatchParserData.help
    )
    status_parser.set_defaults(func=status)

    stop_parser = subparsers.add_parser(
        StopWatchParserData.name,
        description=StopWatchParserData.desc,
        help=StopWatchParserData.help
    )
    stop_parser.set_defaults(func=stop)

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

    set_parser.add_argument(
        '-p',
        '--project-type',
        metavar='project-type',
        action='store',
        type=str,
        help='set or change the project type'
    )

    set_parser.set_defaults(func=set_cmd)
    return set_parser


def _setup_overview_parser(subparsers):
    overview_parser = subparsers.add_parser(
        OverviewParserData.name,
        description=OverviewParserData.desc,
        help=OverviewParserData.help
    )

    overview_parser.add_argument(
        '-f',
        '--format',
        type=str,
        help='The date format of the output',
        default=DEFAULT_DATE_FORMAT
    )

    overview_parser.add_argument(
        '-g',
        '--graph',
        action='store_true',
        help='Display a bar chart for the last 5 days of writing'
    )

    overview_parser.set_defaults(func=overview_cmd)
    return overview_parser


def _setup_data_parser(subparsers):
    data_parser = subparsers.add_parser(
        DataParserData.name,
        description=DataParserData.desc,
        help=DataParserData.help
    )

    data_parser.add_argument(
        '-f',
        '--format',
        type=str,
        help='The date format of the output'
    )

    group = data_parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-t',
        '--today',
        action='store_true',
        help='Returns all counts that were recorded today'
    )

    group.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Returns all counts that were recorded'
    )

    data_parser.set_defaults(func=data_cmd)
    return data_parser


def _valid_date(s):
    try:
        return dateutil.parser.parse(s).date()
    except ValueError:
        msg = "Not a valid date"
        raise argparse.ArgumentTypeError(msg)
