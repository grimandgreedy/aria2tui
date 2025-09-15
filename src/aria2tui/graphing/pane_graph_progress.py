#!/bin/python
# -*- coding: utf-8 -*-
"""
pane_graph_progress.py

Author: GrimAndGreedy
License: MIT
"""

from listpick.pane.pane_utils import escape_ansi
from aria2tui.graphing.graph_utils import display_ansi
import curses
from datetime import datetime
from math import ceil
import curses


def seconds_to_short_format(seconds) -> str:
    """ 
    Convert a number of seconds to the most significant unit.

    Seconds and minutes have no decimal places, hours and days have one decimal place.
    E.g., 
        50->50s
        61->1m
        359->6m
        86400*3/2->1.5d
    """
    if seconds < 60:
        return f'{int(seconds)}s'
    elif seconds < 3600:
        minutes = round(seconds / 60)
        return f'{minutes}m'
    elif seconds < 86400:
        hours = round(seconds / 3600, 1)
        return f'{hours}h'
    else:
        days = round(seconds / 86400, 1)
        return f'{days}d'

def right_split_dl_progress_graph(stdscr, x, y, w, h, state, row, cell, past_data: list = [], data: list = [], test: bool = False):
    """
    Display a graph of the data in right pane.

    data[0] = x_vals
    data[1] = y_vals
    data[2] = id
    """
    if test: return True

    # Title
    title = "DL Progress"
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

    # Display pane count
    # pane_count = len(state["right_panes"])
    # pane_index = state["right_pane_index"]
    # if pane_count > 1:
    #     s = f" {pane_index+1}/{pane_count} "
    #     stdscr.addstr(y+h-1, x+w-len(s)-1, s, curses.color_pair(state["colours_start"]+20))

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
        import plotille as plt
    except:
        s = f"No module named 'plotille'"
        stdscr.addstr(y+2, x+2, s[:w-2])
        return None


    # x_vals, y_vals = list(range(100)), [x**2 for x in range(100)]
    if data in [[], {}, None]:
        return None


    try:
        header = state["header"]
        gid_index, fname_index, status_index = header.index("GID"), header.index("Name"), header.index("Status")

        gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
        fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]
        status  = state["indexed_items"][state["cursor_pos"]][1][status_index]
    except:
        return None

    # if status == "paused": return None

    # Display file name
    if len(fname) < w:
        fname = f"{fname:^{w}}"
    else:
        fname = f" {fname}"
    stdscr.addstr(y+1, x+1, fname[:w-1], curses.color_pair(state["colours_start"]+2) | curses.A_BOLD | curses.A_UNDERLINE)

    # We need at least 23 chars of width and at least 10 rows to display a meaningful graph.
    if w <= 23 or h < 10:
        stdscr.addstr(y+3, x+2, f'{"Pane"[:w-2]:^{w-2}}')
        stdscr.addstr(y+4, x+2, f'{"Too"[:w-2]:^{w-2}}')
        stdscr.addstr(y+5, x+2, f'{"Small"[:w-2]:^{w-2}}')
        return None

    x_vals, dls_progress = data[0], data[1]

    # x_vals consist of datetime.now() so we need to convert it to unix time and then make them relative to the first in the lest
    x_vals = [x.timestamp() for x in x_vals]
    x_vals = [x - x_vals[0] for x in x_vals]
    graph_str = get_progress_graph_string(x_vals, dls_progress, width=w-3-7, height=h-4)


    default_colours = state["colours"]["unselected_fg"], state["colours"]["unselected_bg"]
    default_colours = curses.COLOR_YELLOW, state["colours"]["unselected_bg"]
    if curses.COLOR_PAIRS > 64:
        display_ansi(
            stdscr,
            ansi_lines=[s[3:] for s in graph_str.split("\n")],
            x=x+2,
            y=y+3,
            w=w-2,
            h=h-3,
            pair_offset=200,
            default_colours=default_colours,
        )

    else:
        for i, s in enumerate(graph_str.split("\n")):
            s = escape_ansi(s)
            s = s[3:]
            stdscr.addstr(y+3+i, x+2, s[:w-2])

    return []


