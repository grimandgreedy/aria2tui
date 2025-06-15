#!/bin/python
from subprocess import run
from urllib import request as rq
import urllib
import copy
import json
import os
import sys

sys.path.append(os.path.expanduser("~/scripts/utils/list_picker/"))

from list_picker import *
from list_picker_colours import get_colours, help_colours
from table_to_list_of_lists import *
from options_selectors import default_option_selector
import time
from time import sleep
import curses
from aria2c_wrapper import *
import tempfile
import toml
from utils import *
from aria2c_utils import *
from aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from collections.abc import Callable
from keys import menu_keys
from aria2tui_keys import download_option_keys

def begin(stdscr : curses.window, config: dict) -> None:
    """ Initialise data and start application. """

    url = config["general"]["url"]
    port = config["general"]["port"]
    token = config["general"]["token"]
    paginate = config["general"]["paginate"]

    custom_colours = get_colours(config["appearance"]["theme"])

    # ["NAME", function, functionargs, extra]
    download_options = [
        ["pause", pause, {}, {}],
        ["unpause", unpause, {}, {}],
        ["change options", changeOptionDialog, {}, {}],
        ["changePosition", changePosition, {}, {}],
        ["sendToFrontOfQueue", changePosition, {"pos":0} , {}],
        ["sendToBackOfQueue", changePosition, {"pos":10000}, {}],
        ["retryDownload", retryDownload, {}, {}],
        ["Remove Paused", remove, {}, {}],
        # ["forceRemove", forceRemove, {}, {}],
        # ["removeStopped", removeDownloadResult, {}, {}],
        ["Remove Errored", removeDownloadResult, {}, {}],
        ["getFiles", getFiles, {}, {"view":True}],
        ["getServers", getServers, {}, {"view":True}],
        ["getPeers", getPeers, {}, {"view":True}],
        ["getUris", getUris, {}, {"view":True}],
        ["tellStatus", tellStatus, {}, {"view":True}],
        ["getOption", getOption, {}, {"view":True}],
        ["getAllInfo", getAllInfo, {}, {"view":True}],
        # ["changeOption", changeOption, {}, {"view":True}],
        ["openDownloadLocation (new window)", openDownloadLocation, {}, {}],
        ["openDownloadLocation", lambda gid: openDownloadLocation(gid, new_window=False), {}, {}],
        ["Open File(s)", openGidFiles, {}, {}],
        ["Open File(s) (do not group)", lambda gids: openGidFiles(gids, group=False), {}, {}],
    ]
    menu_options = [
        ["Watch Downloads", None,{},{}],
        ["View Downloads", None,{},{}],
        ["Add URIs", addUris,{},{}],
        ["Add Torrents", addTorrents,{},{}],
        ["Pause All", pauseAll,{},{}],
        ["Remove completed/errored downloads", removeCompleted,{},{}],
        ["Get Global Options", getGlobalOption,{},{"view": True}],
        ["Get Global Stat", getGlobalStat,{},{"view": True}],
        ["Get Session Info", getSessionInfo,{},{"view": True}],
        ["Get Version", getVersion,{},{"view": True}],
        ["Edit Config", editConfig,{},{}],
        ["Restart Aria", restartAria,{},{"display_message": "Restarting Aria2c..." }],
    ]
    appLoop(stdscr, config, highlights, menu_highlights, custom_colours, modes, download_options, menu_options, paginate)

