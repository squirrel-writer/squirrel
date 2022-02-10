import os
import time
import multiprocessing as mp
from datetime import datetime

import pytest

from squirrel import xml
from squirrel.squirrel import _main


@pytest.fixture
def test_directory(tmp_path):
    cwd = os.getcwd()
    d = tmp_path / 'test_directory'
    d.mkdir()
    os.chdir(str(d))

    yield True

    # teardown
    os.chdir(cwd)


@pytest.fixture
def initialized(test_directory):
    _main(['init'])


@pytest.fixture
def watching(initialized):
    watch = mp.Process(target=_main, args=(['watch', 'start', '-d'],))
    watch.start()
    watch.join()
    yield True
    _main(['watch', 'stop'])


@pytest.fixture
def one_watch_added(initialized):
    count = 1
    now = datetime.now()
    xml.add_watch_entry(count, now)
    yield (count, now)
