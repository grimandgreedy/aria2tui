#!/bin/python
# -*- coding: utf-8 -*-
"""
core.py - Core abstractions and configuration

Contains:
- Operation class for defining download operations
- Configuration management functions
- Download string classification utilities

Author: GrimAndGreedy
License: MIT
"""

import os
import subprocess
import toml
import re
from typing import Callable

from aria2tui.utils.logging_utils import get_logger

logger = get_logger()


class Operation:
    def __init__(
        self,
        name: str,
        function: Callable,
        function_args:dict = {},
        meta_args: dict = {},
        exec_only: bool = False,
        accepts_gids_list: bool = False,
        send_request: bool = False,
        view: bool = False,
        picker_view: bool = False,
        form_view: bool = False,
        reapply_terminal_settings = False,
        applicable_statuses = [],
        torrent_operation = False
    ):
        self.name = name
        self.function = function
        self.function_args = function_args
        self.meta_args = meta_args
        self.exec_only = exec_only
        self.accepts_gids_list = accepts_gids_list
        self.send_request = send_request
        self.view = view
        self.picker_view = picker_view
        self.form_view = form_view
        self.reapply_terminal_settings = reapply_terminal_settings
        self.applicable_statuses = applicable_statuses
        self.torrent_operation = torrent_operation
        """
        Operation.function(
            stdscr: curses.window,
            gids: list[str],
            fnames: list[str],

        )
        """


def get_config(path="") -> dict:
    """ Get config from file. """
    full_config = get_default_config()
    default_path = "~/.config/aria2tui/config.toml"

    CONFIGPATH = default_path
    if "ARIA2TUI_CONFIG_PATH" in os.environ:
        if os.path.exists(os.path.expanduser(os.environ["ARIA2TUI_CONFIG_PATH"])):
            CONFIGPATH = os.environ["ARIA2TUI_CONFIG_PATH"]

    ## Ensure that users with old keys in their config are not bothered by key changes
    new_keys_to_old = {
        "startup_commands": "startupcmds",
        "restart_commands": "restartcmds",
        "aria2_config_path": "ariaconfigpath",
    }
    old_keys_to_new = {
        "startupcmds": "startup_commands",
        "restartcmds": "restart_commands",
        "ariaconfigpath": "aria2_config_path"
    }

    if os.path.exists(os.path.expanduser(CONFIGPATH)):
        with open(os.path.expanduser(CONFIGPATH), "r") as f:
            user_config = toml.load(f)

        if "general" in user_config:
            for user_key in user_config["general"]:
                full_config_key = user_key
                if user_key in old_keys_to_new:
                    full_config_key = old_keys_to_new[user_key]
                full_config["general"][full_config_key] = user_config["general"][user_key]
        if "appearance" in user_config:
            for user_key in user_config["appearance"]:
                full_config_key = user_key
                if user_key in old_keys_to_new:
                    full_config_key = old_keys_to_new[user_key]
                full_config["appearance"][full_config_key] = user_config["appearance"][user_key]

    return full_config


def get_default_config() -> dict:
    default_config = {
        "general" : {
            "url": "http://localhost",
            "port": "6800",
            "token": "",
            "startup_commands": ["aria2c"],
            "restart_commands": ["pkill aria2c && sleep 1 && aria2c"],
            "aria2_config_path": "~/.config/aria2/aria2.conf",
            "paginate": False,
            "refresh_timer": 2,
            "global_stats_timer": 1,
            "terminal_file_manager": "yazi",
            "gui_file_manager": "kitty yazi",
            "launch_command": "xdg-open",
        },
        "appearance":{
            "theme": 3,
            "show_right_pane_default": False,
            "right_pane_default_index": 0,
        }
    }
    return default_config


def restartAria() -> None:
    """Restart aria2 daemon."""
    logger.info("restartAria called")
    config = get_config()
    for cmd in config["general"]["restart_commands"]:
        logger.info("Restarting aria2c with command: %s", cmd)
        subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    # Wait before trying to reconnect
    subprocess.run("sleep 2", shell=True, stderr=subprocess.PIPE)


def editConfig() -> None:
    """ Edit the config file in nvim. """
    logger.info("editConfig called")
    config =  get_config()

    file = config["general"]["aria2_config_path"]
    cmd = f"nvim {file}"
    logger.info("Opening config file: %s", file)
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)


def classify_download_string(input_string: str) -> str:
    magnet_link_pattern = r'^magnet:\?xt=urn:btih'
    metalink_pattern = r'^metalink:'
    ftp_pattern = r'^(ftp|ftps|sftp)://'
    http_pattern = r'^(http|https)://'

    # Check if the input string matches any of the patterns
    if re.match(magnet_link_pattern, input_string):
        return "Magnet"
    elif re.match(metalink_pattern, input_string):
        return "Metalink"
    elif re.match(ftp_pattern, input_string):
        return "FTP"
    elif re.match(http_pattern, input_string):
        return "HTTP"

    # Check if the input string is a file path
    if os.path.exists(os.path.expanduser(os.path.expandvars(input_string))) and os.path.isfile(input_string) and input_string.endswith(".torrent"):
        return "Torrent File"

    return ""
