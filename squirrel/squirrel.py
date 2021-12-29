from .argparsers import setup_parsers
import logging


def _main():
    logging.basicConfig(level=logging.DEBUG)
    parser = setup_parsers()
    args = parser.parse_args()
    args.func(args)
