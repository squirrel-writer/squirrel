import os
import time
import functools
import signal
from datetime import datetime
import logging

from daemonize import Daemonize
from watchdog.observers import Observer

from squirrel.plugin import PluginManager, Handler
from ..vars import \
    logger, watch_daemon_pidfile_path, watch_daemon_logfile_path, \
    DAEMON_NAME, ignore_file_path, console
from ..xml import get_data_from_project_file, add_watch_entry
from ..exceptions import PluginNotSetupCorrectlyError, ProjectNotSetupCorrectlyError


def watch(args):
    logger.debug(args)
    wd = os.getcwd()

    if args.daemon:
        daemon_logger, keep_fds = setup_daemon_logger()
        d = Daemonize(app=DAEMON_NAME,
                      pid=watch_daemon_pidfile_path,
                      action=functools.partial(
                          daemon, wd, daemon_logger, args.delay),
                      logger=daemon_logger,
                      chdir=wd,
                      keep_fds=keep_fds)
        d.start()
        return True
    else:
        try:
            return daemon(wd, logger, args.delay)
        except KeyboardInterrupt:
            return False

    return True


def status(args):
    """Returns the status of squirreld watcher"""
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
    """Kills the squirrel daemon watcher"""
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


def daemon(wd, logger, delay=3):
    watches = wd

    try:
        project_files, ignores, plugin_manager = pre_daemon_setup(
            wd, logger=logger)
    except (PluginNotSetupCorrectlyError, ProjectNotSetupCorrectlyError) as e:
        logger.error(e)
        return False

    engine = plugin_manager.selected_plugin.module

    event_handler = Handler(ignores)
    observer = Observer(timeout=70)
    observer.schedule(event_handler, watches, recursive=True)
    observer.start()
    logger.debug('Watchdog initialized')
    while True:
        # TODO: Avoid testing event_handler as it
        # bypasses the Observer timeout.
        # (I think at least. Watchdog documentation isn't clear
        # on what the timeout does exactly).
        # And leads to some files not being tested.
        if event_handler.files:
            # Make a copy of the files to avoid
            # RuntimeError: Set changed size during iteration
            # TODO: move this logic inside the EventHandler.
            files = list(event_handler.files)

            should_update_count = False

            # For loop to prompt modified files to log and project_files
            for file in files:
                logger.info(f'Found a modified file <{file.split("/")[-1]}>')
                if os.path.exists(file):
                    should_update_count = True
                    project_files.add(file)

                if file in project_files:
                    should_update_count = True

            if should_update_count:
                purge_deleted_files(project_files, logger)
                update_count(engine, project_files, logger=logger)

            # Clears list before a new run.
            # TODO: This should move
            # in the Future inside the EventHandler.
            event_handler.files.clear()

        time.sleep(60 * delay)


def pre_daemon_setup(cwd, logger=logger):
    """Runs all the necessary steps before listening for files.
    Raises ProjectNotSetupCorrectlyError if plugin name is unacessable.
    Raises PluginNotSetupCorrectlyError if there's any problem with the plugin."""
    try:
        project_type = get_data_from_project_file()['project-type']
    except FileNotFoundError:
        raise ProjectNotSetupCorrectlyError()

    try:
        plugin_manager = PluginManager(project_type, logger=logger)
    except PluginNotSetupCorrectlyError:
        raise

    # Loads '.ignore' into a variable
    ignores = plugin_manager.import_ignores(cwd, ignore_file_path, logger)
    logger.debug(f'Added ignores {ignores.get("dir")}{ignores.get("file")}')

    # Loads file in project directory into project_files list
    project_files = plugin_manager.get_files(cwd, ignores)
    logger.info(f'Found {len(project_files)} files in project folder')

    try:
        plugin_manager.load()
    except PluginNotSetupCorrectlyError:
        raise

    return (project_files, ignores, plugin_manager)


def update_count(engine, files, logger=logger):
    # Counts files in project folder
    start = time.time()
    total = engine.get_count(files)
    end = time.time()
    total_time = round(end - start, 3)

    logger.info(
        f'{engine.__name__}: get_count({len(files)} files)'
        f' -> {total} took {total_time}'
    )

    # Adds new entry to watch-data.xml
    added = add_watch_entry(total, datetime.now())
    if added:
        logger.debug('A new watch entry was added')
        return True
    return False


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
