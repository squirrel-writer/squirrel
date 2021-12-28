from .parsers import *
import argparse


def setup_parsers():
    """Sets up all of the argparsers"""
    main_parser = _setup_main_parser()
    subparsers = _setup_subparsers(main_parser)
    init_parser = _setup_init_parser(subparsers)
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
        type=str,
        help='specify a name for the project',
    )

    return init_parser

