import subprocess


def get_count(files) -> int:
    output = subprocess.run(
        f'wc -w {" ".join(files)} | tail -n 1',
        shell=True,
        capture_output=True,
        text=True,
    )
    return int(output.stdout.split(' ')[1])
