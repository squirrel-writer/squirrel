import os
import subprocess
import time
import functools
import signal
from datetime import datetime
import logging

# from inotifyrecursive import INotify, flags
from daemonize import Daemonize

from squirrel.plugin import *
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

def file_not_exists(files, logger):
    """Check if file exists and remove it from list of watched file if not"""
    for file in files:
        if not os.path.exists(file):
            logger.info(f'Removed temporary/deleted file <{file.split("/")[-1]}>')
            files.remove(file)

def daemon(wd, logger):

    os.chdir(wd)
    logger.debug('Adding WatchDog watches')
    watches = wd
    engine = Plugin.load_module()

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, watches, recursive=True)
    observer.start()
    while True:
        time.sleep(15)
        if event_handler.files:
            # For loop to prompt modified files to log
            for file in event_handler.files:
                logger.info(f'Found a modified file <{file.split("/")[-1]}>')
                # Check if modified file exists in project_file list
                if file not in project_files:
                    project_files.append(file)
            # Check if file exists
            file_not_exists(project_files, logger)
            # Counts files in project folder
            start = time.time()
            total = engine.get_count(event_handler.files)
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