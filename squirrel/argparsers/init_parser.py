
class Init:
    name = 'init'
    desc = 'Inialiazation of new projects'
    help = f'Create a new {MainParser.prog} project or reset the existing one'
    init_parser = Subparsers.parsers.add_parser(
        name,
        description=desc,
        help=help,
    )

    init_parser.add_argument(
        '-n',
        '--name',
        metavar='name',
        type=str,
        help='name help',
    )
