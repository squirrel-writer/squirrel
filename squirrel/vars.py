import os
import logging

from rich.console import Console


DIRECTORY_NAME = '.squirrel'
PROJECT_FILENAME = 'squirrel-project.xml'
WATCH_FILENAME = 'watch-data.xml'
DAEMON_NAME = 'squirreld'
WATCH_DAEMON_PIDFILE = f'{DAEMON_NAME}.pid'
DAEMON_LOGFILE = f'{DAEMON_NAME}.log'
IGNORE_FILENAME = '.squirrelignore'
project_file_path = os.path.join(DIRECTORY_NAME, PROJECT_FILENAME)
watch_file_path = os.path.join(DIRECTORY_NAME, WATCH_FILENAME)
watch_daemon_pidfile_path = os.path.join(DIRECTORY_NAME, WATCH_DAEMON_PIDFILE)
watch_daemon_logfile_path = os.path.join(DIRECTORY_NAME, DAEMON_LOGFILE)
ignore_file_path = IGNORE_FILENAME

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

PLUGIN_PATH = 'plugins/'

squirrel_art = r"""
                              _
                          .-'` `}
                  _./)   /       }
                .'o   \ |       }
                '.___.'`.\    {`
                /`\_/  , `.    }
                \=' .-'   _`\  {
                 `'`;/      `,  }
                    _\       ;  }
               jgs /__`;-...'--'
"""

ignore_file_content = """\
# Add files, extensions and folders to be ignored by Squirrel
# '.*', '*~', '*~' and '.<dir>' is ignored by default

# Ignore folders:
# sample/

# Ignore extensions:
# *.tmp

# Ignore files:
# ignore.txt
# sample/ignore.txt

"""

console = Console()

logger = logging.getLogger("rich")