def get_dl_progress(data, state):
    """
    Get dl speed and add it to data[1]

    data[0]: datetime_0, datetime_1, ..., datetime_n
    data[1]: dl_progress_at_0, dl_progress_at_1, ...
    data[2]: row id
    """
    from aria2tui.utils import aria2c_utils
    import os

    if len(state["indexed_items"]) == 0:
        return [[datetime.now()], [0], -1]

    try:
        header = state["header"]
        gid_index, fname_index = header.index("GID"), header.index("Name")

        gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
        fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]
        req = aria2c_utils.tellStatus(gid)
        info = aria2c_utils.sendReq(req)
        done = info["result"]["completedLength"]
        total = info["result"]["totalLength"]
        if int(total) == 0:
            progress = 0
        else:
            progress = int(done)/int(total)
    except Exception as e:
        return data

    if data in [[], {}, None] or data[-1] != gid:
        return [[datetime.now()], [progress], gid]
    else:
        data[0].append(datetime.now())
        data[1].append(progress)
    return data



def get_progress_graph_string(x_vals, dls_progress, width=50, height=20, title=None, x_label=None, y_label=None):
    """ Generate a graph of x_vals, dls_progress using plotille"""

    import plotille as plt
    import numpy as np
    # Create a figure and axis object using plotille
    fig = plt.Figure()
    fig.color_mode = 'byte'
    if len(x_vals) == 1:
        x_dense = [x_vals[0]+i*(1/(4*width)) for i in range(width*2)]
        y_dense = [dls_progress[0] for _ in range(width*2)]
    elif len(x_vals) < 2**50:
        # Create smooth (x, y) segments between each original pair
        x_dense = []
        y_dense = []
        # steps_per_segment = min(10*width//len(x_vals), 20)
        steps_per_segment = max(2, 3*ceil(width//len(x_vals)))


        for i in range(len(x_vals) - 1):
            x_start, x_end = x_vals[i], x_vals[i + 1]
            y_start, y_end = dls_progress[i], dls_progress[i + 1]

            x_segment = np.linspace(x_start, x_end, steps_per_segment, endpoint=False)
            y_segment = np.linspace(y_start, y_end, steps_per_segment, endpoint=False)

            x_dense.extend(x_segment)
            y_dense.extend(y_segment)

        x_dense.append(x_vals[-1])
        y_dense.append(dls_progress[-1])
        
    else:
        x_dense, y_dense = x_vals, dls_progress

    for x, y in zip(x_dense, y_dense):
        fig.plot([x, x], [0, y], lc=curses.COLOR_BLUE)
    
    # if dls_progress[-1] != 1:
    #     # fig.text([x_dense[len(x_dense)//2]], [dls_progress[-1]], [f"{dls_progress[-1]*100:.1f}%"])
    #     # fig.text([(max(x_dense)-min(x_dense))/2], [.5], [f"{dls_progress[-1]*100:.1f}%"])
    #     fig.text([0], [0.95], [f"{dls_progress[-1]*100:.1f}%"])
    # else:
    #     # fig.text([(max(x_dense)-min(x_dense))/2], [.5], [f"{dls_progress[-1]*100:.1f}%"])
    #     fig.text([0], [0.95], [f"{dls_progress[-1]*100:.1f}%"])
    pc = f"{dls_progress[-1]*100:.1f}%" if dls_progress[-1] < 1 else "100%"
    text_y = min(y_dense[-1] + 0.1, 0.95)
    text_x = max((width-8)/width * x_dense[-1], 0)
    fig.text([text_x], [text_y], [pc], lc=curses.COLOR_BLUE)

    fig.width = width-10
    fig.height = height-4
    # fig.x_ticks_fkt = lambda x, _: f"{int(x)}s"
    fig.x_ticks_fkt = lambda x, _: seconds_to_short_format(x)
    fig.y_ticks_fkt = lambda y, _: f"{y*100:.0f}%"
    fig.set_y_limits(min_=0, max_=1)
    fig.set_x_limits(min_=0)
    fig.x_label = "t"
    fig.y_label = "%"
    fig.origin = False

    graph_str = str(fig.show())
    
    return graph_str
