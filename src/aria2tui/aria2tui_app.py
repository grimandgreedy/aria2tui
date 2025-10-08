#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2tui_app.py

Author: GrimAndGreedy
License: MIT
"""

import os
import sys
from sys import exit
import tempfile
import time
import toml
import json
import curses

from listpick.listpick_app import *
from listpick.listpick_app import Picker, start_curses, close_curses, restrict_curses, unrestrict_curses

from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from aria2tui.ui.aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from aria2tui.ui.aria2tui_keys import download_option_keys
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid
from aria2tui.ui.aria2tui_menu_options import menu_options, download_options, menu_data, downloads_data, dl_operations_data


class Aria2TUI:
    def __init__(
        self,
        stdscr: curses.window,
        download_options: list[Operation],
        menu_options: list[Operation],
        menu_data: dict,
        downloads_data: dict,
        dl_operations_data: dict,
    ):
        self.stdscr = stdscr
        self.download_options = download_options
        self.menu_options = menu_options
        self.menu_data = menu_data
        self.downloads_data = downloads_data
        self.dl_operations_data = dl_operations_data
        self.add_require_option_to_dl_operations()


    def add_require_option_to_dl_operations(self) -> None:
        self.dl_operations_data["require_option"] =  [False if option.name != "Change Position" else True for option in self.download_options]
        self.dl_operations_data["option_functions"] = [None if option.name != "Change Position" else lambda stdscr, refresh_screen_function=None: default_option_selector(stdscr, field_prefix=" Download Position: ", refresh_screen_function=refresh_screen_function) for option in self.download_options]

    def check_and_reapply_terminal_settings(self, menu_option: Operation, stdscr: curses.window):
        if menu_option.reapply_terminal_settings:
            restrict_curses(stdscr)
            unrestrict_curses(stdscr)
            

    def run(self) -> None:
        """ 
        Run Aria2TUI app loop.
        """

        # Create the main menu, downloads, and operations Picker objects
        DownloadsPicker = Picker(self.stdscr, **self.downloads_data)
        DownloadsPicker.load_input_history("~/.config/aria2tui/cmdhist.json")
        MenuPicker = Picker(self.stdscr, **self.menu_data)
        DownloadOperationPicker = Picker(self.stdscr, **self.dl_operations_data)


        while True:

            ## DISPLAY DOWNLOADS
            selected_downloads, opts, self.downloads_data = DownloadsPicker.run()

            # When going back to the Downloads picker after selecting a download it shouldn't wait to get new data before displaying the picker
            DownloadsPicker.get_data_startup = False

            if selected_downloads:
                ## CHOOSE OPERATION TO APPLY TO SELECTED DOWNLOADS
                items, header = self.downloads_data["items"], self.downloads_data["header"]
                gid_index, fname_index = header.index("GID"), header.index("Name")
                gids = [item[gid_index] for i, item in enumerate(items) if i in selected_downloads]
                fnames = [item[fname_index] for i, item in enumerate(items) if i in selected_downloads]

                # Display the download names in a right pane
                self.dl_operations_data["right_panes"] = [
                    {
                        "proportion": 1/3,
                        "auto_refresh": False,
                        "get_data": lambda data, state: [],
                        "display": right_split_display_list,
                        "data": ["Selected...", fnames],
                        "refresh_time": 1.0,
                    },
                ]
                self.dl_operations_data["split_right"] = True

                DownloadOperationPicker.set_function_data(self.dl_operations_data)
                selected_operation, opts, self.dl_operations_data = DownloadOperationPicker.run()
                if selected_operation:
                    operation = download_options[selected_operation[0]]

                    user_opts = self.dl_operations_data["user_opts"]
                    view = False
                    if operation.meta_args and "view" in operation.meta_args and operation.meta_args["view"]: view=True
                    picker_view = False
                    if operation.meta_args and "picker_view" in operation.meta_args and operation.meta_args["picker_view"]: picker_view=True


                    ## APPLY THE SELECTED OPERATION TO THE SELECTED DOWNLOADS
                    applyToDownloads(
                        self.stdscr,
                        operation,
                        gids,
                        operation.name,
                        operation.function,
                        operation.function_args,
                        user_opts,
                        view,
                        fnames=fnames,
                        picker_view=picker_view
                    )

                    self.downloads_data["selections"] = {}
                    self.dl_operations_data["user_opts"] = ""
                    self.check_and_reapply_terminal_settings(operation, self.stdscr)
                else: continue

            else: 

                ## If we have not selected any downloads, then we have exited the downloads picker
                ## DISPLAY MAIN MENU
                while True:
                    selected_menu, opts, self.menu_data = MenuPicker.run()

                    # If we exit from the menu then exit altogether
                    if not selected_menu: 
                        DownloadsPicker.save_input_history("~/.config/aria2tui/cmdhist.json")
                        close_curses(self.stdscr)
                        return 

                    menu_option = self.menu_options[selected_menu[0]]
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
                        function_args=menu_option.function_args
                    )
                    if menu_option.send_request:
                        result = sendReq(result)
                    ## if it is a view operation such as "View Global Stats" then send the request and open it with nvim
                    if menu_option.view:
                        # Ensure that the screen is cleared after nvim closes, otherwise artifcats remain.
                        DownloadsPicker.clear_on_start = True
                        MenuPicker.clear_on_start = True
                        # response = sendReq(menu_option.function(**menu_option.function_args))
                        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                            tmpfile.write(json.dumps(result, indent=4))
                            tmpfile_path = tmpfile.name
                        # cmd = r"""nvim -i NONE -c 'setlocal bt=nofile' -c 'silent! %s/^\s*"function"/\0' -c 'norm ggn'""" + f" {tmpfile_path}"
                        cmd = f"nvim {tmpfile_path}"
                        process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
                        self.check_and_reapply_terminal_settings(menu_option, self.stdscr)

                    ## If it is a picker view operation then send the request and display it in a Picker
                    elif menu_option.picker_view:
                        DownloadsPicker.clear_on_start = True
                        MenuPicker.clear_on_start = True

                        result = flatten_data(result)
                        resp_list = [[key, val] for key, val in result.items()]
                        config = get_config()
                        colour_theme_number=config["appearance"]["theme"]
                        x = Picker(
                            self.stdscr,
                            items = resp_list,
                            header = ["Key", "Val"],
                            title=menu_option.name,
                            colour_theme_number=colour_theme_number,
                            reset_colours=False,
                            cell_cursor=False,
                        )
                        x.run()

                    
                    else:
                        if "display_message" in menu_option.meta_args and menu_option.meta_args["display_message"]:
                            display_message(self.stdscr, menu_option.meta_args["display_message"])
                        self.check_and_reapply_terminal_settings(menu_option, self.stdscr)

                        # Add notification of success or failure to listpicker
                        if result not in ["", None, []]:
                            # If we have are returning gids and a status message then set the startup notification to the status message.
                            if type(result) == type((0,0)) and len(result) == 2:
                                if type(result[0]) == type([]) and type(result[1]) == type(""):
                                    DownloadsPicker.startup_notification = str(result[1])

                        self.stdscr.clear()
                        self.stdscr.refresh()
                        break

def display_message(stdscr: curses.window, msg: str) -> None:
    """ Display a given message using curses. """
    h, w = stdscr.getmaxyx()
    if (h>8 and w >20):
        stdscr.addstr(h//2, (w-len(msg))//2, msg)
        stdscr.refresh()


def handleAriaStartPromt(stdscr):
    """
    Handles the aria2c startup prompt when a connection cannot be established. 

    Displays a prompt to the user asking if they want to start aria2c. If "Yes" then we
    attempt to start aria2c using the startup_commands as defined in the user's config file.

    Args:
        stdscr: The curses window object used for UI rendering.
    """
    ## Check if aria is running
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(2))  # Apply background color
    stdscr.refresh()
    config = get_config()

    colour_theme_number=config["appearance"]["theme"]

    header, choices = ["Aria2c Connection Down. Do you want to start it?"], ["Yes", "No"]
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

    while True:
        connection_up = testConnection()
        can_connect = testAriaConnection()
        if not can_connect:
            if not connection_up:

                choice, opts, function_data = ConnectionPicker.run()

                if choice == [1] or choice == []:
                    close_curses(stdscr)
                    exit()

                config = get_config()
                ConnectionPicker.splash_screen("Starting Aria2c Now...")

                for cmd in config["general"]["startup_commands"]:
                    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                time.sleep(0.2)
            else:
                ConnectionPicker.splash_screen(["The connection is up but unresponsive...", "Is your token correct in your aria2tui.toml?"])
                stdscr.timeout(5000)
                stdscr.getch()
                exit()
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

                response = messagebox.askyesno("Aria2TUI", "Aria2c connection failed. Start daemon?")

                if not response:
                    exit_ = True
                else:
                    # Attempt to start aria2c
                    config = get_config()
                    for cmd in config["general"]["startup_commands"]:
                        subprocess.run(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                    time.sleep(0.1)

            except Exception as e:
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
            except:
                message = "Error adding download."
            finally:
                os.system(f"notify-send '{message}'")
                sys.exit(1)
        else:
            try:
                message = "Error adding download."
                os.system(f"notify-send '{message}'")
            except:
                pass
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
    stdscr = start_curses()

    ## Check if aria is running and prompt the user to start it if not
    handleAriaStartPromt(stdscr)

    app = Aria2TUI(
        stdscr, 
        download_options,
        menu_options,
        menu_data,
        downloads_data,
        dl_operations_data,
    )
    app.run()
    # begin(stdscr)

    ## Clean up curses and clear terminal
    stdscr.clear()
    stdscr.refresh()
    close_curses(stdscr)
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    aria2tui()
