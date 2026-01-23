#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2tui_app.py

Author: GrimAndGreedy
License: MIT
"""

import os
import sys


# Redirect stderr to prevent artifacts from affecting TUI
_original_stderr = sys.stderr
sys.stderr = open(os.devnull, "w")


from sys import exit
import tempfile
import time
import toml
import json
import curses
import subprocess
import logging
import importlib
from pathlib import Path

from listpick.listpick_app import *
from listpick.listpick_app import (
    Picker,
    start_curses,
    close_curses,
    restrict_curses,
    unrestrict_curses,
    default_option_selector,
    right_split_display_list,
)
from listpick.utils.picker_state import DynamicPickerState

from aria2tui.lib.aria2c_wrapper import *

# from aria2tui.utils.aria2c_utils import *
from aria2tui.utils.aria2c_utils import (
    Operation,
    applyToDownloads,
    sendReq,
    flatten_data,
    get_config,
    config_file_exists,
    get_default_config_for_form,
    create_config_from_form,
    testConnection,
    testAriaConnection,
    classify_download_string,
    addDownload,
    addTorrent,
    editAria2TUIConfig,
)
from aria2tui.utils.aria2c.core import config_manager, get_config_path
from aria2tui.ui.aria2_detailing import (
    highlights,
    menu_highlights,
    modes,
    operations_highlights,
)
from aria2tui.ui.aria2tui_keys import download_option_keys
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid
from aria2tui.ui.aria2tui_menu_options import (
    menu_options,
    download_options,
    menu_data,
    downloads_data,
    dl_operations_data,
)
from aria2tui.ui.aria2tui_form import FormViewerApp
from aria2tui.utils.logging_utils import configure_logging, get_logger

logger = get_logger()


class Aria2TUI:
    def __init__(
        self,
        stdscr: curses.window,
        download_options: list[Operation],
        menu_options: list[Operation],
        menu_data: dict,
        downloads_data: dict,
        dl_operations_data: dict,
        debug: bool = False,
    ):
        logger.info("Aria2TUI initialized (debug=%s)", debug)
        self.stdscr = stdscr
        self.download_options = download_options
        self.menu_options = menu_options
        self.menu_data = menu_data
        self.downloads_data = downloads_data
        self.dl_operations_data = dl_operations_data
        self.debug = debug
        self.add_require_option_to_dl_operations()

    def add_require_option_to_dl_operations(self) -> None:
        self.dl_operations_data["require_option"] = [
            False if option.name not in "Change Position in Queue" else True
            for option in self.download_options
        ]
        self.dl_operations_data["option_functions"] = [
            None
            if option.name != "Change Position in Queue"
            else lambda stdscr, refresh_screen_function=None: default_option_selector(
                stdscr,
                field_prefix=" Download Position: ",
                refresh_screen_function=refresh_screen_function,
            )
            for option in self.download_options
        ]

    def check_and_reapply_terminal_settings(
        self, menu_option: Operation, stdscr: curses.window
    ):
        if menu_option.reapply_terminal_settings:
            restrict_curses(stdscr)
            unrestrict_curses(stdscr)

    def run(self) -> None:
        """
        Run Aria2TUI app loop.
        """

        logger.info("Aria2TUI.run() started")

        # Create the main menu, downloads, and operations Picker objects
        DownloadsPicker = Picker(self.stdscr, **self.downloads_data)
        DownloadsPicker.load_input_history("~/.config/aria2tui/cmdhist.json")

        # Enable verbose mode if debug flag is set
        if self.debug:
            DownloadsPicker.verbose = True
            logger.info("DownloadsPicker verbose mode enabled")

        MenuPicker = Picker(self.stdscr, **self.menu_data)
        DownloadOperationPicker = Picker(self.stdscr, **self.dl_operations_data)

        while True:
            ## DISPLAY DOWNLOADS
            selected_downloads, opts, self.downloads_data = DownloadsPicker.run()
            logger.info(
                "DownloadsPicker.run() returned selected_downloads=%s",
                selected_downloads,
            )

            # When going back to the Downloads picker after selecting a download it shouldn't wait to get new data before displaying the picker
            DownloadsPicker.get_data_startup = False

            if selected_downloads:
                ## CHOOSE OPERATION TO APPLY TO SELECTED DOWNLOADS

                # Filter download operations menu based on selections
                status_index = DownloadsPicker.header.index("Status")
                type_index = DownloadsPicker.header.index("Type")
                selected_download_statuses = [
                    DownloadsPicker.items[selected_index][status_index]
                    for selected_index in selected_downloads
                ]
                selected_download_types = [
                    DownloadsPicker.items[selected_index][type_index]
                    for selected_index in selected_downloads
                ]

                if len(set(selected_download_statuses)) == 1:
                    status = selected_download_statuses[0]
                    applicable_download_operations = [
                        dl_opt
                        for dl_opt in download_options
                        if status in dl_opt.applicable_statuses
                    ]
                else:
                    applicable_download_operations = download_options

                # If selected downloads are not all torrents remove menu options only applicable to torrents
                if not set(selected_download_types) == set(["torrent"]):
                    applicable_download_operations = [
                        dl_opt
                        for dl_opt in applicable_download_operations
                        if not dl_opt.torrent_operation
                    ]
                else:
                    applicable_download_operations = [
                        dl_opt
                        for dl_opt in applicable_download_operations
                        if not dl_opt.non_torrent_operation
                    ]

                self.dl_operations_data["items"] = [
                    [download_option.name]
                    for download_option in applicable_download_operations
                ]

                # Ensure that change position in queue
                self.dl_operations_data["require_option"] = [
                    False if option.name not in "Change Position in Queue" else True
                    for option in applicable_download_operations
                ]
                self.dl_operations_data["option_functions"] = [
                    None
                    if option.name != "Change Position in Queue"
                    else lambda stdscr,
                    refresh_screen_function=None: default_option_selector(
                        stdscr,
                        field_prefix=" Download Position: ",
                        refresh_screen_function=refresh_screen_function,
                    )
                    for option in applicable_download_operations
                ]

                # Get filenames to display in right pane
                items, header = (
                    self.downloads_data["items"],
                    self.downloads_data["header"],
                )
                gid_index, fname_index = header.index("GID"), header.index("Name")
                gids = [
                    item[gid_index]
                    for i, item in enumerate(items)
                    if i in selected_downloads
                ]
                fnames = [
                    item[fname_index]
                    for i, item in enumerate(items)
                    if i in selected_downloads
                ]

                # Display the download names in a right pane
                self.dl_operations_data["right_panes"] = [
                    {
                        "proportion": 1 / 3,
                        "auto_refresh": False,
                        "get_data": lambda data, state: [],
                        "display": right_split_display_list,
                        "data": ["Selected...", fnames],
                        "refresh_time": 1.0,
                    },
                ]
                self.dl_operations_data["split_right"] = True

                DownloadOperationPicker.set_function_data(self.dl_operations_data)
                selected_operation, opts, self.dl_operations_data = (
                    DownloadOperationPicker.run()
                )
                if selected_operation:
                    operation = applicable_download_operations[selected_operation[0]]

                    user_opts = self.dl_operations_data["user_opts"]

                    logger.info(
                        "Applying operation '%s' to gids=%s fnames=%s user_opts=%s",
                        operation.name,
                        gids,
                        fnames,
                        user_opts,
                    )

                    ## APPLY THE SELECTED OPERATION TO THE SELECTED DOWNLOADS
                    applyToDownloads(
                        stdscr=self.stdscr,
                        operation=operation,
                        gids=gids,
                        user_opts=user_opts,
                        fnames=fnames,
                    )

                    self.downloads_data["selections"] = {}
                    self.dl_operations_data["user_opts"] = ""
                    self.check_and_reapply_terminal_settings(operation, self.stdscr)
                else:
                    continue

            else:
                ## If we have not selected any downloads, then we have exited the downloads picker
                ## DISPLAY MAIN MENU
                logger.info("Entering main menu loop")
                while True:
                    selected_menu, opts, self.menu_data = MenuPicker.run()

                    # If we exit from the menu then exit altogether
                    if not selected_menu:
                        DownloadsPicker.save_input_history(
                            "~/.config/aria2tui/cmdhist.json"
                        )
                        close_curses(self.stdscr)
                        logger.info("Exiting main menu loop and application")
                        return

                    menu_option = self.menu_options[selected_menu[0]]
                    logger.info("Menu option selected: %s", menu_option.name)
                    if menu_option.name == "View Downloads":
                        DownloadsPicker.auto_refresh = False
                        break
                    elif menu_option.name == "Watch Downloads":
                        DownloadsPicker.auto_refresh = True
                        break

                        # response = sendReq(menu_option.function(**menu_option.function_args))
                    result = menu_option.function(
                        stdscr=self.stdscr,
                        gids=[],
                        fnames=[],
                        operation=menu_option,
                        function_args=menu_option.function_args,
                    )
                    if menu_option.send_request:
                        result = sendReq(result)
                    ## if it is a view operation such as "View Global Stats" then send the request and open it with nvim
                    if menu_option.view:
                        # Ensure that the screen is cleared after nvim closes, otherwise artifcats remain.
                        DownloadsPicker.clear_on_start = True
                        MenuPicker.clear_on_start = True
                        # response = sendReq(menu_option.function(**menu_option.function_args))
                        with tempfile.NamedTemporaryFile(
                            delete=False, mode="w"
                        ) as tmpfile:
                            tmpfile.write(json.dumps(result, indent=4))
                            tmpfile_path = tmpfile.name
                        # cmd = r"""nvim -i NONE -c 'setlocal bt=nofile' -c 'silent! %s/^\s*"function"/\0' -c 'norm ggn'""" + f" {tmpfile_path}"
                        cmd = f"nvim {tmpfile_path}"
                        process = subprocess.run(
                            cmd, shell=True, stderr=subprocess.PIPE
                        )
                        self.check_and_reapply_terminal_settings(
                            menu_option, self.stdscr
                        )

                    ## If it is a picker view operation then send the request and display it in a Picker
                    elif menu_option.picker_view:
                        DownloadsPicker.clear_on_start = True
                        MenuPicker.clear_on_start = True

                        result = flatten_data(result)
                        resp_list = [[key, val] for key, val in result.items()]
                        config = get_config()
                        colour_theme_number = config["appearance"]["theme"]
                        x = Picker(
                            self.stdscr,
                            items=resp_list,
                            header=["Key", "Val"],
                            title=menu_option.name,
                            colour_theme_number=colour_theme_number,
                            reset_colours=False,
                            cell_cursor=False,
                        )
                        x.run()

                    elif menu_option.form_view:
                        # Display structured data in the read-only form viewer
                        DownloadsPicker.clear_on_start = True
                        MenuPicker.clear_on_start = True

                        # Unwrap JSON-RPC style responses
                        if isinstance(result, dict) and "result" in result:
                            payload = result["result"]
                        else:
                            payload = result

                        # Flatten nested structures where possible
                        try:
                            flat = flatten_data(payload)
                        except Exception:
                            flat = {"value": json.dumps(payload, indent=2, default=str)}

                        section_fields = {}
                        for key, val in flat.items():
                            section_fields[str(key)] = str(val)

                        form_dict = {str(menu_option.name): section_fields}

                        viewer = FormViewerApp(self.stdscr, form_dict)
                        viewer.run()

                    else:
                        if (
                            "display_message" in menu_option.meta_args
                            and menu_option.meta_args["display_message"]
                        ):
                            display_message(
                                self.stdscr, menu_option.meta_args["display_message"]
                            )
                        self.check_and_reapply_terminal_settings(
                            menu_option, self.stdscr
                        )

                        # Add notification of success or failure to listpicker
                        if result not in ["", None, []]:
                            # If we have are returning gids and a status message then set the startup notification to the status message.
                            if type(result) == type((0, 0)) and len(result) == 2:
                                if type(result[0]) == type([]) and type(
                                    result[1]
                                ) == type(""):
                                    DownloadsPicker.startup_notification = str(
                                        result[1]
                                    )

                        self.stdscr.clear()
                        self.stdscr.refresh()
                        break


def display_message(stdscr: curses.window, msg: str) -> None:
    """Display a given message using curses."""
    h, w = stdscr.getmaxyx()
    if h > 8 and w > 20:
        stdscr.addstr(h // 2, (w - len(msg)) // 2, msg)
        stdscr.refresh()


def handleConfigSetup(stdscr):
    """
    Handles the config file setup if it doesn't exist.

    Checks for the presence of a config file at ~/.config/aria2tui/config.toml
    (or ARIA2TUI_CONFIG_PATH if set). If the config file doesn't exist,
    presents the user with a form to create it.

    Returns:
        tuple: (success: bool, new_stdscr: curses.window or None)
    """
    logger.info("handleConfigSetup() called")

    if config_file_exists():
        logger.info("Config file already exists")
        return True, stdscr

    logger.info("Config file does not exist, showing setup form")

    # Get default config for the form
    form_data = get_default_config_for_form()

    # Show the form
    from aria2tui.ui.aria2tui_form import run_form

    # Temporarily exit curses to run the form
    close_curses(stdscr)

    try:

        def form_wrapper(stdscr):
            # Picker colours have not been defined yet
            curses.start_color()
            curses.use_default_colors()

            # Define color pairs that the form expects
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Section titles
            curses.init_pair(
                3, curses.COLOR_BLACK, curses.COLOR_YELLOW
            )  # Editing field background
            curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)  # Discard button
            curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Save button
            curses.init_pair(
                9, curses.COLOR_BLACK, curses.COLOR_WHITE
            )  # Current field highlight

            # Run the form
            from aria2tui.ui.aria2tui_form import FormApp

            app = FormApp(stdscr, form_data)
            return app.run()

        result, saved = curses.wrapper(form_wrapper)

        # Restart curses and clear screen
        new_stdscr = start_curses()
        new_stdscr.clear()
        new_stdscr.refresh()

        # Only create config file if user clicked Save button
        if not saved:
            logger.info("User cancelled or discarded config setup")
            return False, new_stdscr

        # Create config file from form data
        create_config_from_form(result)
        logger.info("Config file created successfully")

        # Reload modules to pick up new config values
        import aria2tui.utils.aria2c._lambdas
        import aria2tui.ui.aria2tui_menu_options

        importlib.reload(aria2tui.utils.aria2c._lambdas)
        importlib.reload(aria2tui.ui.aria2tui_menu_options)

        import aria2tui.utils.aria2c_utils

        importlib.reload(aria2tui.utils.aria2c_utils)

        logger.info("Reloaded config modules with new config values")

        # Small delay to ensure file is written to disk before aria2 connection check
        time.sleep(0.2)

        return True, new_stdscr

    except Exception as e:
        logger.exception("Error during config setup: %s", e)
        # Restart curses even on error
        new_stdscr = start_curses()
        # Clear screen even on error
        new_stdscr.clear()
        new_stdscr.refresh()
        return False, new_stdscr


def handleAriaStartPromt(stdscr):
    """
    Handles the aria2c startup prompt when a connection cannot be established.

    Displays a prompt to the user asking if they want to start aria2c. If "Yes" then we
    attempt to start aria2c using the startup_commands as defined in the user's config file.

    Args:
        stdscr: The curses window object used for UI rendering.
    """
    logger.info("handleAriaStartPromt() called")
    ## Check if aria is running
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.bkgd(" ", curses.color_pair(2))  # Apply background color
    stdscr.refresh()
    config = get_config()

    colour_theme_number = config["appearance"]["theme"]

    header, choices = (
        ["Aria2c Connection Down. Do you want to start it?"],
        ["Yes", "No", "Edit Aria2TUI Config"],
    )
    connect_data = {
        "items": choices,
        "title": "Aria2TUI",
        "header": header,
        "max_selected": 1,
        "colour_theme_number": colour_theme_number,
        "number_columns": False,
    }
    ConnectionPicker = Picker(stdscr, **connect_data)
    ConnectionPicker.splash_screen("Testing Aria2 Connection")

    def connectionPrompt():
        choice, opts, function_data = ConnectionPicker.run()

        if choice == [1] or choice == []:
            close_curses(stdscr)
            logger.info("User chose not to start aria2c; exiting")
            exit()
        elif choice == [2]:
            editAria2TUIConfig()
            stdscr.clear()
            return None

        config = get_config()
        ConnectionPicker.splash_screen("Starting Aria2c Now...")

        for cmd in config["general"]["startup_commands"]:
            logger.info("Starting aria2c with command: %s", cmd)
            subprocess.Popen(
                cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )

        time.sleep(0.2)

    while True:
        connection_up = testConnection()
        can_connect = testAriaConnection()
        logger.info(
            "Connection check: connection_up=%s can_connect=%s",
            connection_up,
            can_connect,
        )
        if not can_connect:
            if not connection_up:
                connectionPrompt()
            else:
                ConnectionPicker.splash_screen(
                    [
                        "The connection is up but unresponsive...",
                        "Is your token correct in your aria2tui.toml?",
                    ]
                )
                stdscr.timeout(3500)
                stdscr.getch()
                logger.info("Connection up but unresponsive")
                connectionPrompt()
        else:
            break


def aria2tui() -> None:
    """
    The main entry point for the Aria2TUI application.

    Handles starting the TUI, managing downloads via command-line arguments, and interacting
    with the user if the aria2c daemon is not running.

    Depending on invocation, this function operates in two modes:
    1. Download Addition Mode: If run with `--add_download` or `--add_download_bg` and a URI,
       it attempts to add the download directly. If the aria2c daemon is not running,
       it may prompt the user to start it, and uses either a GUI prompt (via Tkinter) or
       a TUI prompt (via curses) depending on the command-line flag.
       Notifications are sent to the user's desktop regarding success or failure.
    2. TUI Mode: If run without download-specific arguments, the curses-based
       Aria2TUI UI is started for interactive use, prompting the user to start
       aria2c if necessary, and then launching the main application interface.

    Returns:
        None
    """

    debug = False
    if "--debug" in sys.argv:
        debug = True
        sys.argv.remove("--debug")

    configure_logging(debug=debug)
    logger.info("aria2tui() called with argv=%s (debug=%s)", sys.argv, debug)

    if len(sys.argv) == 3 and sys.argv[1].startswith("--add_download"):
        connection_up = testConnection()
        if not connection_up and sys.argv[1] == "--add_download_bg":
            exit_ = False
            try:
                import tkinter as tk
                from tkinter import messagebox

                # No main window
                root = tk.Tk()
                root.withdraw()

                response = messagebox.askyesno(
                    "Aria2TUI", "Aria2c connection failed. Start daemon?"
                )

                if not response:
                    exit_ = True
                else:
                    # Attempt to start aria2c
                    config = get_config()
                    for cmd in config["general"]["startup_commands"]:
                        subprocess.run(
                            cmd,
                            shell=True,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                        )
                    time.sleep(0.1)

            except Exception as e:
                logger.exception("Error in --add_download_bg flow: %s", e)
                message = "Problem encountered. Download not added."
                os.system(f"notify-send '{message}'")
                sys.exit()
            finally:
                if exit_:
                    message = "Exiting. Download not added."
                    os.system(f"notify-send '{message}'")
                    sys.exit()

                connection_up = testConnection()
                if not connection_up:
                    message = "Problem encountered. Check your aria2tui config. Download not added."
                    os.system(f"notify-send '{message}'")
                    exit()
        elif not connection_up:
            stdscr = start_curses()
            handleAriaStartPromt(stdscr)
            close_curses(stdscr)

        uri = sys.argv[2]
        dl_type = classify_download_string(sys.argv[2])
        if dl_type in ["Magnet", "Metalink", "FTP", "HTTP"]:
            return_val, gid = addDownload(uri)
        elif dl_type == "Torrent File":
            try:
                js_req = addTorrent(uri)
                sendReq(js_req)
                message = "Torrent added successfully."
            except Exception as e:
                logger.exception("Error adding torrent file '%s': %s", uri, e)
                message = "Error adding download."
            finally:
                os.system(f"notify-send '{message}'")
                sys.exit(1)
        else:
            try:
                message = "Error adding download."
                os.system(f"notify-send '{message}'")
            except Exception as e:
                logger.exception(
                    "Error sending notification for failed download: %s", e
                )
            finally:
                sys.exit(1)

        if return_val:
            message = f"Success! download added: gid={gid}."
        else:
            message = "Error adding download."
        print(message)
        try:
            if sys.argv[1] == "--add_download_bg":
                os.system(f"notify-send '{message}'")
        except:
            pass
        return None

    ## Run curses
    logger.info("Starting curses UI")
    stdscr = start_curses()

    ## Check for config file and create it if it doesn't exist
    config_success, stdscr = handleConfigSetup(stdscr)
    if not config_success:
        logger.info("Config setup cancelled, exiting")
        close_curses(stdscr)
        return

    ## Check if aria is running and prompt the user to start it if not
    handleAriaStartPromt(stdscr)

    # Create picker states dynamically based on instances in config
    picker_states = []

    instance_count = config_manager.get_instance_count()
    logger.info(f"Creating {instance_count} picker state(s) from config")

    for i in range(instance_count):
        instance_name = config_manager.get_instance_name(i)

        # Create a closure to capture the instance index
        def make_startup(instance_index):
            def startup_function(
                items, header, visible_rows_indices, getting_data, function_data
            ):
                name = config_manager.get_instance_name(instance_index)
                logger.info(f"Switching to instance: {name}")
                config_manager.switch_instance(instance_index)

            return startup_function

        state = DynamicPickerState(
            path=f"aria2://instance-{i}",
            display_name=instance_name,
            refresh_function=downloads_data["refresh_function"],
            auto_refresh=downloads_data.get("auto_refresh", False),
            refresh_timer=downloads_data.get("timer", 2.0),
            startup_function=make_startup(i),
        )
        picker_states.append(state)
        logger.info(f"Created picker state for instance: {instance_name}")

    # Add picker states to downloads_data
    downloads_data["loaded_picker_states"] = picker_states
    downloads_data["picker_state_index"] = 0

    app = Aria2TUI(
        stdscr,
        download_options,
        menu_options,
        menu_data,
        downloads_data,
        dl_operations_data,
        debug=debug,
    )
    logger.info("Starting Aria2TUI.run() loop")
    app.run()
    # begin(stdscr)

    ## Clean up curses and clear terminal
    logger.info("TUI run complete, cleaning up curses")
    stdscr.clear()
    stdscr.refresh()
    close_curses(stdscr)
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    aria2tui()
