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
        torrent_operation = False,
        non_torrent_operation = False,
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
        self.non_torrent_operation = non_torrent_operation
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

def editAria2TUIConfig() -> None:
    """
    Edit the aria2tui config file using a form interface.
    
    Loads the existing config from the default location or ARIA2TUI_CONFIG_PATH,
    populates a form with current values (using defaults for missing fields),
    and saves the updated config back to the same location.
    
    Note: This function is called from within a Picker context, so curses
    color pairs are already initialized and don't need to be set up again.
    """
    import curses
    
    logger.info("editAria2TUIConfig called")
    
    # Get the current config (merges user config with defaults)
    current_config = get_config()
    
    # Get default form structure
    form_data = get_default_config_for_form()
    
    # Populate form with current config values
    # Connection Settings
    form_data["Connection Settings"]["URL"] = current_config["general"]["url"]
    form_data["Connection Settings"]["Port"] = current_config["general"]["port"]
    form_data["Connection Settings"]["Token"] = current_config["general"]["token"]
    
    # Commands - join list items back into command strings
    startup_cmds = current_config["general"]["startup_commands"]
    if isinstance(startup_cmds, list):
        form_data["Commands"]["Startup Commands"] = " && ".join(startup_cmds)
    else:
        form_data["Commands"]["Startup Commands"] = str(startup_cmds)
    
    restart_cmds = current_config["general"]["restart_commands"]
    if isinstance(restart_cmds, list):
        form_data["Commands"]["Restart Commands"] = " && ".join(restart_cmds)
    else:
        form_data["Commands"]["Restart Commands"] = str(restart_cmds)
    
    # Paths
    form_data["Paths"]["Aria2 Config Path"] = (
        current_config["general"]["aria2_config_path"], 
        "file"
    )
    form_data["Paths"]["Terminal File Manager"] = current_config["general"]["terminal_file_manager"]
    form_data["Paths"]["GUI File Manager"] = current_config["general"]["gui_file_manager"]
    form_data["Paths"]["Launch Command"] = current_config["general"]["launch_command"]
    
    # Behavior
    paginate_value = "true" if current_config["general"]["paginate"] else "false"
    form_data["Behavior"]["Paginate"] = (
        paginate_value,
        "cycle",
        ["true", "false"]
    )
    form_data["Behavior"]["Refresh Timer (seconds)"] = str(current_config["general"]["refresh_timer"])
    form_data["Behavior"]["Global Stats Timer (seconds)"] = str(current_config["general"]["global_stats_timer"])
    
    # Appearance
    form_data["Appearance"]["Theme"] = (
        str(current_config["appearance"]["theme"]),
        "cycle",
        ["0", "1", "2", "3", "4", "5"]
    )
    show_right_pane = "true" if current_config["appearance"]["show_right_pane_default"] else "false"
    form_data["Appearance"]["Show Right Pane by Default"] = (
        show_right_pane,
        "cycle",
        ["true", "false"]
    )
    form_data["Appearance"]["Right Pane Default Index"] = (
        str(current_config["appearance"]["right_pane_default_index"]),
        "cycle",
        ["0", "1", "2"]
    )
    
    # Show the form using curses wrapper
    # Color pairs are already initialized by Picker, so we don't need to set them up
    def form_wrapper(stdscr):
        from aria2tui.ui.aria2tui_form import FormApp
        app = FormApp(stdscr, form_data)
        return app.run()
    
    result, saved = curses.wrapper(form_wrapper)
    
    # Only save if user clicked the Save button
    # This prevents overwriting the config file when user discards changes or exits without saving,
    # which would lose comments and formatting in the TOML file
    if saved:
        create_config_from_form(result)
        logger.info("Config file updated successfully")
        
        # Reload modules to pick up new config values
        import importlib
        import sys
        
        # First reload core to get fresh config
        import aria2tui.utils.aria2c.core
        importlib.reload(aria2tui.utils.aria2c.core)
        
        # Reload _lambdas which uses the config
        import aria2tui.utils.aria2c._lambdas
        importlib.reload(aria2tui.utils.aria2c._lambdas)
        
        # Reload the aria2c package __init__ which re-exports lambdas
        import aria2tui.utils.aria2c
        importlib.reload(aria2tui.utils.aria2c)
        
        # Reload menu options which may use config
        import aria2tui.ui.aria2tui_menu_options
        importlib.reload(aria2tui.ui.aria2tui_menu_options)
        
        # Reload the compatibility shim
        import aria2tui.utils.aria2c_utils
        importlib.reload(aria2tui.utils.aria2c_utils)
        
        # Update the currently running aria2tui_app module's namespace with new functions
        import aria2tui.aria2tui_app
        if hasattr(aria2tui.aria2tui_app, 'sendReq'):
            aria2tui.aria2tui_app.sendReq = aria2tui.utils.aria2c.sendReq
        if hasattr(aria2tui.aria2tui_app, 'testConnection'):
            aria2tui.aria2tui_app.testConnection = aria2tui.utils.aria2c.testConnection
        if hasattr(aria2tui.aria2tui_app, 'testAriaConnection'):
            aria2tui.aria2tui_app.testAriaConnection = aria2tui.utils.aria2c.testAriaConnection
        if hasattr(aria2tui.aria2tui_app, 'addDownload'):
            aria2tui.aria2tui_app.addDownload = aria2tui.utils.aria2c.addDownload
        if hasattr(aria2tui.aria2tui_app, 'addTorrent'):
            aria2tui.aria2tui_app.addTorrent = aria2tui.utils.aria2c.addTorrent
        
        logger.info("Reloaded config modules and updated references with new config values")
    else:
        logger.info("Config edit cancelled or discarded by user")


