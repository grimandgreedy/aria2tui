#!/bin/python
from subprocess import run
from urllib import request as rq
import urllib
import copy
import json

from sqlalchemy.engine import cursor
from list_picker import *
from list_picker_colours import get_colours, help_colours
from table_to_list_of_lists import *
import time
import multiprocessing
import queue
import os
from time import sleep
import curses
from aria2c_wrapper import *
import tempfile
import tomllib
from utils import *
from aria2c_utils import *

r"""
todo 

 - refresh menu with a timer
 - (!!!) add retry download function by getting download data, remove it and readd it
 - info is wrong for torrents. The size, % completed, etc. Might need to rework the the data scraped from the json response.
 - remove completed not working
 - fix adding uris with filename. Data is the same but it is corrupted somehow.
    - works:        https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg
    - doesn't work: https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLBVWNXUrlGnx3VtnPULUE6v0EteQg
 - get all function
 - merge columns
 - add empty values for inapplicable cols
 - allow index
 - add a config file (~/.config/ariatui.conf) which contains the rpc url, port, secret, etc.
 - fix not resizing properly
 - Add hidden columns to function so that they remain hidden on refresh
 - Add a view all tasks option
 - Add color to highlight errored and completed tasks
 - implement proper retrydownload function 
 - allow options when adding uris; perhaps use the same structure as the aria2c input file
 - improve menu navigation
    - when downloads are selected and we go back they should still be selected
 - redo menu order
 - fix dir; it should be obtained from getInfo; 
    - E.g., 4chan downloads don't show filename or dir as dir is based on filename
 - should the colours be:
    - completed: green
    - active: blue
    - paused: ??? gray?
 - after nvim is opened (e.g., show all dl info) the display needs to be redrawn
 - fix filenames; also check torrents
 - add highlights for % complete
 - create watch all
 - make operations on downloads into a batch request
 - examine parsing of toml (why are the arguments set outside of the main function?)
 - make fetching active, queue, and stopped downloads into a batch request (all)
 - add to config
    - highlights off
    - color off
 - live setting changes
    - theme
 - make percentage bar look nicer
 - watch active only refreshes upon a keypress
 - when the item order refreshes (e.g. new downloads added) the selected items change. need to associate the selected items with gids and then create new selected items which will be passed back
 - takes us back to the top when it refreshes in a different mode (I think due to filter)
 - add pin_cursor option to prevent the cursor from going down when refreshing
 - add url to test_connection
 - specifying name doesn't work with magnet links
 - add global stats bar
 - monitor log file
 - setup https connection
 - add default sort method for columns
 - add source column, showing site from which it is being downloaded
 - When I change a download to position 4, the user_option 4 will remain in the options going forward
 - (!!!) Download position jumps around when refreshing since changing the sort methods to be column-wise
    -   might have to do with filtering; 
    -   when original sort order there is no jumping
    -   lots of jumping when sorting by size
 - open files (*)
    - open files of the same type in one instance
 - Filter/search problems
    - ^[^\s] matches all rows in help but only highlights the first col
        - seems to match the expression in any col but then only show highlights based on the row_str so misses matches in the second col
 - make remove work with errored download
 - ForceRemove doesn't seem to do anything (with stopped download)
 - retry download doesn't seem to do anything 
 - restrict refresh so that it doesn't exit on the menu
 - infobox causes flickering
 - add key to open download location using 'o'
 - remove old watch loop; pass refresh function to watch, no refresh function to view
 - show notification if adding downloads fail
 - (!!!) there is a problem with the path when readding downloads sometimes. It is correct in the download info but is displayed wrong???
 - make operations work only with certain download types:
    - make remove work with all
    - queue operations only on those in the queue
    - retry only on errored
    - 

DONE
 - If a download is paused and it is paused again it throws an error when it should just skip it.
 - implement addTorrent
 - Return a list of files and % completed for each file in a torrent.
 - check if remove completed/errored is working
 - show all downloads (not just 500)
    - set max=5000 which should be fine
    - had to set the max in the aria config file as well
 - Add a getAllInfo option for downloads
 - open location
 - figure out how to keep the row constant when going back and forth between menus
 - make fetching active, queue, and stopped downloads into a batch request
 - (!!!) high CPU usage
    - when val in `stdscr.timeout(val)` is low the cpu usage is high
 - colour problems:
    - aria2tui > view downloads > 'q' > 'z' 
    (*) fixed by arbitarily setting 0-50 for application colours, 50-100 for help colours and 100-150 for notification colours
 - have to open watch active twice; first time exits immediately...
 - add preview of selected downloads when selecting options
    (*) implemented infobox
 - artifacts after opening download location in terminal; have to refresh before and after?
    (*) stdscr.clear() after yazi closes
 - add a lambda function for add_download so that url and port don't have to be specifed



"""



