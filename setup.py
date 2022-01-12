import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="squirrel-writer",
    version="0.0.2",
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
        "distlib==0.3.4",
        "filelock==3.4.2; python_version >= '3.7'",
        "packaging==21.3; python_version >= '3.6'",
        "platformdirs==2.4.1; python_version >= '3.7'",
        "pluggy==1.0.0; python_version >= '3.6'",
        "py==1.11.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "pygments==2.11.2; python_version >= '3.5'",
        "pyparsing==3.0.6; python_version >= '3.6'",
        "rich==11.0.0",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "toml==0.10.2; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "tox==3.24.5",
        "virtualenv==20.13.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "watchdog==2.1.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 2 - Pre-Alpha",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["squirrel=squirrel.squirrel:_main", ], },
)
