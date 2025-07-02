#!/bin/python
# -*- coding: utf-8 -*-
"""
speed_graph_plain_text.py

Author: GrimAndGreedy
License: MIT
"""

import time
import os
import subprocess
import toml
from urllib import request as rq
import json
import sys
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("../../..")
import tempfile
import tabulate
from typing import Callable, Tuple

from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria_adduri import addDownloadFull
# from listpick.utils.utils import *
from listpick import *
from listpick.listpick_app import *

def graph_speeds_no_curses(get_data_function, end_time, title, wait_time) -> None:
    """ Display a graph of the global stats in plain text. """
    ticker = 0
    x, y, y2 = [], [], []
    while ticker < end_time:
        x.append(ticker)
        resp = get_data_function()
        down = int(resp['result']['downloadSpeed'])
        up = int(resp['result']['uploadSpeed'])
        # down = bytes_to_human_readable(resp['result']['downloadSpeed'])
        y.append(down)
        y2.append(up)
        fig = plt.Figure()
        fig.lc = 25
        fig.color_mode = 'byte'
        # fig.lc = 'red'
        fig.bg=100
        fig.plot(x, y, lc=200, label='Download speed')
        fig.plot(x, y2, lc=25, label='Upload speed')
        fig.y_ticks_fkt = lambda y, _: bytes_to_human_readable(y)
        fig.x_ticks_fkt = lambda x, _: f"{int(x)}s"
        fig.set_y_limits(min_=0)
        fig.set_x_limits(min_=0)
# min(4, max(0, len(y)-1))
        fig.text([x[-1]], [y[0]], ['Down'], lc=200)
        fig.text([x[0]], [y2[0]], ['Up'], lc=25)
        width, height = os.get_terminal_size()
        fig.width = width - 28
        fig.height = height - 8
        os.system('cls' if os.name == 'nt' else 'clear')
        print()
        print(f"{title:^{width}}")
        print()
        print(fig.show())
        # print(plotille.plot(x, y, height=20, width=60))
        time.sleep(wait_time)
        ticker += wait_time