# def run_with_timeout(function, args, kwargs, timeout):
#     result_queue = multiprocessing.Queue()
#
#     # Create a wrapper function to pass both positional and keyword arguments, and a result queue
#     def wrapper():
#         function(*args, result_queue=result_queue, **kwargs)
#
#     p = multiprocessing.Process(target=wrapper)
#     p.start()
#     p.join(timeout)  # Wait for `timeout` seconds or until process finishes
#
#     if p.is_alive():
#         p.terminate()  # Terminate the process if still alive after timeout
#         p.join()  # Ensure process has terminated
#         result = None
#         print("Curses application terminated due to timeout")
#     else:
#         print("Curses application completed successfully")
#         try:
#             result = result_queue.get_nowait()
#         except queue.Empty:
#             result = None
#
#     return result


def begin(config):
    active_loop = lambda x: x
    waiting_loop = lambda x: x
    stopped_loop = lambda x: x
    options = [
            [
                "View All", 
                {
                    "function": active_loop,
                    "get_data": getAll,
                    "operations": [
                        ["pause", pause],
                        ["unpause", unpause],
                        ["changePosition", changePosition],
                        ["sendToFrontOfQueue", changePosition, {"pos":0} ],
                        ["sendToBackOfQueue", changePosition, {"pos":10000} ],
                        ["remove", remove],
                        ["retryDownload", retryDownload, {}],
                        ["forceRemove", forceRemove],
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
                        ["openFile", openFile, {}, {}],
                    ],
                }
            ],
            [
                "Watch All",
                {
                    "get_data": getAll,
                    "args": (),
                    "kwargs": {},
                    "refresh": True,
                    "operations": [
                        ["pause", pause],
                        ["unpause", unpause],
                        ["changePosition", changePosition],
                        ["sendToFrontOfQueue", changePosition, {"pos":0} ],
                        ["sendToBackOfQueue", changePosition, {"pos":10000} ],
                        ["remove", remove],
                        ["retryDownload", retryDownload, {}],
                        ["forceRemove", forceRemove],
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
                        ["openFile", openFile, {}, {}],
                    ],
                },
            ],
            [
                "AddURIs",
                {
                    "function": addUris,
                },
            ],
            [
                "Add Torrents",
                {
                    "function": addTorrents,
                },
            ],
            [
                "pauseAll",
                {
                    "function": pauseAll,
                }
            ],
            [
                "Remove completed/errored downloads",
                {
                    "function": removeCompleted,
                },
            ],
            [
                "Get Global Options",
                {
                    "function": getGlobalOption,
                }

            ],
            [
                "Get Global Stat",
                {
                    "function": getGlobalStat,
                }
            ],
            [
                "Get Session Info",
                {
                    "function": getSessionInfo,
                }
            ],
            [
                "Get Version",
                {
                    "function": getVersion,
                }
            ],
            [
                "Edit Config",
                {
                    "function": editConfig,
                }
            ],
            [
                "Restart Aria",
                {
                    "function": restartAria,
                }

            ],
        ]
    highlights = [
        {
            "match": "complete",
            "field": 1,
            "color": 8,
        },
        {
            "match": "error",
            "field": 1,
            "color": 7,
        },
        {
            "match": "active",
            "field": 1,
            "color": 9,
        },
        {
            "match": "waiting",
            "field": 1,
            "color": 11,
        },
        {
            "match": "paused",
            "field": 1,
            "color": 12,
        },
        { ## 0-20
            "match": r'^(0\d?(\.\d*)?\b|\b\d(\.\d*)?)\b%?',
            "field": 6,
            "color": 7,
        },
        {
            "match": r'^(2\d(\.\d*)?|3\d(\.\d*)?|40(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 20 to 40
            "field": 6,
            "color": 11,
        },
        {
            "match": r'^(4\d(\.\d*)?|5\d(\.\d*)?|60(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 40 to 60
            "field": 6,
            "color": 9,
        },
        {
            "match": r'^(6\d(\.\d*)?|7\d(\.\d*)?|80(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 60 to 80
            "field": 6,
            "color": 9,
        },
        {
            "match": r'^(8\d(\.\d*)?|9\d(\.\d*)?|100(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 80 to 100
            "field": 6,
            "color": 8,
        },
    ]
    menu_highlights = [
        {
            "match": "complete",
            "field": 0,
            "color": 8,
        },
        {
            "match": "error",
            "field": 0,
            "color": 7,
        },
        {
            "match": "active",
            "field": 0,
            "color": 9,
        },
        {
            "match": "waiting",
            "field": 0,
            "color": 11,
        },
    ]
    modes = [
        {
            'filter': '',
            'sort': 0,
            'name': 'All',
        },
        {
            'filter': '--1 active',
            'name': 'Active',
        },
        {
            'filter': '--1 waiting',
            'name': 'Queue',
        },
        {
            'filter': '--1 waiting|active',
            'name': 'Active+Queue',
        },
        {
            'filter': '--1 paused',
            'name': 'Paused',
        },
        {
            'filter': '--1 complete',
            'name': 'Completed',
        },
        {
            'filter': '--1 error',
            'name': 'Error',
        },
    ]

    app_name = "Aria2TUI"
    menu_persistent = False
    dl_type_list = [3]
    cursor_pos = 0
    menu_data = {
        "top_gap": 0,
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colours": custom_colours,
        "max_selected": 1,
    }
    view_loop_data = {
        "top_gap": 0,
        "highlights": highlights,
        "paginate": paginate,
        "modes": modes,
        "display_modes": True,
        "title": app_name,
        "colours": custom_colours,
        "columns_sort_method": [0, 1, 1, 7, 7, 1, 7, 5, 1, 1],
        "sort_reverse": [False, False, False, True, True, True, True, True, False, False],
    }
    watch_loop_data = {
        "top_gap": 0,
        "highlights": highlights,
        "paginate": paginate,
        "modes": modes,
        "display_modes": True,
        "title": app_name,
        "colours": custom_colours,
        "columns_sort_method": [0, 1, 1, 7, 7, 1, 7, 5, 1, 1],
        "sort_reverse": [False, False, False, True, True, True, True, True, False, False],
    }
    dl_option_data = {
        "top_gap": 0,
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colours": custom_colours,
        "require_option": [False if x[0] != "changePosition" else True for x in options[0][1]["operations"]],
    }

    while True:
        menu_data = {key:val for key, val in menu_data.items() if key not in ["items", "indexed_items"]}
        dl_type_list, opts, menu_data = list_picker(
            stdscr,
            items=[[func[0]] for func in options],
            **menu_data,
        )
        if not dl_type_list: break
        dl_type = dl_type_list[0]
        if options[dl_type][0] in ["Watch All"]:
            items, header = options[dl_type][1]["get_data"]()

            ## Remove old data from dict
            watch_loop_data = {key: val for key, val in watch_loop_data.items() if key not in ["items", "indexed_items"]}
            selected_downloads, opts, watch_loop_data = list_picker(
                stdscr,
                items=items,
                header=header,
                auto_refresh=True,
                get_new_data=True,
                refresh_function=options[dl_type][1]["get_data"],
                timer=1,
                **watch_loop_data,
            )
            if not selected_downloads: continue
        elif options[dl_type][0] in ["View All"]:
            items, header = options[dl_type][1]["get_data"]()

            ## Remove old data from dict
            view_loop_data = {key: val for key, val in view_loop_data.items() if key not in ["items", "indexed_items"]}
            selected_downloads, opts, view_loop_data = list_picker(
                stdscr,
                items=items,
                header=header,
                auto_refresh=False,
                get_new_data=False,
                refresh_function=options[dl_type][1]["get_data"],
                timer=1,
                **view_loop_data,
            )
            if not selected_downloads: continue

        elif options[dl_type][0] in ["AddURIs", "Edit Config", "Restart Aria", "Add Torrents"]:
            # Run function
            options[dl_type][1]["function"]()
            continue

        ## Global
        elif options[dl_type][0] in ["Get Global Options", "Get Global Stat", "Get Session Info", "Get Version"]:
            data = send_req(options[dl_type][1]["function"]())
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                tmpfile.write(json.dumps(data, indent=4))
                # tmpfile.write(data)
                tmpfile_path = tmpfile.name
            # cmd = f"kitty --class=reader-class nvim -i NONE {tmpfile_path}"
            cmd = f"nvim -i NONE {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
            continue

        elif options[dl_type][0] in ["pauseAll", "Remove completed/errored downloads"]:
            data = send_req(options[dl_type][1]["function"]())
            continue
        ####### THIS SHOULDN'T BE REACHED
        else:
            ## select downloads to operate upon
            items, header = options[dl_type][1]["get_data"]()
            if len(items) == 0:
                header = ["items"]
                items = [[]]
            view_loop_data = {key: val for key, val in view_loop_data.items() if key not in ["items", "indexed_items"]}
            selected_downloads, opts, view_loop_data = list_picker(
                stdscr,
                items,
                header=header,
                **view_loop_data,

            )
            if not selected_downloads or items == [[]]: continue
        # os.system(f"notify-send {repr(selected_downloads)}")
        gid_index = header.index("gid")
        fname_index = header.index("fname")
        gids = [item[gid_index] for i, item in enumerate(items) if i in selected_downloads]
        fnames = [item[fname_index] for i, item in enumerate(items) if i in selected_downloads]

        ## select action to perform on downloads
        operations = [operation_list[0] for operation_list in options[dl_type][1]["operations"]]
        items, header = operations, [f"Select operation"]
        dl_option_data = {key: val for key, val in dl_option_data.items() if key not in ["items", "indexed_items"]}
        dl_option_data["display_infobox"] = True
        dl_option_data["infobox_items"] = fnames

        operation_n, opts, dl_option_data = list_picker(
            stdscr,
            items,
            # colours=custom_colours,
            header=header,
            **dl_option_data,

        )
        if not operation_n: 
            continue
        operation = operation_n[0]
        operation_f = options[dl_type][1]["operations"][operation][1]
        operation_list = options[dl_type][1]["operations"][operation]
        operation_function = operation_list[1]

        if len(operation_list) > 2:
            operation_kwargs = operation_list[2]


        # Reset menu after selection
        view_loop_data["selections"] = {}
        watch_loop_data["selections"] = {}

        # print(f"We want to {operations[operation]}")
        # print(f"    on {gids}")
        # print(f"    from list {dl_type_list}")

        responses = []
        for gid in gids:
            try:
                # jsonreq = changePosition(gid,0)
                if operations[operation] == "changePosition":
                    position = int(opts) if opts.strip().isdigit() else 0
                    jsonreq = operation_f(str(gid), position)
                elif operations[operation] == "getAllInfo":
                    js_rs = getAllInfo(str(gid))
                    responses.append(js_rs)
                    continue

                elif len(operation_list) > 2:
                    jsonreq = operation_f(str(gid), **operation_kwargs)
                else:
                    jsonreq = operation_f(str(gid))

                js_rs = send_req(jsonreq)
                responses.append(js_rs)
            except:
                responses.append({})
                pass
        if len(operation_list) > 2 and "view" in operation_list[-1].keys() and operation_list[-1]:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                # tmpfile.write(json.dumps(data, indent=4))
                for i, response in enumerate(responses):
                    tmpfile.write(f'{"*"*50}\n{str(i)+": "+gids[i]:^50}\n{"*"*50}\n')
                    tmpfile.write(json.dumps(response, indent=4))
                # tmpfile.write(operation_f(str(gids[0])))
                # tmpfile.writelines([json.dumps(response, indent=4) for response in responses])
                # tmpfile.write(data)
                tmpfile_path = tmpfile.name
            # cmd = f"kitty --class=reader-class nvim -i NONE {tmpfile_path}"
            # cmd = r"nvim -i NONE -c '/^\s*\d'" + f" {tmpfile_path}"
            cmd = r"nvim -i NONE -c '/^\s*\"function\"'" + f" {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
        stdscr.clear()

