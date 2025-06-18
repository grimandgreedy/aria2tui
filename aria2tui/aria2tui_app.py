#!/bin/python

import os
import sys
import tempfile
import time
import toml
import json
import curses

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.expanduser("../../list_picker/"))

from list_picker.ui.list_picker_colours import get_colours, get_help_colours, get_notification_colours
from list_picker.utils.options_selectors import default_option_input, output_file_option_selector
from list_picker.utils.table_to_list_of_lists import *
from list_picker.utils.utils import *
from list_picker.utils.sorting import *
from list_picker.utils.filtering import *
from list_picker.ui.input_field import *
from list_picker.utils.clipboard_operations import *
from list_picker.utils.searching import search
from list_picker.ui.help_screen import help_lines
from list_picker.ui.keys import list_picker_keys, notification_keys, options_keys, menu_keys
from list_picker.utils.generate_data import generate_list_picker_data
from list_picker.utils.dump import dump_state, load_state, dump_data
from list_picker.list_picker_app import Picker, start_curses, close_curses

from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from aria2tui.ui.aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from aria2tui.ui.aria2tui_keys import download_option_keys
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid


def begin(stdscr : curses.window) -> None:
    """ Initialise data and start application. """


    # ["NAME", function, functionargs, extra]
    download_options = [
        ["pause", pause, {}, {}],
        ["unpause", unpause, {}, {}],
        ["change options (single)", changeOptionDialog, {}, {}],
        ["change options (batch)", changeOptionBatchDialog, {}, {}],
        ["changePosition", changePosition, {}, {}],
        ["sendToFrontOfQueue", changePosition, {"pos":0} , {}],
        ["sendToBackOfQueue", changePosition, {"pos":10000}, {}],
        ["retryDownload", retryDownload, {}, {}],
        ["retryDownloadAndPause", retryDownloadAndPause, {}, {}],
        ["Remove (paused/active)", remove, {}, {}],
        # ["forceRemove", forceRemove, {}, {}],
        # ["removeStopped", removeDownloadResult, {}, {}],
        ["Remove (errored)", removeDownloadResult, {}, {}],
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

        ["Transfer Speed Graph *experimental*", graph_speeds_gid,{
            "stdscr":stdscr,
            "get_data_function": lambda gid: sendReq(tellStatus(gid)),

            "graph_wh" : lambda: (
                9*os.get_terminal_size()[0]//10,
                9*os.get_terminal_size()[1]//10,
            ),
            "timeout": 1000,

            "xposf" : lambda: os.get_terminal_size()[0]//20,
            "yposf" : lambda: os.get_terminal_size()[1]//20,
            "title": "Download Transfer Speeds",
        },{}],
    ]
    menu_options = [
        ["Watch Downloads", None,{},{}],
        ["View Downloads", None,{},{}],
        ["Add URIs", addUris,{},{}],
        ["Add URIs and immediately pause", addUrisAndPause,{},{}],
        ["Add Torrents and magnet links", addTorrents,{},{}],
        ["Transfer Speed Graph *experimental*", graph_speeds,{
            "stdscr":stdscr,
            "get_data_function": lambda: sendReq(getGlobalStat()),

            "graph_wh" : lambda: (
                9*os.get_terminal_size()[0]//10,
                9*os.get_terminal_size()[1]//10,
            ),

            "xposf" : lambda: os.get_terminal_size()[0]//20,
            "yposf" : lambda: os.get_terminal_size()[1]//20,
            "title": "Global Transfer Speeds",
        },{}],
        # ["Pause All", pauseAll,{},{}],
        # ["Force Pause All", forcePauseAll,{},{}],
        # ["Remove completed/errored downloads", removeCompleted,{},{}],
        ["Get Global Options", getGlobalOption,{},{"view": True}],
        ["Get Global Stat", getGlobalStat,{},{"view": True}],
        ["Get Session Info", getSessionInfo,{},{"view": True}],
        ["Get Version", getVersion,{},{"view": True}],
        ["Edit Config", editConfig,{},{}],
        ["Restart Aria", restartAria,{},{"display_message": "Restarting Aria2c..." }],
    ]
    appLoop(stdscr, highlights, menu_highlights, modes, download_options, menu_options)

