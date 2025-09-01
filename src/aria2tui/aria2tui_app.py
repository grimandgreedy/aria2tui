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

os.chdir(os.path.dirname(os.path.realpath(__file__)))
# os.chdir("../..")
# sys.path.append(os.path.expanduser("../../"))
sys.path.append(os.path.expanduser("../"))

from listpick.listpick_app import *
from listpick.listpick_app import Picker, start_curses, close_curses, restrict_curses, unrestrict_curses

from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from aria2tui.ui.aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from aria2tui.ui.aria2tui_keys import download_option_keys
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid
from aria2tui.ui.aria2tui_menu_options import menu_options, download_options, Option, menu_data, downloads_data, dl_operations_data


class Aria2TUI:
    def __init__(
        self,
        stdscr: curses.window,
        download_options: list[Option],
        menu_options: list[Option],
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
        self.add_graph_to_options()
        self.add_require_option_to_dl_operations()


    def add_require_option_to_dl_operations(self) -> None:
        self.dl_operations_data["require_option"] =  [False if option.name != "Change Position" else True for option in self.download_options]
        self.dl_operations_data["option_functions"] = [None if option.name != "Change Position" else lambda stdscr, refresh_screen_function=None: default_option_selector(stdscr, field_prefix=" Download Position: ", refresh_screen_function=refresh_screen_function) for option in self.download_options]

    def add_graph_to_options(self) -> None:
        """ Add the transmission speed graphs to the menu options. """
        self.download_options.append(
            Option("Transfer Speed Graph", graph_speeds_gid, {
                "stdscr": self.stdscr,
                "get_data_function": lambda gid: sendReq(tellStatus(gid)),

                "graph_wh" : lambda: (
                    9*os.get_terminal_size()[0]//10,
                    9*os.get_terminal_size()[1]//10,
                ),
                "timeout": 1000,

                "xposf" : lambda: os.get_terminal_size()[0]//20,
                "yposf" : lambda: os.get_terminal_size()[1]//20,
                "title": "Download Transfer Speeds",
            }),
        )
        options_names = [[option.name] for option in self.download_options]
        self.dl_operations_data["items"] = options_names

        self.menu_options.append(
            Option("Transfer Speed Graph (Global)", graph_speeds, {
                "stdscr": self.stdscr,
                "get_data_function": lambda: sendReq(getGlobalStat()),
                "graph_wh" : lambda: (
                    9*os.get_terminal_size()[0]//10,
                    9*os.get_terminal_size()[1]//10,
                ),
                "xposf" : lambda: os.get_terminal_size()[0]//20,
                "yposf" : lambda: os.get_terminal_size()[1]//20,
                "title": "Global Transfer Speeds",
            }),
        )
        # self.menu_data["items"] = [[menu_option.name] for menu_option in self.menu_options],
        menu_names = [[option.name] for option in self.menu_options]
        self.menu_data["items"] = menu_names
        # MenuPicker.set_function_data(self.menu_data)

    def check_and_refresh_terminal_options(self, menu_option: Option, stdscr: curses.window):
        if "refresh_terminal_options" in menu_option.meta_args and menu_option.meta_args["refresh_terminal_options"]:
            restrict_curses(stdscr)
            unrestrict_curses(stdscr)
            

    def run(self) -> None:
        """ Run Aria2TUI app loop. """
        DownloadsPicker = Picker(self.stdscr, **self.downloads_data)
        DownloadsPicker.load_input_history("~/.config/aria2tui/cmdhist.json")
        MenuPicker = Picker(self.stdscr, **self.menu_data)
        DownloadOperationPicker = Picker(self.stdscr, **self.dl_operations_data)
        while True:
            ## SELECT DOWNLOADS
            selected_downloads, opts, self.downloads_data = DownloadsPicker.run()
            # When going back to the Downloads picker after selecting a download it shouldn't wait to get new data before displaying the picker
            DownloadsPicker.get_data_startup = False

            if selected_downloads:

                items, header = self.downloads_data["items"], self.downloads_data["header"]
                gid_index, fname_index = header.index("GID"), header.index("Name")
                gids = [item[gid_index] for i, item in enumerate(items) if i in selected_downloads]
                fnames = [item[fname_index] for i, item in enumerate(items) if i in selected_downloads]

                # Display the download names in an infobox when selecting which operation to perform
                # self.dl_operations_data["display_infobox"] = True
                # self.dl_operations_data["infobox_items"] = [[f] for f in fnames]
                # self.dl_operations_data["infobox_title"] = f"{len(fnames)} Selected..."

                # Display the download names in a right pane
                self.dl_operations_data["right_panes"] = [
                    {
                        "proportion": 2/3,
                        "auto_refresh": False,
                        "get_data": lambda data, state: [],
                        "display": right_split_display_list,
                        "data": ["Selected...", fnames],
                        "refresh_time": 1.0,
                    },
                ]
                self.dl_operations_data["split_right"] = True

                ## SELECT OPERATION TO APPLY TO SELECTED DOWNLOADS
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
                    applyToDownloads(self.stdscr, gids, operation.name, operation.function, operation.function_args, user_opts, view, fnames=fnames, picker_view=picker_view)
                    self.downloads_data["selections"] = {}
                    self.dl_operations_data["user_opts"] = ""
                    self.check_and_refresh_terminal_options(operation, self.stdscr)
                else: continue

            else: 

                while True:
                    ## SELECT MENU OPTION
                    selected_menu, opts, self.menu_data = MenuPicker.run()

                    # If we exit from the menu then exit altogether
                    if not selected_menu: 
                        DownloadsPicker.save_input_history("~/.config/aria2tui/cmdhist.json")
                        close_curses(self.stdscr)
                        return 

                    menu_option = self.menu_options[selected_menu[0]]
                    if menu_option.name == "View Downloads":
                        self.downloads_data["auto_refresh"] = False
                        break
                    elif menu_option.name == "Watch Downloads":
                        self.downloads_data["auto_refresh"] = True
                        break

                    ## if it is a view operation such as "View Global Stats" then send the request and open it with nvim
                    elif "view" in menu_option.meta_args and menu_option.meta_args["view"]:
                        # Ensure that the screen is cleared after nvim closes, otherwise artifcats remain.
                        self.downloads_data["clear_on_start"] = True
                        self.menu_data["clear_on_start"] = True
                        response = sendReq(menu_option.function(**menu_option.function_args))
                        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                            tmpfile.write(json.dumps(response, indent=4))
                            tmpfile_path = tmpfile.name
                        # cmd = r"""nvim -i NONE -c 'setlocal bt=nofile' -c 'silent! %s/^\s*"function"/\0' -c 'norm ggn'""" + f" {tmpfile_path}"
                        cmd = f"nvim {tmpfile_path}"
                        process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
                        self.check_and_refresh_terminal_options(menu_option, self.stdscr)
                    elif "picker_view" in menu_option.meta_args and menu_option.meta_args["picker_view"]:
                        self.downloads_data["clear_on_start"] = True
                        self.menu_data["clear_on_start"] = True
                        response = sendReq(menu_option.function(**menu_option.function_args))
                        response = flatten_data(response)
                        resp_list = [[key, val] for key, val in response.items()]
                        config = get_config()
                        colour_theme_number=config["appearance"]["theme"]
                        x = Picker(
                            self.stdscr,
                            items = resp_list,
                            header = ["Key", "Val"],
                            title=menu_option.name,
                            colour_theme_number=colour_theme_number,
                            reset_colours=False,
                        )
                        x.run()
                    else:
                        if "display_message" in menu_option.meta_args and menu_option.meta_args["display_message"]:
                            display_message(self.stdscr, menu_option.meta_args["display_message"])
                        return_val = menu_option.function(**menu_option.function_args)
                        self.check_and_refresh_terminal_options(menu_option, self.stdscr)

                        # Add notification of success or failure to listpicker
                        if return_val not in ["", None, []]:
                            # If we have are returning gids and a status message then set the startup notification to the status message.
                            if type(return_val) == type((0,0)) and len(return_val) == 2:
                                if type(return_val[0]) == type([]) and type(return_val[1]) == type(""):
                                    DownloadsPicker.startup_notification = str(return_val[1])

                        self.stdscr.clear()
                        self.stdscr.refresh()
                        break

def display_message(stdscr: curses.window, msg: str) -> None:
    h, w = stdscr.getmaxyx()
    if (h>8 and w >20):
        stdscr.addstr(h//2, (w-len(msg))//2, msg)
        stdscr.refresh()


def handleAriaStartPromt(stdscr):
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

                for cmd in config["general"]["startupcmds"]:
                    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                time.sleep(2)
            else:
                ConnectionPicker.splash_screen(["The connection is up but unresponsive...", "Is your token correct in your aria2tui.toml?"])
                stdscr.timeout(5000)
                stdscr.getch()
                exit()
        else:
            break


def aria2tui() -> None:
    """ Main function """

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
    # global menu_options, download_options, menu_data, downloads_data, dl_operations_data
    aria2tui()
