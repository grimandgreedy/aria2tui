#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2tui_menu_options.py

Author: GrimAndGreedy
License: MIT
"""

import os
import sys
import curses 

from listpick.listpick_app import *

from aria2tui.ui.aria2_detailing import highlights, menu_highlights, modes, operations_highlights
from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from aria2tui.graphing.speed_graph import graph_speeds, graph_speeds_gid
from aria2tui.ui.aria2tui_keys import download_option_keys, menu_keys, aria2tui_keys
from aria2tui.graphing.pane_graph import get_dl_data, right_split_dl_graph
from aria2tui.graphing.pane_graph_progress import get_dl_progress, right_split_dl_progress_graph
from aria2tui.graphing.pane_pieces import right_split_piece_progress, get_dl_pieces
from aria2tui.graphing.pane_files import right_split_files, get_dl_files
from aria2tui.utils.display_info import *


config = get_config()
paginate = config["general"]["paginate"]

colour_theme_number=config["appearance"]["theme"]

app_name = "Aria2TUI"
global_stats_timer = config["general"]["global_stats_timer"]
refresh_timer = config["general"]["refresh_timer"]
show_graph = config["appearance"]["show_right_pane_default"]
right_pane_index = config["appearance"]["right_pane_default_index"]


download_options = [
    Operation(
        name="Resume Download(s)",
        function=lambda stdscr, gid, fname, operation, function_args: unpause(gid),
        send_request=True,
        applicable_statuses=["paused"]
    ),
    Operation(
        name="Pause Download(s)",
        function=lambda stdscr, gid, fname, operation, function_args: pause(gid),
        send_request=True,
        applicable_statuses=["active", "waiting"]
    ),
    Operation(
        name="Change Position in Queue",
        # function=lambda stdscr, gid, fname, operation, function_args: changePosition(gid),
        function=lambda stdscr, gid, fname, operation, function_args: None,
        send_request=True,
        applicable_statuses=["waiting", "paused", "active"]
    ),
    Operation(
        name="Send to Front of Queue",
        function=lambda stdscr, gid, fname, operation, function_args: changePosition(gid, pos=0),
        send_request=True,
        applicable_statuses=["waiting", "paused", "active"]
    ),
    Operation(
        name="Send to Back of Queue",
        function=lambda stdscr, gid, fname, operation, function_args: changePosition(gid, pos=100000),
        send_request=True,
        applicable_statuses=["waiting", "paused", "active"]
    ),
    Operation(
        name="Open Download Location",
        function=lambda stdscr, gid, fname, operation, function_args: openDownloadLocation(gid, new_window=False),
        reapply_terminal_settings=True,
        applicable_statuses=["active", "waiting", "paused", "complete", "error", "removed"]
    ),
    Operation(
        name="Open Download Location (gui, new window)",
        function=lambda stdscr, gid, fname, operation, function_args: openDownloadLocation(gid),
        applicable_statuses=["active", "waiting", "paused", "complete", "error", "removed"]
    ),
    Operation(
        name="Open File(s)",
        function=lambda stdscr, gids, fnames, operation, function_args: openGidFiles(gids),
        accepts_gids_list=True,
        applicable_statuses=["active", "waiting", "complete"]
    ),
    Operation(
        name="Change Filename(s)",
        function=lambda stdscr, gid, fname, operation, function_args: changeFilenameForm(stdscr, gid, fname),
        # send_request=True,
        applicable_statuses=["active", "waiting", "paused"]
    ),
    # Operation(
    #     name="Change Options Picker (for each selected)",
    #     function=lambda stdscr, gid, fname, operation, function_args: changeOptionPicker(stdscr, gid),
    #     applicable_statuses=["active", "waiting", "paused"]
    # ),
    Operation(
        name="Change Options",
        function=lambda stdscr, gids, fnames, operation, function_args: changeOptionsBatchPicker(stdscr, gids),
        accepts_gids_list=True,
        applicable_statuses=["active", "waiting", "paused"]
    ),
    # Operation(
    #     name="Change Options nvim (for each selected)",
    #     function=lambda stdscr, gid, fname, operation, function_args: changeOptionDialog(gid),
    #     reapply_terminal_settings=True,
    #     applicable_statuses=["active", "waiting", "paused"]
    # ),
    Operation(
        name="Change Options in NeoVim (For All Selected)",
        function=lambda stdscr, gids, fnames, operation, function_args: changeOptionBatchDialog(gids),
        accepts_gids_list=True,
        reapply_terminal_settings=True,
        applicable_statuses=["active", "waiting", "paused"]
    ),
    Operation(
        name="Modify Torrent Files",
        function=lambda stdscr, gids, fnames, operation, function_args: download_selected_files(stdscr, gids),
        accepts_gids_list=True,
        applicable_statuses=["active", "paused", "waiting"],
        torrent_operation=True
    ),
    Operation(
        name="Retry Download(s)",
        function=lambda stdscr, gid, fname, operation, function_args: retryDownload(gid),
        applicable_statuses=["error", "removed", "complete"]
    ),
    Operation(
        name="Retry Download(s) and Pause",
        function=lambda stdscr, gid, fname, operation, function_args: retryDownloadAndPause(gid),
        applicable_statuses=["error", "removed", "complete"]
    ),
    Operation(
        name="Remove Download(s)",
        function=lambda stdscr, gids, fnames, operation, function_args: remove_downloads(gids),
        accepts_gids_list=True,
        applicable_statuses=["active", "waiting", "paused", "complete", "error"]
    ),
    # Operation(
    #     name="Remove (paused/waiting)",
    #     function=lambda stdscr, gid, fname, operation, function_args: remove(gid),
    #     send_request=True,
    #     applicable_statuses=["paused", "waiting"]
    # ),
    # Operation("forceRemove", forceRemove),
    # Operation("removeStopped", removeDownloadResult),
    # Operation(
    #     name="Remove (errored/completed)",
    #     function=lambda stdscr, gid, fname, operation, function_args: removeDownloadResult(gid),
    #     send_request=True,
    #     applicable_statuses=["error", "complete"]
    # ),
    Operation(
        name="Show Download Information",
        function=lambda stdscr, gids, fnames, operation, function_args: display_info_menu(stdscr, gids, fnames, operation),
        accepts_gids_list=True,
        applicable_statuses=["active", "waiting", "paused", "complete", "error", "removed"]
    ),
    # Operation(
    #     name="Open File(s) (do not group)",
    #     function=lambda stdscr, gids, fnames, operation, function_args: openGidFiles(gids, group=False),
    #     accepts_gids_list=True,
    # ),
    Operation(
        name="Transfer Speed Graph",
        function=lambda stdscr, gid, fname, operation, function_args: graph_speeds_gid(stdscr, gid=gid, **function_args),
        function_args={
            "get_data_function": lambda gid: sendReq(tellStatus(gid)),

            "graph_wh" : lambda: (
                os.get_terminal_size()[0]-8,
                os.get_terminal_size()[1]-2,
            ),
            "timeout": 1000,

            "xposf" : lambda: 4,
            "yposf" : lambda: 1,
            "title": "Download Transfer Speeds",
        },
        applicable_statuses=["active", "waiting", "paused", "complete", "error", "removed"]
    ),

]


menu_options = [
    Operation(
        name="Watch Downloads",
        function=lambda: 4
    ),
    Operation(
        name="View Downloads",
        function=lambda stdscr=None, gid=0, fname="", operation=None, function_args={}: 4,
    ),
    # Operation( name="Add URIs", addUris, {}, {"reapply_terminal_settings": True}),
    # Operation( name="Add URIs and immediately pause", addUrisAndPause, {}, {"reapply_terminal_settings": True}),
    Operation(
        name="Add Download Task (Form)",
        function=lambda stdscr, gids, fnames, operation, function_args: addDownloadTasksForm(),
        reapply_terminal_settings=True,
    ),
    Operation(
        name="Add Download Tasks",
        function=lambda stdscr, gids, fnames, operation, function_args: addDownloadsAndTorrents(),
        reapply_terminal_settings=True,
    ),
    Operation(
        name="Add Download Tasks & Pause", 
        function=lambda stdscr, gids, fnames, operation, function_args: addDownloadsAndTorrentsAndPause(),
        reapply_terminal_settings=True,
    ),
    Operation(
        name="Add Torrent Files (file picker)",
        function=lambda stdscr, gids, fnames, operation, function_args: addTorrentsFilePicker(),
        reapply_terminal_settings=True,
    ),
    # Operation( name="Add Torrents (nvim)", addTorrents, {}, {"reapply_terminal_settings": True}),
    # Operation( name="Pause All", pauseAll),
    # Operation( name="Force Pause All", forcePauseAll),
    # Operation( name="Remove completed/errored downloads", removeCompleted),

    Operation(
        name="Get Global Options",
        function=lambda stdscr, gids, fnames, operation, function_args: getGlobalOption(),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="Get Global Stats",
        function=lambda stdscr, gids, fnames, operation, function_args: getGlobalStat(),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="Get Session Info",
        function=lambda stdscr, gids, fnames, operation, function_args: getSessionInfo(),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="Get Version",
        function=lambda stdscr, gids, fnames, operation, function_args: getVersion(),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="Edit Config",
        function=lambda stdscr, gids, fnames, operation, function_args: editConfig(), 
        reapply_terminal_settings=True,
    ),
    Operation(
        name="Restart Aria",
        function=lambda stdscr, gids, fnames, operation, function_args: restartAria(),
        meta_args={"display_message": "Restarting Aria2c..." }
    ),
    Operation(
        name="Transfer Speed Graph (Global)", 
        function=lambda stdscr, gids, fnames, operation, function_args: graph_speeds(stdscr, **function_args), 
        function_args={
            "get_data_function": lambda: sendReq(getGlobalStat()),

            "graph_wh" : lambda: (
                os.get_terminal_size()[0]-8,
                os.get_terminal_size()[1]-2,
            ),
            "timeout": 1000,

            "xposf" : lambda: 4,
            "yposf" : lambda: 1,
            "title": "Global Transfer Speeds",
        }
    ),
]

download_info_menu = [
    Operation(
        name="DL Info: Get All Info",
        function=lambda stdscr, gid, fname, operation, function_args: getAllInfo(gid),
        form_view=True,
    ),
    Operation(
        name="DL Info: Files",
        function=lambda stdscr, gids, fnames, operation, function_args: display_files(stdscr, gids, fnames, operation),
        accepts_gids_list=True,
    ),
    Operation(
        name="DL Info: Servers",
        function=lambda stdscr, gid, fname, operation, function_args: getServers(gid),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="DL Info: Peers",
        function=lambda stdscr, gid, fname, operation, function_args: getPeers(gid),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="DL Info: URIs",
        function=lambda stdscr, gid, fname, operation, function_args: getUris(gid),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="DL Info: Status Info",
        function=lambda stdscr, gid, fname, operation, function_args: tellStatus(gid),
        send_request=True,
        form_view=True,
    ),
    Operation(
        name="DL Info: Aria2c Options",
        function=lambda stdscr, gid, fname, operation, function_args: getOption(gid),
        send_request=True,
        form_view=True,
    ),
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
    "editable_by_default": False,
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
    "editable_by_default": False,
    # "split_right_function": right_split_dl_graph,
    # "split_right_refresh_data": get_dl_data,
    # "split_right_proportion": 2/3,
    # "split_right_auto_refresh": True,
    # "split_right_refresh_data_timer": 1.0,
    # "split_right_function": right_split_dl_progress_graph,
    # "split_right_refresh_data": get_dl_progress,
    "macros": aria2tui_macros,
}
dl_operations_data = {
    "items": [[download_option.name] for download_option in download_options],
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
    "editable_by_default": False,
}
