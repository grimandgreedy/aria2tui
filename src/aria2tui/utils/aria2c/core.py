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


class ConfigManager:
    """
    Singleton configuration manager for aria2tui.

    Manages loading, caching, and reloading of configuration.
    Supports both single-instance (backward compatible) and multi-instance modes.
    Provides getter methods to access current config values without re-reading the file.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = get_config()
            cls._instance._current_instance_index = 0
            cls._instance._instances = []
            cls._instance._shared_config = {}
            cls._instance._load_instances()
        return cls._instance

    def _load_instances(self):
        """Load instances from config if instances array is present."""
        logger.info(f"Config keys: {list(self._config.keys())}")
        logger.info(f"Instances in config: {self._config.get('instances', [])}")

        if "instances" in self._config and self._config["instances"]:
            # Multi-instance mode
            self._instances = self._config.get("instances", [])
            # Store shared settings from general
            self._shared_config = self._config.get("general", {}).copy()
            logger.info(
                f"Multi-instance mode enabled with {len(self._instances)} instance(s)"
            )
        else:
            # Single instance mode (backward compatibility)
            # Treat the entire general section as a single instance
            general = self._config.get("general", {})
            self._instances = [
                {
                    "name": "Default",
                    "url": general.get("url", "http://localhost"),
                    "port": general.get("port", "6800"),
                    "token": general.get("token", ""),
                    "startup_commands": general.get("startup_commands", ["aria2c"]),
                    "restart_commands": general.get(
                        "restart_commands", ["pkill aria2c && sleep 1 && aria2c"]
                    ),
                    "aria2_config_path": general.get(
                        "aria2_config_path", "~/.config/aria2/aria2.conf"
                    ),
                }
            ]
            # Other settings become shared
            self._shared_config = {
                "terminal_file_manager": general.get("terminal_file_manager", "yazi"),
                "gui_file_manager": general.get("gui_file_manager", "kitty yazi"),
                "global_stats_timer": general.get("global_stats_timer", 1),
                "refresh_timer": general.get("refresh_timer", 2),
            }
            logger.info("Single instance mode (backward compatible)")

    def reload(self, path=""):
        """Reload configuration from file."""
        self._config = get_config(path)
        self._load_instances()
        logger.info("Configuration reloaded")

    def get_config(self) -> dict:
        """Get the full configuration dictionary."""
        return self._config

    def get_instances(self) -> list:
        """Get all instances."""
        return self._instances

    def get_instance_count(self) -> int:
        """Get number of instances."""
        return len(self._instances)

    def get_instance_name(self, index: int) -> str:
        """Get name of instance at index."""
        if 0 <= index < len(self._instances):
            return self._instances[index].get("name", f"Instance {index}")
        return ""

    def get_instance_names(self) -> list:
        """Get names of all instances."""
        return [
            inst.get("name", f"Instance {i}") for i, inst in enumerate(self._instances)
        ]

    def get_current_instance(self) -> dict:
        """Get the current active instance config."""
        if self._instances:
            return self._instances[self._current_instance_index]
        return {}

    def get_current_instance_index(self) -> int:
        """Get the current instance index."""
        return self._current_instance_index

    def switch_instance(self, index: int):
        """Switch to a different instance by index."""
        if 0 <= index < len(self._instances):
            self._current_instance_index = index
            logger.info(f"Switched to instance: {self.get_instance_name(index)}")
        else:
            logger.warning(f"Invalid instance index: {index}")

    def get_url(self) -> str:
        """Get the aria2 RPC URL for current instance."""
        instance = self.get_current_instance()
        return instance.get("url", self._shared_config.get("url", "http://localhost"))

    def get_port(self) -> str:
        """Get the aria2 RPC port for current instance."""
        instance = self.get_current_instance()
        return instance.get("port", self._shared_config.get("port", "6800"))

    def get_token(self) -> str:
        """Get the aria2 RPC token for current instance."""
        instance = self.get_current_instance()
        return instance.get("token", self._shared_config.get("token", ""))


    def get_restart_commands(self) -> list:
        """Get the restart commands for current instance."""
        instance = self.get_current_instance()
        return instance.get(
            "restart_commands",
            self._shared_config.get(
                "restart_commands", ["pkill aria2c && sleep 1 && aria2c"]
            ),
        )

    def get_aria2_config_path(self) -> str:
        """Get the aria2 config path for current instance."""
        instance = self.get_current_instance()
        return instance.get(
            "aria2_config_path",
            self._shared_config.get("aria2_config_path", "~/.config/aria2/aria2.conf"),
        )


class Operation:
    def __init__(
        self,
        name: str,
        function: Callable,
        function_args: dict = {},
        meta_args: dict = {},
        exec_only: bool = False,
        accepts_gids_list: bool = False,
        send_request: bool = False,
        view: bool = False,
        picker_view: bool = False,
        form_view: bool = False,
        reapply_terminal_settings=False,
        applicable_statuses=[],
        torrent_operation=False,
        non_torrent_operation=False,
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
    """Get config from file."""
    full_config = get_default_config()
    default_path = "~/.config/aria2tui/config.toml"

    # If a path is explicitly provided, use it
    if path:
        CONFIGPATH = path
    # Otherwise check environment variable
    elif "ARIA2TUI_CONFIG_PATH" in os.environ:
        if os.path.exists(os.path.expanduser(os.environ["ARIA2TUI_CONFIG_PATH"])):
            CONFIGPATH = os.environ["ARIA2TUI_CONFIG_PATH"]
        else:
            CONFIGPATH = default_path
    # Otherwise use default
    else:
        CONFIGPATH = default_path

    ## Ensure that users with old keys in their config are not bothered by key changes
    new_keys_to_old = {
        "startup_commands": "startupcmds",
        "restart_commands": "restartcmds",
        "aria2_config_path": "ariaconfigpath",
    }
    old_keys_to_new = {
        "startupcmds": "startup_commands",
        "restartcmds": "restart_commands",
        "ariaconfigpath": "aria2_config_path",
    }

    if os.path.exists(os.path.expanduser(CONFIGPATH)):
        with open(os.path.expanduser(CONFIGPATH), "r") as f:
            user_config = toml.load(f)

        if "general" in user_config:
            for user_key in user_config["general"]:
                full_config_key = user_key
                if user_key in old_keys_to_new:
                    full_config_key = old_keys_to_new[user_key]
                full_config["general"][full_config_key] = user_config["general"][
                    user_key
                ]
        if "appearance" in user_config:
            for user_key in user_config["appearance"]:
                full_config_key = user_key
                if user_key in old_keys_to_new:
                    full_config_key = old_keys_to_new[user_key]
                full_config["appearance"][full_config_key] = user_config["appearance"][
                    user_key
                ]

        # Copy instances array if present (for multi-instance mode)
        if "instances" in user_config:
            full_config["instances"] = user_config["instances"]

    return full_config


def get_default_config() -> dict:
    default_config = {
        "general": {
            "url": "http://localhost",
            "port": "6800",
            "token": "",
            "startup_commands": ["aria2c"],
            "restart_commands": ["pkill aria2c && sleep 1 && aria2c"],
            "aria2_config_path": "~/.config/aria2/aria2.conf",
            "refresh_timer": 2,
            "global_stats_timer": 1,
            "terminal_file_manager": "yazi",
            "gui_file_manager": "kitty yazi",
        },
        "appearance": {
            "theme": 3,
            "show_right_pane_default": False,
            "right_pane_default_index": 0,
        },
    }
    return default_config


# Global config manager instance - must be instantiated after get_config() is defined
config_manager = ConfigManager()


def restartAria() -> None:
    """Restart aria2 daemon."""
    logger.info("restartAria called")
    restart_commands = config_manager.get_restart_commands()
    for cmd in restart_commands:
        logger.info("Restarting aria2c with command: %s", cmd)
        subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    # Wait before trying to reconnect
    subprocess.run("sleep 2", shell=True, stderr=subprocess.PIPE)


def editConfig() -> None:
    """Edit the config file in nvim."""
    logger.info("editConfig called")
    file = config_manager.get_aria2_config_path()
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

    Supports both single-instance and multi-instance modes. In multi-instance mode,
    creates a separate form section for each instance.
    """
    import curses

    logger.info("editAria2TUIConfig called")

    # Get the current config (merges user config with defaults)
    current_config = config_manager.get_config()

    # Check if multi-instance mode is enabled by checking for instances array
    is_multi = "instances" in current_config and current_config["instances"]

    # Get default form structure
    form_data = get_default_config_for_form()

    if is_multi:
        # Multi-instance mode: create a section for each instance
        instances = current_config["instances"]

        # Remove the single-instance sections (will be replaced with instance-specific sections)
        if "Connection Settings" in form_data:
            del form_data["Connection Settings"]
        if "Commands" in form_data:
            del form_data["Commands"]

        # Create a section for each instance
        for idx, instance in enumerate(instances):
            instance_name = instance.get("name", f"Instance {idx + 1}")
            section_key = f"Instance {idx + 1}: {instance_name}"

            # Get commands and format them
            startup_cmds = instance.get("startup_commands", ["aria2c"])
            if isinstance(startup_cmds, list):
                startup_cmds_str = " && ".join(startup_cmds)
            else:
                startup_cmds_str = str(startup_cmds)

            restart_cmds = instance.get(
                "restart_commands", ["pkill aria2c && sleep 1 && aria2c"]
            )
            if isinstance(restart_cmds, list):
                restart_cmds_str = " && ".join(restart_cmds)
            else:
                restart_cmds_str = str(restart_cmds)

            form_data[section_key] = {
                "Name": instance.get("name", f"Instance {idx + 1}"),
                "URL": instance.get("url", "http://localhost"),
                "Port": instance.get("port", "6800"),
                "Token": instance.get("token", ""),
                "Startup Commands": startup_cmds_str,
                "Restart Commands": restart_cmds_str,
                "Aria2 Config Path": (
                    instance.get("aria2_config_path", "~/.config/aria2/aria2.conf"),
                    "file",
                ),
            }

        # Shared settings from general section
        form_data["File Management"]["Terminal File Manager"] = current_config["general"].get(
            "terminal_file_manager", "yazi"
        )
        form_data["File Management"]["GUI File Manager"] = current_config["general"].get(
            "gui_file_manager", "kitty yazi"
        )
        # Remove Aria2 Config Path from File Management section (it's per-instance)
        if "Aria2 Config Path" in form_data["File Management"]:
            del form_data["File Management"]["Aria2 Config Path"]

        form_data["Behavior"]["Refresh Timer (seconds)"] = str(
            current_config["general"].get("refresh_timer", 2)
        )
        form_data["Behavior"]["Global Stats Timer (seconds)"] = str(
            current_config["general"].get("global_stats_timer", 1)
        )
    else:
        # Single instance mode: use general section
        # Connection Settings
        form_data["Connection Settings"]["URL"] = current_config["general"].get(
            "url", "http://localhost"
        )
        form_data["Connection Settings"]["Port"] = current_config["general"].get(
            "port", "6800"
        )
        form_data["Connection Settings"]["Token"] = current_config["general"].get(
            "token", ""
        )

        # Commands - join list items back into command strings
        startup_cmds = current_config["general"].get("startup_commands", ["aria2c"])
        if isinstance(startup_cmds, list):
            form_data["Commands"]["Startup Commands"] = " && ".join(startup_cmds)
        else:
            form_data["Commands"]["Startup Commands"] = str(startup_cmds)

        restart_cmds = current_config["general"].get(
            "restart_commands", ["pkill aria2c && sleep 1 && aria2c"]
        )
        if isinstance(restart_cmds, list):
            form_data["Commands"]["Restart Commands"] = " && ".join(restart_cmds)
        else:
            form_data["Commands"]["Restart Commands"] = str(restart_cmds)

        # File Management
        form_data["File Management"]["Aria2 Config Path"] = (
            current_config["general"].get(
                "aria2_config_path", "~/.config/aria2/aria2.conf"
            ),
            "file",
        )
        form_data["File Management"]["Terminal File Manager"] = current_config["general"].get(
            "terminal_file_manager", "yazi"
        )
        form_data["File Management"]["GUI File Manager"] = current_config["general"].get(
            "gui_file_manager", "kitty yazi"
        )

        # Behavior
        form_data["Behavior"]["Refresh Timer (seconds)"] = str(
            current_config["general"].get("refresh_timer", 2)
        )
        form_data["Behavior"]["Global Stats Timer (seconds)"] = str(
            current_config["general"].get("global_stats_timer", 1)
        )

    # Appearance (always from appearance section)
    form_data["Appearance"]["Theme"] = (
        str(current_config["appearance"]["theme"]),
        "cycle",
        ["0", "1", "2", "3", "4", "5"],
    )
    show_right_pane = (
        "true" if current_config["appearance"]["show_right_pane_default"] else "false"
    )
    form_data["Appearance"]["Show Right Pane by Default"] = (
        show_right_pane,
        "cycle",
        ["true", "false"],
    )
    form_data["Appearance"]["Right Pane Default Index"] = (
        str(current_config["appearance"]["right_pane_default_index"]),
        "cycle",
        ["0", "1", "2"],
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

        # Reload config using ConfigManager
        # This automatically updates all lambdas that use config_manager
        config_manager.reload()
        logger.info("Configuration reloaded successfully")
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

    return os.path.expanduser(default_path)


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
        "File Management": {
            "Aria2 Config Path": ("~/.config/aria2/aria2.conf", "file"),
            "Terminal File Manager": "yazi",
            "GUI File Manager": "kitty yazi",
        },
        "Behavior": {
            "Refresh Timer (seconds)": "2",
            "Global Stats Timer (seconds)": "1",
        },
        "Appearance": {
            "Theme": ("3", "cycle", ["0", "1", "2", "3", "4", "5"]),
            "Show Right Pane by Default": ("false", "cycle", ["true", "false"]),
            "Right Pane Default Index": ("0", "cycle", ["0", "1", "2"]),
        },
    }