def config_file_exists() -> bool:
    """Check if the aria2tui config file exists."""
    default_path = "~/.config/aria2tui/config.toml"
    
    config_path = default_path
    if "ARIA2TUI_CONFIG_PATH" in os.environ:
        config_path = os.environ["ARIA2TUI_CONFIG_PATH"]
    
    return os.path.exists(os.path.expanduser(config_path))


def get_config_path() -> str:
    """Get the path to the aria2tui config file."""
    default_path = "~/.config/aria2tui/config.toml"
    
    if "ARIA2TUI_CONFIG_PATH" in os.environ:
        return os.environ["ARIA2TUI_CONFIG_PATH"]
    
    return default_path


def get_default_config_for_form() -> dict:
    """Get default config structure formatted for the form UI."""
    return {
        "Connection Settings": {
            "URL": "http://localhost",
            "Port": "6800", 
            "Token": "",
        },
        "Commands": {
            "Startup Commands": "aria2c",
            "Restart Commands": "pkill aria2c && sleep 1 && aria2c",
        },
        "Paths": {
            "Aria2 Config Path": ("~/.config/aria2/aria2.conf", "file"),
            "Terminal File Manager": "yazi",
            "GUI File Manager": "kitty yazi",
            "Launch Command": "xdg-open",
        },
        "Behavior": {
            "Paginate": ("false", "cycle", ["true", "false"]),
            "Refresh Timer (seconds)": "2",
            "Global Stats Timer (seconds)": "1",
        },
        "Appearance": {
            "Theme": ("3", "cycle", ["0", "1", "2", "3", "4", "5"]),
            "Show Right Pane by Default": ("false", "cycle", ["true", "false"]),
            "Right Pane Default Index": ("0", "cycle", ["0", "1", "2"]),
        }
    }


