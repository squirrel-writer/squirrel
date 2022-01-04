import os
import subprocess
import time
import functools
import signal
from datetime import datetime
import logging

from inotifyrecursive import INotify, flags
from daemonize import Daemonize

from squirrel import plugin
from ..vars import logger, watch_daemon_pidfile_path, watch_daemon_logfile_path, DAEMON_NAME, console
from ..xml import add_watch_entry


def watch(args):
    logger.debug(args)
    wd = os.getcwd()

    if args.daemon:
        daemon_logger, keep_fds = setup_daemon_logger()
        d = Daemonize(app=DAEMON_NAME,
                      pid=watch_daemon_pidfile_path,
                      action=functools.partial(daemon, wd, daemon_logger),
                      logger=daemon_logger,
                      keep_fds=keep_fds)
        d.start()
    else:
        try:
            daemon(wd, logger)
        except KeyboardInterrupt:
            pass


def status(args):
    logger.debug(args)
    pid = get_daemon_pid()
    if pid != 0:
        if pid_exists(pid):
            console.print('🟢 squirreld watcher is running')
        else:
            console.print('🔴 squirreld watcher is not running')
    else:
        console.print('🔴 squirreld watcher is not running')


def stop(args):
    logger.debug(args)
    pid = get_daemon_pid()
    os.kill(pid, signal.SIGTERM)
    console.print('Stopping squirreld watcher')


def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_daemon_pid() -> int:
    path = watch_daemon_pidfile_path
    try:
        with open(path, 'r') as f:
            pid = f.readline()
            return int(pid)
    except FileNotFoundError:
        return 0


def daemon(wd, logger):
    watch_flags = flags.CREATE | flags.MODIFY | flags.DELETE

#set working dir
    os.chdir(wd)
    logger.debug('Adding inotify watches')
#tuple with working dir
    watches = (wd, )
#start Inotify (Watchdog)
    i = INotify()
#legger til alle watchdir til Inotify
    for watch in watches:
        i.add_watch_recursive(watch, watch_flags)

# laster riktig type plugin etter hva som er definert i squirrel.xml
    engine = plugin.load_module()

    while True:
# Laster alle endrede filer til en List
        events = i.read()

# --> Endre 'count' til True hvis filen ikke er skjulet (.*)
        files = get_files(wd)

        # lazzy fix for when we get event from hidden files
        # or files from hidden directories
        count = False
        for event in events:
            fullpath = os.path.join(i.get_path(event.wd), event.name)
            if fullpath in files:
                count = True
                break
# <---

        if count:
            # time get_count
            start = time.time()
# teller ord i alle filer som finnes i 'files'
            total = engine.get_count(files)
            end = time.time()
            logger.info(
                f'{engine.__name__}: get_count({len(files)} files) -> {total} took {end - start}')

            added = add_watch_entry(total, datetime.now())
            if added:
                logger.debug('A new watch entry was added')


def setup_daemon_logger():
    daemon_logger = logging.getLogger(DAEMON_NAME)
    daemon_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(watch_daemon_logfile_path)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    daemon_logger.addHandler(fh)
    keep_fds = [fh.stream.fileno()]

    return daemon_logger, keep_fds


# TODO: we might benefit from this becoming a plugin
def get_files(path):
    find_output = subprocess.run(
        f'find {path} -type f -not -path "*/[@.]*"',
        shell=True,
        capture_output=True,
        text=True
    )
    return find_output.stdout.strip().split('\n')
