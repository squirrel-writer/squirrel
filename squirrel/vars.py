import os
import logging

from rich.console import Console


DIRECTORY_NAME = '.squirrel'
PROJECT_FILENAME = 'squirrel-project.xml'
WATCH_FILENAME = 'watch-data.xml'
DAEMON_NAME = 'squirreld'
WATCH_DAEMON_PIDFILE = f'{DAEMON_NAME}.pid'
DAEMON_LOGFILE = f'{DAEMON_NAME}.log'
project_file_path = os.path.join(DIRECTORY_NAME, PROJECT_FILENAME)
watch_file_path = os.path.join(DIRECTORY_NAME, WATCH_FILENAME)
watch_daemon_pidfile_path = os.path.join(DIRECTORY_NAME, WATCH_DAEMON_PIDFILE)
watch_daemon_logfile_path = os.path.join(DIRECTORY_NAME, DAEMON_LOGFILE)

# TODO: find artist and credit him
squirrel_art = """
                              _
                          .-'` `}
                  _./)   /       }
                .'o   \ |       }
                '.___.'`.\    {`
                /`\_/  , `.    }
                \=' .-'   _`\  {
                 `'`;/      `,  }
                    _\       ;  }
                   /__`;-...'--'
"""

console = Console()

logger = logging.getLogger("rich")
