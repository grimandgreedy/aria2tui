#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2tui_menu_options.py

Author: GrimAndGreedy
License: MIT
"""

import os, sys
from aria2tui.ui.aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid
from aria2tui.ui.aria2tui_keys import download_option_keys, menu_keys, aria2tui_keys
from aria2tui.graphing.pane_graph import get_dl_data, right_split_dl_graph
from aria2tui.graphing.pane_graph_progress import get_dl_progress, right_split_dl_progress_graph
from aria2tui.graphing.pane_pieces import right_split_piece_progress, get_dl_pieces
from aria2tui.graphing.pane_files import right_split_files, get_dl_files

from listpick.listpick_app import *
from aria2tui.utils.display_info import *

config = get_config()
paginate = config["general"]["paginate"]

colour_theme_number=config["appearance"]["theme"]

app_name = "Aria2TUI"
global_stats_timer = config["general"]["global_stats_timer"]
refresh_timer = config["general"]["refresh_timer"]
show_graph = config["appearance"]["show_right_pane_default"]
right_pane_index = config["appearance"]["right_pane_default_index"]

class Option:
    def __init__(
        self, name: str,
        function: Callable,
        function_args:dict = {},
        meta_args: dict = {},
        exec_only: bool = False,
    ):
        self.name = name
        self.function = function
        self.function_args = function_args
        self.meta_args = meta_args
        self.exec_only = exec_only

download_options = [
    Option("Pause",   pause),
    Option("Unpause", unpause),
    Option("Change Options Picker (for each selected)", changeOptionPicker),
    Option("Change Options Picker (for all selected)", changeOptionsBatchPicker),
    Option("Change Options nvim (for each selected)", changeOptionDialog),
    Option("Change Options nvim (for all selected)", changeOptionBatchDialog),
    Option("Modify torrent files (active/paused/waiting)", selected_download),
    Option("Change Position", changePosition),
    Option("Send to Front of Queue", changePosition, {"pos":0}),
    Option("Send to Back of Queue", changePosition, {"pos":10000}),
    Option("Retry Download", retryDownload),
    Option("Retry Download and Pause", retryDownloadAndPause),
    Option("Remove (paused/waiting)", remove),
    # Option("forceRemove", forceRemove),
    # Option("removeStopped", removeDownloadResult),
    Option("Remove (errored/completed)", removeDownloadResult),


    Option("DL Info: Files", display_files, {}, {"picker_view":True}, exec_only = True),
    Option("DL Info: Servers", getServers, {}, {"picker_view":True}),
    Option("DL Info: Peers", getPeers, {}, {"picker_view":True}),
    Option("DL Info: URIs", getUris, {}, {"picker_view":True}),
    Option("DL Info: Status Info", tellStatus, {}, {"picker_view":True}),
    Option("DL Info: Aria2c Options", getOption, {}, {"picker_view":True}),
    Option("DL Info: Get All Info", getAllInfo, {}, {"picker_view":True}),

    Option("Open Download Location (terminal)", lambda gid: openDownloadLocation(gid, new_window=False), {}, {"refresh_terminal_options": True}),
    Option("Open Download Location (gui, new window)", openDownloadLocation),
    Option("Open File(s)", openGidFiles),
    Option("Open File(s) (do not group)", lambda gids: openGidFiles(gids, group=False)),

]


menu_options = [
    Option("Watch Downloads", lambda: 4),
    Option("View Downloads", lambda: 4),
    # Option("Add URIs", addUris, {}, {"refresh_terminal_options": True}),
    # Option("Add URIs and immediately pause", addUrisAndPause, {}, {"refresh_terminal_options": True}),
    Option("Add Download Tasks", addDownloadsAndTorrents, {}, {"refresh_terminal_options": True}),
    Option("Add Download Tasks & Pause", addDownloadsAndTorrentsAndPause, {}, {"refresh_terminal_options": True}),
    Option("Add Torrents (file picker)", addTorrentsFilePicker, {}, {"refresh_terminal_options": True}),
    # Option("Add Torrents (nvim)", addTorrents, {}, {"refresh_terminal_options": True}),
    # Option("Pause All", pauseAll),
    # Option("Force Pause All", forcePauseAll),
    # Option("Remove completed/errored downloads", removeCompleted),

    Option("Get Global Options", getGlobalOption,{},{"picker_view": True}),
    Option("Get Global Stat", getGlobalStat,{},{"picker_view": True}),
    Option("Get Session Info", getSessionInfo,{},{"picker_view": True}),
    Option("Get Version", getVersion,{},{"picker_view": True}),
    Option("Edit Config", editConfig, {}, {"refresh_terminal_options": True}),
    Option("Restart Aria", restartAria,{},{"display_message": "Restarting Aria2c..." }),
]




menu_data = {
    "top_gap": 0,
    "highlights": menu_highlights,
    "paginate": paginate,
    "title": app_name,
    "colour_theme_number": colour_theme_number,
    "max_selected": 1,
    "items": [[menu_option.name] for menu_option in menu_options],
    "header": ["Main Menu    "],
    "centre_in_terminal": True,
    "centre_in_cols": False,
    "paginate": paginate,
    "centre_in_terminal_vertical": True,
    "hidden_columns": [],
    "keys_dict": menu_keys,
    "show_footer": False,
    "number_columns": False,
    "cell_cursor": False,
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
    "columns_sort_method": [0, 1, 1, 7, 7, 1, 6, 7, 5, 1, 1, 1, 1],
    "sort_reverse": [False, False, False, True, True, True, True, True, False, False, False, False, False],
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
    "cell_cursor": False,

    "split_right": show_graph,
    "right_panes": [
        # DL files
        {
            "proportion": 1/2,
            "display": right_split_files,
            "get_data": get_dl_files,
            "data": [],
            "auto_refresh": True,
            "refresh_time": 0.2,
        },
        # DL transfer speed graph
        {
            "proportion": 1/3,
            "display": right_split_dl_graph,
            "get_data": get_dl_data,
            "data": [],
            "auto_refresh": True,
            "refresh_time": 1.0,
        },
        # DL progress graph
        {
            "proportion": 1/3,
            "display": right_split_dl_progress_graph,
            "get_data": get_dl_progress,
            "data": [],
            "auto_refresh": True,
            "refresh_time": 1.0,
        },
        # DL Pieces
        {
            "proportion": 1/3,
            "display": right_split_piece_progress,
            "get_data": get_dl_pieces,
            "data": [],
            "auto_refresh": True,
            "refresh_time": 1.0,
        },
    ],
    "right_pane_index": right_pane_index,
    "footer_string": "?/s 󰇚 ?/s 󰕒 | ?A ?W ?S",
    # "split_right_function": right_split_dl_graph,
    # "split_right_refresh_data": get_dl_data,
    # "split_right_proportion": 2/3,
    # "split_right_auto_refresh": True,
    # "split_right_refresh_data_timer": 1.0,
    # "split_right_function": right_split_dl_progress_graph,
    # "split_right_refresh_data": get_dl_progress,
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
    "number_columns": False,
    "cell_cursor": False,
}
