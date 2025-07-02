#!/bin/python
# -*- coding: utf-8 -*-
"""
speed_graph.py

Author: GrimAndGreedy
License: MIT
"""

import sys, os
sys.path.append(os.path.expanduser(".."))
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("../../..")
from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria2c_utils import *
from listpick import *
from listpick.listpick_app import *
import time
import re
from typing import Callable

def escape_ansi(line: str) -> str:
    """ Remove ansi characters from string. """
    ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)

def handle_plotille_not_found(stdscr: curses.window) -> None:
    """ Display ModuleNotFoundError. """
    h, w = stdscr.getmaxyx()
    s = "ModuleNotFoundError: No module named 'plotille'"
    stdscr.addstr(h//2, (w - len(s))//2, s)
    stdscr.refresh()
    stdscr.getch()


def graph_speeds(
        stdscr: curses.window,
        get_data_function: Callable,
        timeout:int=1000,
        title:str="",
        refresh_time: int = 2,
        xposf: Callable = lambda: 0,
        yposf: Callable = lambda: 0,
        graph_wh: Callable[None,Tuple[int, int]] = lambda: os.get_terminal_size(),

    ) -> None:
    """ Display a graph of the global stats in a curses window. """
    try:
        import plotille as plt
    except:
        handle_plotille_not_found(stdscr)
        return None

    initial_time = time.time()
    x, y, y2 = [], [], []
    while time.time()-initial_time < timeout:


        resp = get_data_function()
        x.append(time.time()-initial_time)
        down = int(resp['result']['downloadSpeed'])
        up = int(resp['result']['uploadSpeed'])

        y.append(down)
        y2.append(up)

        fig = plt.Figure()
        fig.plot(x, y)
        fig.plot(x, y2)

        fig.y_ticks_fkt = lambda y, _: bytes_to_human_readable(y)
        fig.x_ticks_fkt = lambda x, _: f"{int(x)}s"
        fig.set_y_limits(min_=0)
        fig.set_x_limits(min_=0)
        fig.text([x[-1]], [y[0]], ['Dn'])
        fig.text([x[0]], [y2[0]], ['Up'])

        width, height = graph_wh()
        fig.width = width - 7
        fig.height = height - 4
        globh, globw = stdscr.getmaxyx()
        xpos, ypos = xposf(), yposf()
        maxw, maxh = globw-xpos-1, globh-ypos

        stdscr.erase()

        # Draw title
        stdscr.addstr(ypos, xpos, f"{title:^{min(width,maxw)}}")

        # Draw graph
        lines = fig.show().split('\n')
        for i, line in enumerate(lines):
            if i > maxh-2: break
            line = escape_ansi(line)

            stdscr.addstr(i+1+ypos, xpos , line[:min(width,maxw)])

        # Show the extreme points of the width and also the last printable char
        show_control_chars = False
        if show_control_chars:
            stdscr.addstr(0,0, f"{maxw}, {maxh}")
            stdscr.addstr(ypos, xpos, "*", curses.A_REVERSE)
            stdscr.addstr(ypos+maxh-1, xpos, "*", curses.A_REVERSE)
            stdscr.addstr(ypos, xpos+maxw-1, "*", curses.A_REVERSE)
            stdscr.addstr(ypos+maxh-1, xpos+maxw-2, "*", curses.A_REVERSE)
            stdscr.addstr(ypos+ min(height, maxh-1), xpos, "+", curses.A_REVERSE)
            stdscr.addstr(ypos, xpos+min(maxw-1, width), "+", curses.A_REVERSE)
            stdscr.addstr(ypos+min(height, maxh-1), xpos+min(width, maxw-2), "+", curses.A_REVERSE)

        stdscr.refresh()
        key = stdscr.getch()
        if key in [3, ord('q')]: 
            return None

def graph_speeds_gid(
        stdscr: curses.window,
        get_data_function: Callable,
        timeout:int=1000,
        title:str="",
        refresh_time: int = 2,
        xposf: Callable = lambda: 0,
        yposf: Callable = lambda: 0,
        graph_wh: Callable[None,Tuple[int, int]] = lambda: os.get_terminal_size(),
        gid:str = ""

    ) -> None:
    """ Display a graph in a curses window for a certain gid. """
    try:
        import plotille as plt
    except:
        handle_plotille_not_found(stdscr)
        return None

    initial_time = time.time()
    x, y, y2 = [], [], []
    while time.time()-initial_time < timeout:

        resp = get_data_function(gid)
        x.append(time.time()-initial_time)
        down = int(resp['result']['downloadSpeed'])
        up = int(resp['result']['uploadSpeed'])

        y.append(down)
        y2.append(up)

        fig = plt.Figure()
        fig.plot(x, y)
        fig.plot(x, y2)

        fig.y_ticks_fkt = lambda y, _: bytes_to_human_readable(y)
        fig.x_ticks_fkt = lambda x, _: f"{int(x)}s"
        fig.set_y_limits(min_=0)
        fig.set_x_limits(min_=0)
        fig.text([x[-1]], [y[0]], ['Dn'])
        fig.text([x[0]], [y2[0]], ['Up'])

        width, height = graph_wh()
        fig.width = width - 7
        fig.height = height - 4
        globh, globw = stdscr.getmaxyx()
        xpos, ypos = xposf(), yposf()
        maxw, maxh = globw-xpos-1, globh-ypos

        stdscr.erase()

        # Draw title
        stdscr.addstr(ypos, xpos, f"{title:^{min(width,maxw)}}")

        # Draw graph
        lines = fig.show().split('\n')
        for i, line in enumerate(lines):
            if i > maxh-2: break
            line = escape_ansi(line)

            stdscr.addstr(i+1+ypos, xpos , line[:min(width,maxw)])

        # Show the extreme points of the width and also the last printable char
        show_control_chars = False
        if show_control_chars:
            stdscr.addstr(0,0, f"{maxw}, {maxh}")
            stdscr.addstr(ypos, xpos, "*", curses.A_REVERSE)
            stdscr.addstr(ypos+maxh-1, xpos, "*", curses.A_REVERSE)
            stdscr.addstr(ypos, xpos+maxw-1, "*", curses.A_REVERSE)
            stdscr.addstr(ypos+maxh-1, xpos+maxw-2, "*", curses.A_REVERSE)
            stdscr.addstr(ypos+ min(height, maxh-1), xpos, "+", curses.A_REVERSE)
            stdscr.addstr(ypos, xpos+min(maxw-1, width), "+", curses.A_REVERSE)
            stdscr.addstr(ypos+min(height, maxh-1), xpos+min(width, maxw-2), "+", curses.A_REVERSE)

        stdscr.refresh()
        key = stdscr.getch()
        stdscr.refresh()
        if key in [3, ord('q')]: 
            return None
        resp = get_data_function(gid)



if __name__ == "__main__":
    title = "Global Transfer Speeds"
    end_time = 180
    get_data_function = lambda: sendReq(getGlobalStat())
    gid = "60e0c88ed77a24d6"
    get_data_function = lambda: sendReq(tellStatus(gid))
    wait_time = 2

    stdscr = start_curses()
    size_func = lambda: (
        3*os.get_terminal_size()[0]//4,
        3*os.get_terminal_size()[1]//4,
    )
    xposf = lambda: os.get_terminal_size()[0]//8
    yposf = lambda: os.get_terminal_size()[1]//8
    graph_speeds(
        stdscr,
        get_data_function=get_data_function,
        timeout=end_time,
        refresh_time=wait_time,
        title=title,
        graph_wh= size_func,
        xposf=xposf,
        yposf=yposf,
            
    )
    close_curses(stdscr)
