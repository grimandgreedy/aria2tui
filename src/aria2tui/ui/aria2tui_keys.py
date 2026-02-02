#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2_keys.py
Define key dictionary for controlling the Picker.

Author: GrimAndGreedy
License: MIT
"""

import curses
from listpick.listpick_app import picker_keys
from copy import copy
from listpick.utils import keycodes

aria2tui_keys = copy(picker_keys)

remove_keys = [
    "move_column_left",
    "move_column_right",
    "delete",
    "delete_column",
    "increase_lines_per_page",
    "decrease_lines_per_page",
    "edit",
    "edit_nvim",
    "edit_picker",
    "load",
    "open",
    "notification_toggle",
    "undo",
    "add_column_after",
    "add_column_before",
    "add_row_before",
    "add_row_after",
    "toggle_left_pane",
    "cycle_left_pane",
    "paste",
    "exit",
]

for key in remove_keys:
    if key in aria2tui_keys: del aria2tui_keys[key]

# set 'q'

aria2tui_keys["minimise"] = [ord('q')]

download_option_keys = {
    "refresh":                          [curses.KEY_F5],
    "help":                             [ord('?')],
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K'), keycodes.META_k],
    "five_down":                        [ord('J'), keycodes.META_j],
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l'), 13],
    "redraw_screen":                    [12], # Ctrl-l
    "cycle_sort_method":                [ord('s')],
    "cycle_sort_method_reverse":        [ord('S')],
    "cycle_sort_order":                 [ord('t')],
    "delete":                           [curses.KEY_DC],
    "increase_column_width":            [ord(']')],
    "decrease_column_width":            [ord('[')],
    "search_input":                     [ord('/')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('i')],
    "cancel":                           [27], # Escape key
    "opts_input":                       [ord(':')],
    "opts_select":                      [ord('o')],
    "notification_toggle":              [ord('z')],
    "mode_next":                        [9], # Tab key
    "mode_prev":                        [353], # Shift+Tab key
    "reset_opts":                       [ord('\\')],
    "edit_ipython":                     [5], # Ctrl+e
}

notification_keys = {
    "exit":                             [ord('q'), ord('h'), curses.KEY_ENTER, ord('\n'), ord(' '), 27],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE],
    "page_down":                        [curses.KEY_NPAGE],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "redraw_screen":                    [12], # Ctrl-l
    "opts_input":                       [ord(':')],
    "opts_select":                      [ord('o')],
}


menu_keys = {
    "help":                             [ord('?')],
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K'), keycodes.META_k],
    "five_down":                        [ord('J'), keycodes.META_j],
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l'), 13],
    "redraw_screen":                    [12], # Ctrl-l
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('i')],
    "cancel":                           [27], # Escape key
    "opts_input":                       [ord(':')],
    "mode_next":                        [9], # Tab key
    "mode_prev":                        [353], # Shift+Tab key
    "edit_ipython":                     [5], # Ctrl+e
}


options_keys = {
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "toggle_select":                    [ord(' ')],
    "select_all":                       [ord('m'), 1], # Ctrl-a
    "select_none":                      [ord('M'), 18],   # Ctrl-r
    "visual_selection_toggle":          [ord('v')],
    "visual_deselection_toggle":        [ord('V')],
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l'), 13],
    "redraw_screen":                    [12], # Ctrl-l
    "cycle_sort_method":                [ord('s')],
    "cycle_sort_method_reverse":        [ord('S')],
    "cycle_sort_order":                 [ord('t')],
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "settings_input":                   [ord('`')],
    "continue_search_forward":          [ord('i')],
    "continue_search_backward":         [ord('I')],
    "cancel":                           [27], # Escape key
    "col_select":                       [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')],
}


# Key descriptions for downloader view
downloader_keys_descriptions = {
    # Navigation - downloads context
    "cursor_down": "Move to next download",
    "cursor_up": "Move to previous download",
    "page_down": "Next page of downloads",
    "page_up": "Previous page of downloads",
    "cursor_top": "Jump to first download",
    "cursor_bottom": "Jump to last download",
    "half_page_down": "Scroll down half page",
    "half_page_up": "Scroll up half page",
    "five_down": "Move down 5 downloads",
    "five_up": "Move up 5 downloads",

    # Selection - download management
    "toggle_select": "Select/deselect download",
    "select_all": "Select all downloads",
    "select_none": "Deselect all downloads",
    "visual_selection_toggle": "Start visual selection mode",
    "visual_deselection_toggle": "Start visual deselection mode",
    "enter": "Confirm selection / Open operations menu",

    # File operations - daemon switching
    "mode_next": "Switch to next download daemon",
    "mode_prev": "Switch to previous download daemon",

    # Data operations - download actions
    "delete": "Remove download from queue",
    "refresh": "Refresh download status",

    # Filter and search
    "filter_input": "Filter downloads by name/status",
    "search_input": "Search downloads",
    "continue_search_forward": "Find next match",
    "continue_search_backward": "Find previous match",

    # Sorting
    "cycle_sort_method": "Change sort method (forward)",
    "cycle_sort_method_reverse": "Change sort method (backward)",
    "cycle_sort_order": "Toggle sort ascending/descending",

    # UI controls
    "notification_toggle": "Toggle notifications panel",
    "redraw_screen": "Refresh display",
    "help": "Show keyboard shortcuts",
    "opts_input": "Command input mode",
    "opts_select": "Quick options menu",
    "reset_opts": "Reset options to default",

    # Column operations
    "increase_column_width": "Increase column width",
    "decrease_column_width": "Decrease column width",

    # Exit
    "exit": "Return to main menu",
    "minimise": "Minimize to background",
    "full_exit": "Force quit application",
    "cancel": "Cancel current operation",

    # Advanced
    "edit_ipython": "Open IPython debug console",
}

# Key descriptions for menu view
menu_keys_descriptions = {
    "cursor_down": "Move to next menu item",
    "cursor_up": "Move to previous menu item",
    "page_down": "Next page of menu items",
    "page_up": "Previous page of menu items",
    "cursor_top": "Jump to first menu item",
    "cursor_bottom": "Jump to last menu item",
    "half_page_down": "Scroll down half page",
    "half_page_up": "Scroll up half page",
    "five_down": "Move down 5 items",
    "five_up": "Move up 5 items",
    "enter": "Select menu option",
    "filter_input": "Filter menu items",
    "search_input": "Search menu",
    "continue_search_forward": "Find next match",
    "continue_search_backward": "Find previous match",
    "redraw_screen": "Refresh display",
    "help": "Show keyboard shortcuts",
    "opts_input": "Command input mode",
    "mode_next": "Switch mode forward",
    "mode_prev": "Switch mode backward",
    "exit": "Exit application",
    "full_exit": "Force quit application",
    "cancel": "Cancel / Go back",
    "edit_ipython": "Open IPython debug console",
}

# Key descriptions for download operations menu
download_operations_keys_descriptions = {
    "cursor_down": "Move to next operation",
    "cursor_up": "Move to previous operation",
    "page_down": "Next page of operations",
    "page_up": "Previous page of operations",
    "cursor_top": "Jump to first operation",
    "cursor_bottom": "Jump to last operation",
    "half_page_down": "Scroll down half page",
    "half_page_up": "Scroll up half page",
    "five_down": "Move down 5 operations",
    "five_up": "Move up 5 operations",
    "enter": "Execute operation on selected downloads",
    "search_input": "Search operations",
    "continue_search_forward": "Find next match",
    "continue_search_backward": "Find previous match",
    "redraw_screen": "Refresh display",
    "help": "Show keyboard shortcuts",
    "cycle_sort_method": "Change sort method (forward)",
    "cycle_sort_method_reverse": "Change sort method (backward)",
    "cycle_sort_order": "Toggle sort ascending/descending",
    "increase_column_width": "Increase column width",
    "decrease_column_width": "Decrease column width",
    "notification_toggle": "Toggle notifications panel",
    "mode_next": "Switch mode forward",
    "mode_prev": "Switch mode backward",
    "opts_input": "Command input mode",
    "opts_select": "Quick options menu",
    "reset_opts": "Reset options to default",
    "exit": "Cancel / Return to downloads",
    "full_exit": "Force quit application",
    "cancel": "Cancel / Go back",
}
