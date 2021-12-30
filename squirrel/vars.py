import logging

from rich.console import Console

DIRECTORY_NAME = '.squirrel'
PROJECT_FILENAME = 'squirrel-project.xml'
WATCH_FILENAME = 'watch-data.xml'

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