def appLoop(stdscr: curses.window, config: dict, highlights: list[dict], menu_highlights: list[dict], custom_colours: dict, modes: list[dict], download_options: list[list], menu_options: list[list], paginate: bool =False) -> None:
    """ Main app loop for aria2tui. """
    app_name = "Aria2TUI"
    menu_data = {
        "top_gap": 0,
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colours": custom_colours,
        "max_selected": 1,
        "items": [menu_option[0] for menu_option in menu_options],
        "header": ["Main Menu"],
        "centre_in_terminal": True,
        "centre_in_cols": False,
        "paginate": paginate,
        "centre_in_terminal_vertical": True,
        "hidden_columns": [],
        "keys_dict": menu_keys,
        "show_footer": False,
    }
    downloads_data = {
        "top_gap": 0,
        "highlights": highlights,
        "paginate": paginate,
        "modes": modes,
        "display_modes": True,
        "title": app_name,
        "colours": custom_colours,
        "refresh_function": getAll,
        "columns_sort_method": [0, 1, 1, 7, 7, 1, 7, 5, 1, 1, 0],
        "sort_reverse": [False, False, False, True, True, True, True, True, False, False, False],
        "auto_refresh": True,
        "get_new_data": True,
        "get_data_startup": True,
        "timer": 1,
        "paginate": paginate,
        "hidden_columns": [],
        "id_column": 10,
        "centre_in_terminal_vertical": False,
    }
    dl_operations_data = {
        "top_gap": 0,
        "highlights": operations_highlights,
        "paginate": paginate,
        "title": app_name,
        "colours": custom_colours,
        "require_option": [False if x[0] != "changePosition" else True for x in download_options],
        "option_functions": [None if x[0] != "changePosition" else lambda stdscr, refresh_screen_function: default_option_selector(stdscr, field_name="Download Position") for x in download_options],
        "header": [f"Select operation"],
        "paginate": paginate,
        "hidden_columns": [],
        "keys_dict": download_option_keys,
    }
    while True:
        downloads_data = {key: val for key, val in downloads_data.items() if key not in ["items", "indexed_items"]}
        ## SELECT DOWNLOADS
        selected_downloads, opts, downloads_data = list_picker(
            stdscr,
            **downloads_data,
        )

        if selected_downloads:
            operations = [x[0] for x in download_options]
            operation_functions = [x[1] for x in download_options]
            dl_operations_data = {key: val for key, val in dl_operations_data.items() if key not in ["items", "indexed_items"]}
            header = downloads_data["header"]
            items = downloads_data["items"]
            gid_index = header.index("gid")
            fname_index = header.index("fname")
            gids = [item[gid_index] for i, item in enumerate(items) if i in selected_downloads]
            fnames = [item[fname_index] for i, item in enumerate(items) if i in selected_downloads]

            dl_operations_data["display_infobox"] = True
            dl_operations_data["infobox_items"] = fnames

            ## SELECT DOWNLOAD OPTION
            selected_operation, opts, dl_operations_data = list_picker(
                stdscr,
                items=operations,
                **dl_operations_data,
            )
            if selected_operation:
                operation_name, operation_function = operations[selected_operation[0]], operation_functions[selected_operation[0]]
                user_opts = dl_operations_data["user_opts"]
                view = False
                operation_list = download_options[selected_operation[0]]
                ## e.g., operation_list = ["getFiles", getFiles, {}, {"view":True}]
                if len(operation_list) > 2 and "view" in operation_list[-1] and operation_list[-1]["view"]: view=True
                applyToDownloads(stdscr, gids, operation_name, operation_function, user_opts, view)
                downloads_data["selections"] = {}
                dl_operations_data["user_opts"] = ""
            else: continue
        else: 
            ## SELECT MENU OPTION
            selected_menu, opts, menu_data = list_picker(
                stdscr,
                **menu_data,
            )
            ## If we exit from the menu then exit altogether
            if not selected_menu: break
            ##
            name, func, kwargs, extra = menu_options[selected_menu[0]]
            if name == "View Downloads":
                downloads_data["auto_refresh"] = False
                continue
            elif name == "Watch Downloads":
                downloads_data["auto_refresh"] = True
                continue

            ## if it is a view operation such as "View Global Stats" then send the request and open it with nvim
            elif "view" in extra and extra["view"]:
                response = sendReq(func(**kwargs))
                with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                    tmpfile.write(json.dumps(response, indent=4))
                    tmpfile_path = tmpfile.name
                cmd = f"nvim -i NONE {tmpfile_path}"
                process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
                # stdscr.curs_set(False)
            else:
                if "display_message" in extra and extra["display_message"]:
                    h, w = stdscr.getmaxyx()
                    if (h>8 and w >20):
                        stdscr.addstr(h//2, (w-len(extra["display_message"]))//2, extra["display_message"])
                        stdscr.refresh()

                return_val = func(**kwargs)
                # Add notification of success or failure to listpicker
                if return_val not in ["", None]:
                    downloads_data["startup_notification"] = return_val


def main() -> None:
    """ Main function """
    ## Load config
    CONFIGPATH = "~/scripts/utils/aria2tui/aria2tui.toml"
    with open(os.path.expanduser(CONFIGPATH), "r") as f:
        config = toml.load(f)

    custom_colours = get_colours(config["appearance"]["theme"])

    ## Run curses
    stdscr = curses.initscr()
    stdscr.keypad(True)
    curses.start_color()
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)

    ## Check if aria is running
    connection_up = testConnection()
    if not connection_up:
        header, choices = ["Aria2c Connection Down. Do you want to start it?"], ["Yes", "No"]
        choice, opts, function_data = list_picker(
            stdscr,
            choices,
            colours=custom_colours,
            title="Aria2TUI",
            header=header,
            max_selected=1
        )

        if choice == [1] or choice == []: exit()
        h, w = stdscr.getmaxyx()
        if (h>8 and w >20):
            stdscr.addstr(h//2, (w-len("Starting Aria2c Now"))//2, "Starting Aria2c Now")
            stdscr.refresh()

        for cmd in config["general"]["startupcmds"]:
            subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

        time.sleep(2)

    begin(stdscr, config=config)

    ## Clean up curses and clear terminal
    stdscr.clear()
    stdscr.refresh()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
