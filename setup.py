import setuptools
import os
import shutil
from setuptools.command.install import install

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

required = [
    "plotille",
    "Requests",
    "tabulate",
    "toml",
    "listpick",
],

# class CopyConfig(install):
#     def run(self):
#         # Run the default install command
#         install.run(self)
#        
#         # Path to the bundled config.toml in the package
#         source = os.path.join(self.install_lib, 'aria2tui', 'data', 'config.toml')
#        
#         # Destination path for the user's config.toml file
#         user_config_dir = os.path.expanduser('~/.config/aria2tui')
#         os.makedirs(user_config_dir, exist_ok=True)
#        
#         destination = os.path.join(user_config_dir, 'config.toml')
#
#         # Copy the file
#         if os.path.exists(source):
#             shutil.copy(source, destination)
#             print(f"Copied config.toml to {destination}")
#         else:
#             print(f"config.toml file not found in {source}")

import os
import shutil
from setuptools import find_packages
from pkg_resources import resource_filename

def post_install():
    # Path to the bundled config.toml in the package
    source = resource_filename('myproject', 'data/config.toml')

    # Destination path for the user's config.toml file
    user_config_dir = os.path.expanduser('~/.config/myproject')
    os.makedirs(user_config_dir, exist_ok=True)

    # Full destination path for the config.toml file
    destination = os.path.join(user_config_dir, 'config.toml')

    # Copy the file if it exists
    if os.path.exists(source):
        shutil.copy(source, destination)
        print(f"Copied config.toml to {destination}")
    else:
        print(f"Error: config.toml not found at {source}")


def get_data_files():
    user_config_dir = os.path.expanduser('~/.config/aria2tui')
    return [
        (user_config_dir, ['src/aria2tui/data/config.toml']),
    ]

setuptools.setup(
    name = "Aria2TUI",
    version = "0.1.5.13",
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
            'aria2tui-post-install=aria2tui.post_install:post_install',
        ]
    },
    package_data={
        'aria2tui': ['data/config.toml'],
    },
    # cmdclass={
    #     'install': CopyConfig,
    # },
    data_files=get_data_files(),
    # data_files=[
    #     ('~/.config/aria2tui', ['src/aria2tui/data/config.toml']),
    # ],
    # package_dir = {"": "src"},
    # packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.0",
    install_requires = required,
)
