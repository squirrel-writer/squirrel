import logging

from rich.logging import RichHandler

from .argparsers import setup_parsers


def _main():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(message)s",
                        datefmt="[%X]",
                        handlers=[RichHandler()])
    parser = setup_parsers()
    args = parser.parse_args()
    args.func(args)
