import subprocess


def get_count(files) -> int:
    output = subprocess.run(
        f'wc -w {" ".join(files)} | tail -n 1',
        shell=True,
        capture_output=True,
        text=True,
    )

    count = output.stdout.strip().split(' ')[0]

    return int(count)