def appLoop(
        stdscr: curses.window,
        highlights: list[dict],
        menu_highlights: list[dict],
        modes: list[dict],
        download_options: list[list],
        menu_options: list[list],
    ) -> None:

    """ Main app loop for aria2tui. """

    config = get_config()
    paginate = config["general"]["paginate"]

    colour_theme_number=config["appearance"]["theme"]

    app_name = "Aria2TUI"
    menu_data = {
        "top_gap": 0,
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colour_theme_number": colour_theme_number,
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
        "colour_theme_number": colour_theme_number,
        "refresh_function": getAll,
        "columns_sort_method": [0, 1, 1, 7, 7, 1, 7, 5, 1, 1, 0],
        "sort_reverse": [False, False, False, True, True, True, True, True, False, False, False],
        "auto_refresh": True,
        "get_new_data": True,
        "get_data_startup": True,
        "timer": 2,
        "paginate": paginate,
        "hidden_columns": [],
        "id_column": 10,
        "centre_in_terminal_vertical": False,
        "footer_string_auto_refresh": True,
        "footer_string_refresh_function": getGlobalSpeed,
        "footer_timer": 1,
    }
    dl_operations_data = {
        "top_gap": 0,
        "highlights": operations_highlights,
        "paginate": paginate,
        "title": app_name,
        "colour_theme_number": colour_theme_number,
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
        DownloadsPicker = Picker(stdscr, **downloads_data)
        selected_downloads, opts, downloads_data = DownloadsPicker.run()

        if selected_downloads:
            operations = [x[0] for x in download_options]
            operation_functions = [x[1] for x in download_options]
            operation_function_args = [x[2] for x in download_options]
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
            DownloadOperationPicker = Picker(stdscr, items=operations, **dl_operations_data)
            selected_operation, opts, dl_operations_data = DownloadOperationPicker.run()
            if selected_operation:
                operation_name, operation_function = operations[selected_operation[0]], operation_functions[selected_operation[0]]
                operation_function_args = operation_function_args[selected_operation[0]]

                user_opts = dl_operations_data["user_opts"]
                view = False
                operation_list = download_options[selected_operation[0]]
                ## e.g., operation_list = ["getFiles", getFiles, {}, {"view":True}]
                if len(operation_list) > 2 and "view" in operation_list[-1] and operation_list[-1]["view"]: view=True
                applyToDownloads(stdscr, gids, operation_name, operation_function, operation_function_args, user_opts, view, fnames=fnames)
                downloads_data["selections"] = {}
                dl_operations_data["user_opts"] = ""
            else: continue
        else: 
            ## SELECT MENU OPTION
            MenuPicker = Picker(stdscr, **menu_data)
            selected_menu, opts, menu_data = MenuPicker.run()
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
                if return_val not in ["", None, []]:
                    downloads_data["startup_notification"] = str(return_val)
                    stdscr.clear()


def handleAriaStartPromt(stdscr):
    ## Check if aria is running
    curses.init_pair(1, 253, 232)
    stdscr.bkgd(' ', curses.color_pair(1))  # Apply background color
    stdscr.refresh()
    while True:
        connection_up = testConnection()
        can_connect = testAriaConnection()
        if not can_connect:
            if not connection_up:
                header, choices = ["Aria2c Connection Down. Do you want to start it?"], ["Yes", "No"]
                connect_data = {
                        "items": choices,
                        "title": "Aria2TUI",
                        "header": header,
                        "max_selected": 1,
                    }
                ConnectionPicker = Picker(stdscr, **connect_data)

                choice, opts, function_data = ConnectionPicker.run()

                if choice == [1] or choice == []: exit()

                config = get_config()

                h, w = stdscr.getmaxyx()
                if (h>8 and w >20):
                    s = "Starting Aria2c Now..."
                    stdscr.addstr(h//2-1, (w-len(s))//2, s)
                    s = f'startupcmds = {config["general"]["startupcmds"]}'
                    stdscr.addstr(h//2+1, (w-min(len(s), w))//2, s[:w])
                    stdscr.refresh()

                for cmd in config["general"]["startupcmds"]:
                    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                time.sleep(2)
            else:
                h, w = stdscr.getmaxyx()
                if (h>8 and w >20):
                    s = "The connection is up but unresponsive..."
                    stdscr.addstr(h//2, (w-len(s))//2, s)
                    s="Is your token correct in config.toml?"
                    stdscr.addstr(h//2+1, (w-len(s))//2, s)
                    stdscr.refresh()
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

    begin(stdscr)

    ## Clean up curses and clear terminal
    stdscr.clear()
    stdscr.refresh()
    close_curses(stdscr)
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    aria2tui()
