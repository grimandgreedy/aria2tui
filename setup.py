#!/bin/python
# -*- coding: utf-8 -*-
"""
setup.py

Author: GrimAndGreedy
License: MIT
"""

import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "aria2tui",
    version = "0.1.9.3",
    author = "Grim",
    author_email = "grimandgreedy@protonmail.com",
    description = "aria2tui: A TUI Frontend for the Aria2c Download Manager",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/grimandgreedy/aria2tui",
    project_urls = {
        "Bug Tracker": "https://github.com/grimandgreedy/aria2tui/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    keywords='aria2c aria2 downloader listpick tui python curses torrent metalink',
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'aria2tui = aria2tui:main',
        ]
    },
    package_data={
        'aria2tui': ['data/config.toml'],
    },
    data_files=[
        ('~/.config/aria2tui', ['src/aria2tui/data/config.toml']),
    ],
    python_requires = ">=3.0",
    install_requires = [
        "plotille",
        "Requests",
        "tabulate",
        "toml",
        "listpick >= 0.1.11.3",
    ],
)
