#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2_keys.py
Define key dictionary for controlling the Picker.

Author: GrimAndGreedy
License: MIT
"""

import curses

download_option_keys = {
    "refresh":                          [curses.KEY_F5],
    "help":                             [ord('?')],
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "move_column_left":                 [ord('{')],
    "move_column_right":                [ord('}')],
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
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l')],
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
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l')],
    "redraw_screen":                    [12], # Ctrl-l
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('i')],
    "cancel":                           [27], # Escape key
    "opts_input":                       [ord(':')],
    "mode_next":                        [9], # Tab key
    "mode_prev":                        [353], # Shift+Tab key
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
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l')],
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
