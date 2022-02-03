import os
import subprocess
import logging


logger = logging.getLogger(__name__)


def get_count(files) -> int:
    # remove any non latex files (crucial when we have bib files)
    files = list(filter(lambda x: os.path.splitext(x)[1] == '.tex', files))

    output = subprocess.run(
        f'texcount -0 -sum -q {" ".join(files)}',
        shell=True,
        capture_output=True,
        text=True,
    )

    total = list(filter(lambda x: x.isnumeric(),
                 output.stdout.split('\n')))
    if len(total) > 0:
        return int(total[0])
    logger.debug('Did not find value after parsing `texcount` command')
    return 0
