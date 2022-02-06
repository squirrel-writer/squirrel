import os
import time
import functools
import signal
from datetime import datetime
import logging

from daemonize import Daemonize

from squirrel.plugin import PluginManager, Handler, Observer
from ..vars import \
    logger, watch_daemon_pidfile_path, watch_daemon_logfile_path, \
    DAEMON_NAME, ignore_file_path, console
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
                      chdir=wd,
                      keep_fds=keep_fds)
        d.start()
        return True
    else:
        try:
            daemon(wd, logger)
        except KeyboardInterrupt:
            return False

    return True


def status(args):
    logger.debug(args)
    pid = get_daemon_pid()
    if pid != -1:
        if pid_exists(pid):
            console.print('[green]●[/] squirreld watcher is running')
            return True
        else:
            console.print('[red]●[/] squirreld watcher is not running')
            return False
    else:
        console.print('[red]●[/] squirreld watcher is not running')
        return False


def stop(args):
    logger.debug(args)
    pid = get_daemon_pid()
    if pid != -1:
        if pid_exists(pid):
            os.kill(pid, signal.SIGTERM)
            console.print('Stopping squirreld watcher')
            return True

    console.print('Could not find pid')
    return False


def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_daemon_pid() -> int:
    """Returns the pid of the running daemon or -1 if not found"""
    path = watch_daemon_pidfile_path
    try:
        with open(path, 'r') as f:
            pid = f.readline()
            return int(pid)
    except (FileNotFoundError, ValueError):
        return -1


def purge_deleted_files(files, logger):
    """Remove deleted files from a list of files"""
    remove_files = set()
    for file in files:
        if not os.path.exists(file):
            logger.info(
                f'Removed temporary/deleted file <{file.split("/")[-1]}>')
            remove_files.add(file)
    files.difference_update(remove_files)


def daemon(wd, logger):
    watches = wd
    plugin_manager = PluginManager(logger=logger)

    # Loads '.ignore' into a variable
    ignores = plugin_manager.import_ignores(wd, ignore_file_path, logger)
    logger.debug(f'Added ignores {ignores.get("dir")}{ignores.get("file")}')

    # Loads file in project directory into project_files list
    project_files = plugin_manager.get_files(wd, ignores)
    logger.info(f'Found {len(project_files)} files in project folder')

    engine = plugin_manager.load()

    event_handler = Handler(ignores)
    observer = Observer(timeout=60)
    observer.schedule(event_handler, watches, recursive=True)
    observer.start()
    logger.debug('Watchdog initialized')
    while True:
        if event_handler.files:
            # For loop to prompt modified files to log and project_files
            for file in event_handler.files:
                logger.info(f'Found a modified file <{file.split("/")[-1]}>')
                if os.path.exists(file):
                    project_files.add(file)

            purge_deleted_files(project_files, logger)

            # Counts files in project folder
            start = time.time()
            total = engine.get_count(project_files)
            end = time.time()
            total_time = round(end - start, 3)
            logger.info(
                f'{engine.__name__}: get_count({len(project_files)} files) -> {total} took {total_time}')
            # Adds new entry to watch-data.xml
            added = add_watch_entry(total, datetime.now())
            if added:
                logger.debug('A new watch entry was added')
            # Clears list before a new run
            event_handler.files.clear()
            time.sleep(60*3)


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
