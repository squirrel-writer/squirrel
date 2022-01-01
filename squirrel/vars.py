import os
import logging

from rich.console import Console


DIRECTORY_NAME = '.squirrel'
PROJECT_FILENAME = 'squirrel-project.xml'
WATCH_FILENAME = 'watch-data.xml'
project_file_path = os.path.join(DIRECTORY_NAME, PROJECT_FILENAME)
watch_file_path = os.path.join(DIRECTORY_NAME, WATCH_FILENAME)

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