def main():
    while True:
        connection_up = test_connection()
        if connection_up: break
        header, choices = ["Aria2c Connection down."], ["Yes", "No"]
        choice, opts, function_data = list_picker(
            stdscr,
            choices,
            colours=custom_colours,
            header=header,
            max_selected=1
        )

        if choice == [1] or choice == []: exit()

        subprocess.Popen(f"systemctl --user restart aria2d.service", shell=True, stderr=subprocess.PIPE)
        subprocess.Popen(f"systemctl --user restart ariang.service", shell=True, stderr=subprocess.PIPE)
        time.sleep(2)

    begin(config)




if __name__ == "__main__":
    # os.environ.setdefault('ESCDELAY', '25')
    
    CONFIGPATH = "~/scripts/utils/aria2tui/aria2tui.toml"
    with open(os.path.expanduser(CONFIGPATH), "rb") as f:
        config = tomllib.load(f)

    url = config["general"]["url"]
    port = config["general"]["port"]
    token = config["general"]["token"]
    paginate = config["general"]["paginate"]

    custom_colours = get_colours(config["appearance"]["theme"])
    try:
        ## Run curses
        stdscr = curses.initscr()
        stdscr.keypad(True)
        curses.start_color()
        curses.noecho()  # Turn off automatic echoing of keys to the screen
        curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)

        
        ## start connection
        # Check if config exists. If not then load default
        while True:
            connection_up = testConnection()
            if connection_up: break
            header, choices = ["Aria2c Connection down."], ["Yes", "No"]
            choice, opts, function_data = list_picker(
                stdscr,
                choices,
                colours=custom_colours,
                header=header,
                max_selected=1
            )

            if choice == [1] or choice == []: exit()
            for cmd in config["general"]["startupcmds"]:
                subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

            time.sleep(2)

        begin(config=config)
    except:
        pass
    # Clean up
    stdscr.clear()
    stdscr.refresh()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    os.system('cls' if os.name == 'nt' else 'clear')
