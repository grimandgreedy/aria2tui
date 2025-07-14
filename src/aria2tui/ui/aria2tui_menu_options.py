#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2tui_menu_options.py

Author: GrimAndGreedy
License: MIT
"""

import os, sys
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")
os.chdir("../../..")
from aria2tui.ui.aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid
from aria2tui.ui.aria2tui_keys import download_option_keys, menu_keys, aria2tui_keys

from listpick.listpick_app import *

config = get_config()
paginate = config["general"]["paginate"]

colour_theme_number=config["appearance"]["theme"]

app_name = "Aria2TUI"
global_stats_timer = config["general"]["global_stats_timer"]
refresh_timer = config["general"]["refresh_timer"]

class Option:
    def __init__(self, name: str, function: Callable, function_args:dict = {}, meta_args: dict = {}):
        self.name = name
        self.function = function
        self.function_args = function_args
        self.meta_args = meta_args





download_options = [
    Option("Pause",   pause),
    Option("Unpause", unpause),
    Option("Change Options Picker (for each selected)", changeOptionPicker),
    Option("Change Options Picker (for all selected)", changeOptionsBatchPicker),
    Option("Change Options nvim (for each selected)", changeOptionDialog),
    Option("Change Options nvim (for all selected)", changeOptionBatchDialog),
    Option("Change Position", changePosition),
    Option("Send to Front of Queue", changePosition, {"pos":0}),
    Option("Send to Back of Queue", changePosition, {"pos":10000}),
    Option("Retry Download", retryDownload),
    Option("Retry Download and Pause", retryDownloadAndPause),
    Option("Remove (paused)", remove),
    # Option("forceRemove", forceRemove),
    # Option("removeStopped", removeDownloadResult),
    Option("Remove (errored)", removeDownloadResult),


    Option("DL Info: Files", getFiles, {}, {"picker_view":True}),
    Option("DL Info: Servers", getServers, {}, {"picker_view":True}),
    Option("DL Info: Peers", getPeers, {}, {"picker_view":True}),
    Option("DL Info: URIs", getUris, {}, {"picker_view":True}),
    Option("DL Info: Status Info", tellStatus, {}, {"picker_view":True}),
    Option("DL Info: Aria2c Options", getOption, {}, {"picker_view":True}),
    Option("DL Info: Get All Info", getAllInfo, {}, {"picker_view":True}),

    Option("Open Download Location (terminal)", lambda gid: openDownloadLocation(gid, new_window=False)),
    Option("Open Download Location (gui, new window)", openDownloadLocation),
    Option("Open File(s)", openGidFiles),
    Option("Open File(s) (do not group)", lambda gids: openGidFiles(gids, group=False)),

]


menu_options = [
    Option("Watch Downloads", lambda: 4),
    Option("View Downloads", lambda: 4),
    Option("Add URIs", addUris),
    Option("Add URIs and immediately pause", addUrisAndPause),
    Option("Add Torrents and magnet links", addTorrents),
    # Option("Pause All", pauseAll),
    # Option("Force Pause All", forcePauseAll),
    # Option("Remove completed/errored downloads", removeCompleted),

    Option("Get Global Options", getGlobalOption,{},{"picker_view": True}),
    Option("Get Global Stat", getGlobalStat,{},{"picker_view": True}),
    Option("Get Session Info", getSessionInfo,{},{"picker_view": True}),
    Option("Get Version", getVersion,{},{"picker_view": True}),
    Option("Edit Config", editConfig),
    Option("Restart Aria", restartAria,{},{"display_message": "Restarting Aria2c..." }),
]




menu_data = {
    "top_gap": 0,
    "highlights": menu_highlights,
    "paginate": paginate,
    "title": app_name,
    "colour_theme_number": colour_theme_number,
    "max_selected": 1,
    "items": [menu_option.name for menu_option in menu_options],
    #*******
    "header": ["Main Menu    "],
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
    "timer": refresh_timer,
    "paginate": paginate,
    "hidden_columns": [],
    "id_column": -1,
    "centre_in_terminal_vertical": False,
    "footer_string_auto_refresh": True,
    "keys_dict": aria2tui_keys,
    "footer_string_refresh_function": getGlobalSpeed,
    "footer_timer": global_stats_timer,
}
dl_operations_data = {
    "top_gap": 0,
    "highlights": operations_highlights,
    "paginate": paginate,
    "title": app_name,
    "colour_theme_number": colour_theme_number,
    "header": [f"Select operation"],
    "paginate": paginate,
    "hidden_columns": [],
    "keys_dict": download_option_keys,
    "cancel_is_back": True,
}
