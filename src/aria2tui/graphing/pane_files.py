#!/bin/python
# -*- coding: utf-8 -*-
"""
pane_files.py

Author: GrimAndGreedy
License: MIT
"""

from aria2tui.utils.aria2c_utils import bytes_to_human_readable
import curses
import os
import re


def right_split_files(stdscr, x, y, w, h, state, row, cell: list = [], data: list = [], test: bool = False):
    """
    Display the files of the cursor-hovered download in the right pane.

    data[0]: list of files
    data[1]: gid
    """
    if test: return True

    # Title
    title = "DL Files"
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

    # Separator
    for j in range(h):
        stdscr.addstr(j+y, x, ' ', curses.color_pair(state["colours_start"]+16))

    # Display pane count
    pane_count = len(state["right_panes"])
    pane_index = state["right_pane_index"]
    if pane_count > 1:
        s = f" {pane_index+1}/{pane_count} "
        stdscr.addstr(y+h-1, x+w-len(s)-1, s, curses.color_pair(state["colours_start"]+20))

    if len(state["indexed_items"]) == 0:
        return None

    try:
        header = state["header"]
        gid_index, fname_index, status_index = header.index("GID"), header.index("Name"), header.index("Status")

        gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
        fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]
        status  = state["indexed_items"][state["cursor_pos"]][1][status_index]
    except:
        return None

    # Display file name
    if len(fname) < w:
        fname = f"{fname:^{w}}"
    else:
        fname = f" {fname}"
    stdscr.addstr(y+1, x+1, fname[:w-1], curses.color_pair(state["colours_start"]+2) | curses.A_BOLD | curses.A_UNDERLINE)

    # # If the gid is different then update the data
    # if len(data) and gid != data[1]:
    #     data = [get_dl_files(data, state), gid]


    if data in [[], {}, None, ""]:
        return None

    items = data[0]
    number_to_display = min(len(items), h-5)
    for i in range(number_to_display):
        s = items[i]
        stdscr.addstr(y+3+i, x+2, s[:w-2])

    if number_to_display < len(items):
        stdscr.addstr(y+3+number_to_display, x+2, f" ... {len(items)-number_to_display} more"[:w-2])

    return []


def get_dl_files(data, state) -> list:
    """
    Get a bitstring indicating which pieces of the download have finished.

    data[0]: list of files
    data[1]: gid
    """
    from aria2tui.utils import aria2c_utils

    if len(state["indexed_items"]) == 0:
        return [[], -1]

    try:
        header = state["header"]
        gid_index, fname_index = header.index("GID"), header.index("Name")
        gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
        fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]


        # # If we have already got the list of files for this dl then return them
        # if data not in [[], {}, None, ""] and data[-1] == gid:
        #     return data

        req = aria2c_utils.tellStatus(gid)
        info = aria2c_utils.sendReq(req)

        dir = info["result"]["dir"]

        req = aria2c_utils.getFiles(gid)
        files_dict = aria2c_utils.sendReq(req)
        files = [f["path"] for f in files_dict["result"]]

        # Remove common path
        # files = [f["path"][len(dir)+1:] if f["path"].startswith(dir) else f["path"] for f in files_dict["result"]]
        files = [os.path.basename(f["path"]) for f in files_dict["result"]]

        sizes = [bytes_to_human_readable(files_dict["result"][i]["length"]) for i in range(len(files))]
        for i in range(len(sizes)):
            sizes[i] = re.sub("\.\d+ KB", " KB", sizes[i])
            sizes[i] = re.sub("\.\d+ MB", " MB", sizes[i])
            
        max_width = max(len(s) for s in sizes)

        if len(files) == 1 and files[0].strip() == "": return [[], gid]
        for i in range(len(files)):
            done = files_dict["result"][i]["completedLength"]
            total = files_dict["result"][i]["length"]
            if total == '0':
                progress = 0
            else:
                progress = int(done)/int(total)

            selected_q = files_dict["result"][i]["selected"]
            selected = "[*]" if selected_q == "true" else "[ ]"

            # files[i] = f"{sizes[i]:<{max_width}} [{progress*100:.1f}%] {files[i]}"
            files[i] = f"{selected} {sizes[i]:<{max_width}} [{progress*100:.1f}%] {files[i]}"

        return [files, gid]
    except:

        return [[], -1]
