import logging

from rich.logging import RichHandler

from .argparsers import setup_parsers


def _main():
    parser = setup_parsers()
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(message)s",
                        datefmt="[%X]",
                        handlers=[RichHandler()])

    args.func(args)
