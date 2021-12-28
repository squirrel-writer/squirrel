from .argparsers import setup_parsers


def _main():
    parser = setup_parsers()
    args = parser.parse_args()
    print(args)