def create_config_from_form(form_data: dict) -> None:
    """Create config file and directories from form data with comments and header.

    Args:
        form_data: Form data from the UI
    """
    from datetime import datetime

    config_path = get_config_path()
    config_dir = os.path.dirname(os.path.expanduser(config_path))

    # Create directories if they don't exist
    os.makedirs(config_dir, exist_ok=True)

    # Determine if this is multi-instance mode by checking form structure
    # If form has "Instance X:" sections, it's multi-instance mode
    # If form has "Connection Settings" section, it's single-instance mode
    has_instance_sections = any(key.startswith("Instance ") for key in form_data.keys())
    has_connection_settings = "Connection Settings" in form_data

    is_multi = has_instance_sections and not has_connection_settings

    # Convert form data to config structure
    if is_multi:
        # Multi-instance mode: rebuild instances array from form sections
        instances = []

        # Find all instance sections (they start with "Instance ")
        for section_name in form_data.keys():
            if section_name.startswith("Instance "):
                section_data = form_data[section_name]

                # Extract instance data
                instance = {
                    "name": section_data.get("Name", "Default"),
                    "url": section_data.get("URL", "http://localhost"),
                    "port": section_data.get("Port", "6800"),
                    "token": section_data.get("Token", ""),
                    "startup_commands": [
                        cmd.strip()
                        for cmd in section_data.get("Startup Commands", "aria2c").split(
                            "&&"
                        )
                        if cmd.strip()
                    ],
                    "restart_commands": [
                        cmd.strip()
                        for cmd in section_data.get(
                            "Restart Commands", "pkill aria2c && sleep 1 && aria2c"
                        ).split("&&")
                        if cmd.strip()
                    ],
                    "aria2_config_path": section_data.get(
                        "Aria2 Config Path", "~/.config/aria2/aria2.conf"
                    ),
                }
                instances.append(instance)

        config = {
            "general": {
                "refresh_timer": int(form_data["Behavior"]["Refresh Timer (seconds)"]),
                "global_stats_timer": int(
                    form_data["Behavior"]["Global Stats Timer (seconds)"]
                ),
                "terminal_file_manager": form_data["File Management"]["Terminal File Manager"],
                "gui_file_manager": form_data["File Management"]["GUI File Manager"],
            },
            "appearance": {
                "theme": int(form_data["Appearance"]["Theme"]),
                "show_right_pane_default": form_data["Appearance"][
                    "Show Right Pane by Default"
                ].lower()
                == "true",
                "right_pane_default_index": int(
                    form_data["Appearance"]["Right Pane Default Index"]
                ),
            },
            "instances": instances,
        }
    else:
        # Single instance mode - convert to instances array format
        # This standardizes the config format going forward
        instance = {
            "name": "Default",
            "url": form_data["Connection Settings"]["URL"],
            "port": form_data["Connection Settings"]["Port"],
            "token": form_data["Connection Settings"]["Token"],
            "startup_commands": [
                cmd.strip()
                for cmd in form_data["Commands"]["Startup Commands"].split("&&")
                if cmd.strip()
            ],
            "restart_commands": [
                cmd.strip()
                for cmd in form_data["Commands"]["Restart Commands"].split("&&")
                if cmd.strip()
            ],
            "aria2_config_path": form_data["File Management"]["Aria2 Config Path"],
        }

        config = {
            "general": {
                "refresh_timer": int(form_data["Behavior"]["Refresh Timer (seconds)"]),
                "global_stats_timer": int(
                    form_data["Behavior"]["Global Stats Timer (seconds)"]
                ),
                "terminal_file_manager": form_data["File Management"]["Terminal File Manager"],
                "gui_file_manager": form_data["File Management"]["GUI File Manager"],
            },
            "appearance": {
                "theme": int(form_data["Appearance"]["Theme"]),
                "show_right_pane_default": form_data["Appearance"][
                    "Show Right Pane by Default"
                ].lower()
                == "true",
                "right_pane_default_index": int(
                    form_data["Appearance"]["Right Pane Default Index"]
                ),
            },
            "instances": [instance],
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
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, list):
            # Format list of strings
            items = [format_toml_value(item) for item in value]
            return f"[{', '.join(items)}]"
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

        # Write instances - always use instances array format (even for single instance)
        f.write("# Define aria2 instances\n")
        f.write("# Each instance connects to a different aria2c daemon\n")
        f.write("# You can add more instances by copying the [[instances]] block\n")
        f.write("\n")
        for instance in config["instances"]:
            f.write("[[instances]]\n")
            f.write(f"name = {format_toml_value(instance.get('name', 'Default'))}\n")
            f.write(
                f"url = {format_toml_value(instance.get('url', 'http://localhost'))}\n"
            )
            f.write(f"port = {format_toml_value(instance.get('port', '6800'))}\n")
            f.write(f"token = {format_toml_value(instance.get('token', ''))}\n")
            f.write("# Used for starting and restarting aria2c from within aria2tui\n")
            f.write(
                f"startup_commands = {format_toml_value(instance.get('startup_commands', ['aria2c']))}\n"
            )
            f.write(
                f"restart_commands = {format_toml_value(instance.get('restart_commands', ['pkill aria2c', 'sleep 1', 'aria2c']))}\n"
            )
            f.write('# Used when "Edit Config" option is chosen in the main menu\n')
            f.write(
                f"aria2_config_path = {format_toml_value(instance.get('aria2_config_path', '~/.config/aria2/aria2.conf'))}\n"
            )
            f.write("\n")

        # Write [general] section with comments
        f.write("[general]\n")
        f.write("# Shared settings (apply to all instances)\n")
        f.write("# File managers\n")
        f.write(
            "## terminal_file_manager will open in the same terminal as Aria2TUI in a blocking fashion;\n"
        )
        f.write(
            "## gui_file_manager will fork a new process and open a new application.\n"
        )
        f.write(
            f"terminal_file_manager = {format_toml_value(config['general']['terminal_file_manager'])}\n"
        )
        f.write(
            f"gui_file_manager = {format_toml_value(config['general']['gui_file_manager'])}\n"
        )
        f.write("\n")
        f.write(
            "# Data refresh time (in seconds) for the global stats and for the download data.\n"
        )
        f.write(f"global_stats_timer = {config['general']['global_stats_timer']}\n")
        f.write(f"refresh_timer = {config['general']['refresh_timer']}\n")
        f.write("\n")


        # Write [appearance] section with comments
        f.write("[appearance]\n")
        f.write(
            "# Can change in app from the settings (~) or by pressing `th<Return>\n"
        )
        f.write(f"theme = {config['appearance']['theme']}\n")
        f.write("\n")

        f.write(
            "# Whether the right pane (DL Info, DL graphs) should be displayed by default when opening aria2tui\n"
        )
        f.write(
            f"show_right_pane_default = {str(config['appearance']['show_right_pane_default']).lower()}\n"
        )
        f.write("\n")

        f.write("# Which pane should be displayed first when the sidebar is opened.\n")
        f.write(
            "# [0=DL Files (info), 1=speed graph, 2=progress graph, 3=download pieces]\n"
        )
        f.write(
            f"right_pane_default_index = {config['appearance']['right_pane_default_index']}\n"
        )

    logger.info("Config file created at: %s", config_path)


def classify_download_string(input_string: str) -> str:
    magnet_link_pattern = r"^magnet:\?xt=urn:btih"
    metalink_pattern = r"^metalink:"
    ftp_pattern = r"^(ftp|ftps|sftp)://"
    http_pattern = r"^(http|https)://"

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
    if (
        os.path.exists(os.path.expanduser(os.path.expandvars(input_string)))
        and os.path.isfile(input_string)
        and input_string.endswith(".torrent")
    ):
        return "Torrent File"

    return ""