def create_config_from_form(form_data: dict) -> None:
    """Create config file and directories from form data with comments and header."""
    from datetime import datetime
    
    config_path = get_config_path()
    config_dir = os.path.dirname(os.path.expanduser(config_path))
    
    # Create directories if they don't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Convert form data to config structure
    config = {
        "general": {
            "url": form_data["Connection Settings"]["URL"],
            "port": form_data["Connection Settings"]["Port"],
            "token": form_data["Connection Settings"]["Token"],
            "startup_commands": [cmd.strip() for cmd in form_data["Commands"]["Startup Commands"].split("&&") if cmd.strip()],
            "restart_commands": [cmd.strip() for cmd in form_data["Commands"]["Restart Commands"].split("&&") if cmd.strip()],
            "aria2_config_path": form_data["Paths"]["Aria2 Config Path"],
            "paginate": form_data["Behavior"]["Paginate"].lower() == "true",
            "refresh_timer": int(form_data["Behavior"]["Refresh Timer (seconds)"]),
            "global_stats_timer": int(form_data["Behavior"]["Global Stats Timer (seconds)"]),
            "terminal_file_manager": form_data["Paths"]["Terminal File Manager"],
            "gui_file_manager": form_data["Paths"]["GUI File Manager"],
            "launch_command": form_data["Paths"]["Launch Command"],
        },
        "appearance": {
            "theme": int(form_data["Appearance"]["Theme"]),
            "show_right_pane_default": form_data["Appearance"]["Show Right Pane by Default"].lower() == "true",
            "right_pane_default_index": int(form_data["Appearance"]["Right Pane Default Index"]),
        }
    }
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Helper function to format values for TOML
    def format_toml_value(value):
        """Format a Python value as a TOML value string."""
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, str):
            # Escape quotes and backslashes
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, list):
            # Format list of strings
            items = [format_toml_value(item) for item in value]
            return f'[{", ".join(items)}]'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    # Write config file with header, comments, and formatting
    with open(os.path.expanduser(config_path), "w") as f:
        # Write header
        f.write("####################################################\n")
        f.write("##        Aria2TUI Configuration File\n")
        f.write("####################################################\n")
        f.write("\n")
        f.write(f"# Saved on: {timestamp}\n")
        f.write("\n")
        
        # Write [general] section with comments
        f.write("[general]\n")
        f.write(f'port = {format_toml_value(config["general"]["port"])}\n')
        f.write(f'token = {format_toml_value(config["general"]["token"])}\n')
        f.write(f'url = {format_toml_value(config["general"]["url"])}\n')
        f.write("\n")
        
        f.write("# Used for starting and restarting aria2c from within aria2tui\n")
        f.write(f'startup_commands = {format_toml_value(config["general"]["startup_commands"])}\n')
        f.write(f'restart_commands = {format_toml_value(config["general"]["restart_commands"])}\n')
        f.write("\n")
        
        f.write('# Used when "Edit Config" option is chosen in the main menu\n')
        f.write(f'aria2_config_path = {format_toml_value(config["general"]["aria2_config_path"])}\n')
        f.write("\n")
        
        f.write("# File managers\n")
        f.write("## terminal_file_manager will open in the same terminal as Aria2TUI in a blocking fashion;\n")
        f.write("## gui_file_manager will fork a new process and open a new application.\n")
        f.write(f'terminal_file_manager = {format_toml_value(config["general"]["terminal_file_manager"])}\n')
        f.write(f'gui_file_manager = {format_toml_value(config["general"]["gui_file_manager"])}\n')
        f.write("\n")
        
        f.write("# launch_command is used for opening files with the default application\n")
        f.write(f'launch_command = {format_toml_value(config["general"]["launch_command"])}\n')
        f.write("\n")
        
        f.write("# Data refresh time (in seconds) for the global stats and for the download data.\n")
        f.write(f'global_stats_timer = {config["general"]["global_stats_timer"]}\n')
        f.write(f'refresh_timer = {config["general"]["refresh_timer"]}\n')
        f.write("\n")
        
        f.write("# Scrolls by default\n")
        f.write(f'paginate = {str(config["general"]["paginate"]).lower()}\n')
        f.write("\n")
        
        # Write [appearance] section with comments
        f.write("[appearance]\n")
        f.write("# Can change in app from the settings (~) or by pressing `th<Return>\n")
        f.write(f'theme = {config["appearance"]["theme"]}\n')
        f.write("\n")
        
        f.write("# Whether the right pane (DL Info, DL graphs) should be displayed by default when opening aria2tui\n")
        f.write(f'show_right_pane_default = {str(config["appearance"]["show_right_pane_default"]).lower()}\n')
        f.write("\n")
        
        f.write("# Which pane should be displayed first when the sidebar is opened.\n")
        f.write("# [0=DL Files (info), 1=speed graph, 2=progress graph, 3=download pieces]\n")
        f.write(f'right_pane_default_index = {config["appearance"]["right_pane_default_index"]}\n')
    
    logger.info("Config file created at: %s", config_path)


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
