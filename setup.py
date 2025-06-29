import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "Aria2TUI",
    version = "0.1.5.21",
    author = "Grim",
    author_email = "grimandgreedy@protonmail.com",
    description = "Aria2TUI: A TUI Frontend for the Aria2c Download Manager",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/grimandgreedy/Aria2TUI",
    project_urls = {
        "Bug Tracker": "https://github.com/grimandgreedy/Aria2TUI/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'aria2tui = aria2tui:main',
            # 'aria2tui-post-install=aria2tui.post_install:post_install',
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
        "listpick",
    ],
)
