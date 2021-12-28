class MainParserData:
    prog = 'squirrel'
    desc = 'Squirrel is a command-line program for ' \
    'tracking your writing progress.'

class SubparsersData:
    title = 'Verbs'
    help = f'The main way to interact with {MainParserData.prog}'

class InitParserData:
    name = 'init'
    desc = 'Inialiazation of new projects'
    help = f'Create a new {MainParserData.prog} project or reset the existing one'
