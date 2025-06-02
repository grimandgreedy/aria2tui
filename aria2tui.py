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
from aria2_detailing import highlights, menu_highlights, modes

r"""
TODO 
Errors
    ( ) fix adding uris with filename. Data is the same but it is corrupted somehow.
       - works:        https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg
       - doesn't work: https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLBVWNXUrlGnx3VtnPULUE6v0EteQg
    ( ) When downloads are updating quickly and I try to operate upon them it sometimes says that the indices are not in the list...

Bugs
    ( ) Fix order upon refresh
        ( ) when the item order refreshes (e.g. new downloads added) the selected items change. need to associate the selected items with gids and then create new selected items which will be passed back
    ( ) (!!!) Fix cursor position upon refresh
        ( ) takes us back to the top when it refreshes in a different mode (I think due to filter)
        ( ) add pin_cursor option to prevent the cursor from going down when refreshing
        ( ) might have to do with filtering; 
        ( ) when original sort order there is no jumping
        ( ) lots of jumping when sorting by size
    ( ) Filter/search problems
        ( ) ^[^\s] matches all rows in help but only highlights the first col
            ( ) seems to match the expression in any col but then only show highlights based on the row_str so misses matches in the second col
    ( ) restrict refresh so that it doesn't exit on the menu
    ( ) infobox causes flickering

Features
    ( ) allow options when adding uris; perhaps use the same structure as the aria2c input file
        (*) done in principle
        ( ) Allow all possible options to be specified
    ( ) improve menu navigation
        (*) when downloads are selected and we go back they should still be selected
    ( ) add global stats bar
    ( ) monitor log file
    ( ) setup https connection
    ( ) add source column, showing site from which it is being downloaded
    ( ) Create passive notification
    ( ) Add notifications to the following:
        - adding downloads (# succeeeded or failed)
    ( ) implement changeOption for downloads
    ( ) add key to open download location using 'o'
    ( ) (!!!) make operations upon downloads work only with certain download types:
       (*) make remove work with all
       ( ) queue operations only on those in the queue
       ( ) retry only on errored
    ( ) add column to show download type (e.g., torrent)
    ( ) add support for multiple aria servers

Improvements
    ( ) Redo colours
       - completed: green
       - active: blue
       - paused: ??? gray?

    ( ) (!!!) make operations on downloads into a batch request
    ( ) examine parsing of toml (why are the arguments set outside of the main function?)
    ( ) add to config
       (*) url
       (*) port
       (*) startupcmds
       (*) theme
       (*) paging vs scrolling
       ( ) highlights off
       ( ) color off
    ( ) live setting changes
        (*) show/hide columns
        (*) centre in cols & centre in terminals
        ( ) theme
    (?) Allow name to be specified with magnet link
        (?) I don't think this is possible to change in aria2c
    (*) open files 
        ( ) open files of the same type in one instance
    (*) make remove work with errored download
       (*) remove all errored/completed downloads works




DONE
 (*) If a download is paused and it is paused again it throws an error when it should just skip it.
 (*) implement addTorrent
 (*) Return a list of files and % completed for each file in a torrent.
 (*) check if remove completed/errored is working
 (*) show all downloads (not just 500)
    - set max=5000 which should be fine
    - had to set the max in the aria config file as well
 (*) Add a getAllInfo option for downloads
 (*) open location
 (*) figure out how to keep the row constant when going back and forth between menus
 (*) make fetching active, queue, and stopped downloads into a batch request
 (*) (!!!) high CPU usage
    - when val in `stdscr.timeout(val)` is low the cpu usage is high
 (*) colour problems:
    - aria2tui > view downloads > 'q' > 'z' 
    (*) fixed by arbitarily setting 0-50 for application colours, 50-100 for help colours and 100-150 for notification colours
 (*) have to open watch active twice; first time exits immediately...
 (*) add preview of selected downloads when selecting options
    (*) implemented infobox
 (*) artifacts after opening download location in terminal; have to refresh before and after?
    (*) stdscr.clear() after yazi closes
 (*) add a lambda function for add_download so that url and port don't have to be specifed
 (*) some sudden exits from the watch all menu
    (*) caused by get_new_data not being in the function data
 (*) add empty values for inapplicable cols
 (*) get all function
 (*) fix not resizing properly
 (*) watch active only refreshes upon a keypress
 (*) (!!!) add retry download function by getting download data, remove it and readd it
 (*) info is wrong for torrents. The size, % completed, etc. Might need to rework the the data scraped from the json response.
 (*) after nvim is opened (e.g., show all dl info) the display needs to be redrawn
 (*) (!!!) there is a problem with the path when readding downloads sometimes. It is correct in the download info but is displayed wrong???
    (*) was caused by discordant order of getting download options and the main download information
 (*) fix dir; it should be obtained from getInfo; 
 (*) Add a view all tasks option
 (*) When I change a download to position 4, the user_option 4 will remain in the options going forward
    (*) reset user_opts after option select
 (*) fix filenames; also check torrents
 (*) add highlights for % complete
 (*) make percentage bar look nicer
 (*) add url to test_connection
 (*) add default sort method for columns
 (*) remove old watch loop; pass refresh function to watch, no refresh function to view
 (*) remove completed not working
 (*) Add hidden columns to function so that they remain hidden on refresh
 (*) Add color to highlight errored and completed tasks
 (*) implement proper retrydownload function 
 (*) create watch all
 (*) make fetching active, queue, and stopped downloads into a batch request (all)

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


def begin(stdscr, config):
    url = config["general"]["url"]
    port = config["general"]["port"]
    token = config["general"]["token"]
    paginate = config["general"]["paginate"]

    custom_colours = get_colours(config["appearance"]["theme"])

    # ["NAME", function, functionargs, extra]
    download_options = [
        ["pause", pause, {}, {}],
        ["unpause", unpause, {}, {}],
        ["changePosition", changePosition, {}, {}],
        ["sendToFrontOfQueue", changePosition, {"pos":0} , {}],
        ["sendToBackOfQueue", changePosition, {"pos":10000}, {}],
        ["retryDownload", retryDownload, {}, {}],
        # ["remove", remove, {}, {}],
        # ["forceRemove", forceRemove, {}, {}],
        # ["removeStopped", removeDownloadResult, {}, {}],
        ["Remove Download", removeDownloadResult, {}, {}],
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
        ["Open File(s)", openFile, {}, {}],
        ["Open File(s) (do not group)", lambda gids: openFile(gids, group=False), {}, {}],
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
        ["Restart Aria", restartAria,{},{}],
    ]
    # appLoop(stdscr, config, highlights, menu_highlights, custom_colours, modes, options)
    appLoop(stdscr, config, highlights, menu_highlights, custom_colours, modes, download_options, menu_options)

def appLoop(stdscr, config, highlights, menu_highlights, custom_colours, modes, download_options, menu_options):
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
    }
    dl_option_data = {
        "top_gap": 0,
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colours": custom_colours,
        # "require_option": [False if x[0] != "changePosition" else True for x in options[0][1]["operations"]],
        "require_option": [False if x[0] != "changePosition" else True for x in download_options],
        "header": [f"Select operation"],
    }
    while True:
        downloads_data = {key: val for key, val in downloads_data.items() if key not in ["items", "indexed_items"]}
        ## SELECT DOWNLOADS
        selected_downloads, opts, downloads_data = list_picker(
            stdscr,
            **downloads_data,
        )

        if selected_downloads:
            # operation, operation_function = [operation_list[0] for operation_list in options[dl_type][1]["operations"]]
            operations = [x[0] for x in download_options]
            operation_functions = [x[1] for x in download_options]
            dl_option_data = {key: val for key, val in dl_option_data.items() if key not in ["items", "indexed_items"]}
            header = downloads_data["header"]
            items = downloads_data["items"]
            gid_index = header.index("gid")
            fname_index = header.index("fname")
            gids = [item[gid_index] for i, item in enumerate(items) if i in selected_downloads]
            fnames = [item[fname_index] for i, item in enumerate(items) if i in selected_downloads]

            dl_option_data["display_infobox"] = True
            dl_option_data["infobox_items"] = fnames

            ## SELECT DOWNLOAD OPTION
            selected_operation, opts, dl_option_data = list_picker(
                stdscr,
                items=operations,
                # colours=custom_colours,
                **dl_option_data,
            )
            if selected_operation:
                operation_name, operation_function = operations[selected_operation[0]], operation_functions[selected_operation[0]]
                user_opts = dl_option_data["user_opts"]
                view = False
                operation_list = download_options[selected_operation[0]]
                ## e.g., operation_list = ["getFiles", getFiles, {}, {"view":True}]
                if len(operation_list) > 2 and "view" in operation_list[-1] and operation_list[-1]["view"]: view=True
                applyToDownloads(stdscr, gids, operation_name, operation_function, user_opts, view)
                downloads_data["selections"] = {}
                dl_option_data["user_opts"] = ""
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
                func(**kwargs)
    
def applyToDownloads(stdscr, gids, operation_name, operation_function, user_opts, view):
    responses = []
    if operation_name in ["Open File(s) (do not group)", "Open File(s)"]:
        operation_function(gids)
    else:
        for gid in gids:
            try:
                jsonreq = {}
                if operation_name == "changePosition":
                    position = int(user_opts) if user_opts.strip().isdigit() else 0
                    jsonreq = operation_function(str(gid), position)
                elif operation_name == "getAllInfo":
                    js_rs = getAllInfo(str(gid))
                    responses.append(js_rs)
                elif operation_name == "sendToBackOfQueue":
                    jsonreq = operation_function(str(gid), pos=10000)
                elif operation_name == "sendToFrontOfQueue":
                    jsonreq = operation_function(str(gid), pos=0)
                # elif len(operation_list) > 2:
                #     operation_kwargs = operation_list[2]
                #     jsonreq = operation_function(str(gid), **operation_kwargs)
                else:
                    jsonreq = operation_function(str(gid))

                js_rs = sendReq(jsonreq)
                responses.append(js_rs)
            except:
                pass
                # responses.append({})
        if view:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                for i, response in enumerate(responses):
                    tmpfile.write(f'{"*"*50}\n{str(i)+": "+gids[i]:^50}\n{"*"*50}\n')
                    tmpfile.write(json.dumps(response, indent=4))
                tmpfile_path = tmpfile.name
            cmd = r"nvim -i NONE -c '/^\s*\"function\"'" + f" {tmpfile_path}"
            cmd = r"""nvim -i NONE -c 'setlocal bt=nofile' -c 'silent! %s/^\s*"function"/\0'""" + f" {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    stdscr.clear()

def main():
    ## Load config
    CONFIGPATH = "~/scripts/utils/aria2tui/aria2tui.toml"
    with open(os.path.expanduser(CONFIGPATH), "rb") as f:
        config = tomllib.load(f)

    url = config["general"]["url"]
    port = config["general"]["port"]
    token = config["general"]["token"]
    paginate = config["general"]["paginate"]

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
