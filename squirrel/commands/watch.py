import os
import subprocess
import time
from datetime import datetime

from inotifyrecursive import INotify, flags

from squirrel import plugin
from ..vars import logger
from ..xml import add_watch_entry

def watch(args):
    logger.debug(args)
    watch_flags = flags.CREATE | flags.MODIFY | flags.DELETE
    wd = os.getcwd()

    watches = (wd, )
    i = INotify()
    for watch in watches:
        i.add_watch_recursive(watch, watch_flags)

    engine = plugin.load_module()

    try:
        while True:
            events = i.read()
            logger.debug(events)
            files = get_files(wd)

            # time get_count
            start = time.time()
            total = engine.get_count(files)
            end = time.time()
            logger.info(f'get_count({len(files)} files) -> {total} took {end - start}')

            added = add_watch_entry(total, datetime.now())
            if added:
                logger.debug('A new watch entry was added')
    except KeyboardInterrupt:
        pass

# TODO: we might benefit from this becoming a plugin
def get_files(path):
    find_output = subprocess.run(
        f'find {path} -type f -not -path "*/[@.]*"',
        shell=True,
        capture_output=True,
        text=True
    )
    return find_output.stdout.strip().split('\n')
