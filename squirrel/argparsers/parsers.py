class MainParserData:
    prog = 'squirrel'
    desc = 'Squirrel is a command-line program for ' \
        'tracking your writing progress.'


class SubparsersData:
    title = 'Verbs'
    help = f'The main way to interact with {MainParserData.prog}'


class InitParserData:
    name = 'init'
    desc = 'Initialization of new projects'
    help = f'Create a new {MainParserData.prog} project or reset the existing one'


class WatchParserData:
    name = 'watch'
    desc = 'Monitoring and tracking writing'
    help = 'Starts to monitor the current directory.' \
        f' Note: a {MainParserData.prog} project must have already been created with `init`'


class WatchSubparsersData:
    title = 'Action'
    help = 'Start/Stop/Status watchers'


class StartWatchParserData:
    name = 'start'
    desc = 'Monitoring and tracking writing'
    help = 'Start monitoring the current directory\n' \
        f' Note: a {MainParserData.prog} project must have already been created with `init`'


class StatusWatchParserData:
    name = 'status'
    desc = 'Monitoring and tracking writing'
    help = 'Status of the daemonized watcher'


class StopWatchParserData:
    name = 'stop'
    desc = 'Stop monitoring and tracking writing'
    help = 'Stop monitoring the current directory\n'\
        'Note: This only works with the daemonized version'


class SetParserData:
    name = 'set'
    desc = 'Set or change information about the project e.g description, name, goal'
    help = 'Set or change information about the project'


class OverviewParserData:
    name = 'overview'
    desc = 'Shows your writing progress'
    help = 'Shows an overview of your writing progress'


class DataParserData:
    name = 'data'
    desc = 'Returns raw data from a squirrel project'
    help = 'Returns squirrel project data in a raw format'


class DeleteParserData:
    name = 'delete'
    desc = 'Deletes a squirrel project'
    help = 'Permanently deletes the squirrel project in the directory you are in'
