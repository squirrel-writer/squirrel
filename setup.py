import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="squirrel",
    version="0.0.1",
    author="Mohieddine Drissi",
    author_email="m.drissi@protonmail.com",
    url="https://github.com/squirrel-writer/squirrel",
    description="A command line program to track writing progress",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "colorama==0.4.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "commonmark==0.9.1",
        "daemonize==2.5.0",
        "inotify-simple==1.3.5; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "inotifyrecursive==0.3.5",
        "pygments==2.11.1; python_version >= '3.5'",
        "rich==10.16.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GPLv3 License",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["squirrel=squirrel.squirrel:_main",],},
)
