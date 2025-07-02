#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2tui.py

Author: GrimAndGreedy
License: MIT
"""

from aria2tui_app import aria2tui
from aria2tui_app import *
from utils.aria2c_utils import *
from utils.aria_adduri import *
from ui.aria2_detailing import *
from ui.aria2tui_keys import *
from ui.aria2tui_menu_options import *
from lib.aria2c_wrapper import *
from graphing.speed_graph import *
from graphing.speed_graph_plain_text import *

if __name__ == "__main__":
    aria2tui()
