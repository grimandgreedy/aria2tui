import curses
import re
from numpy import sort_complex
from pandas._libs.lib import is_scalar
from pandas.core.computation.ops import isnumeric
from list_picker_colours import get_colours
import pyperclip
import os
import subprocess
import argparse
from table_to_list_of_lists import *
from math import log10
import time
from datetime import datetime
from wcwidth import wcwidth, wcswidth
from utils import *
from sorting import *
from filtering import *
from data_stuff import test_items, test_highlights

# NOTE: Look for lines like this
# TODO: 
# WARNING: 
# FIX: here
# PERF: 
# HACK:
"""
- c,y copies filtered rows but Y says out of range
- adjust width of particular columns
- Add a set of themes that are changeable
- if no items are selected pipe cursor to command
 - add option to start with X rows already selected (for watch active selection)
 - prevent overspill on last row
 - help screen doesn't adjust when terminal resized
 - add search/filter on help page
 - when +,* is added to the filter it errors out
 - pass colours to list_picker in a more intuitive way
 - some capture groups don't work [^0]
 - show/hide col based on name; have tab auto complete
 - option to search visible columns only
 - remain on same row when resizing with +/-
 - add option for padding/border
    - stdscr.box
 - disable visual selection when # is greater than max_selected
 - put help in a popup like opts
 - redo keybinds
     - n/N search next/prev
 - should general search be cell-wise?
    - e.g., wmv$ shows no matches but --3 wmv$ shows matches
 - add option to go to next dissimilar value in column
    - e.g., select column 2 (complete download), and pressing tab will go to the next that is not complete 
 - when column is selected try best guess search method
 - adjust default column width based on current page?
 - there is a difference between search matches and highlights because the highlights operate on what is displayed
    - What to do?
    - allow visual matches with searches?
    - hide highlights across fields?
 - add notification system
 - Add error handling
    - apply_settings("sjjj") 
 - complete get_colours loop
 - toggle cursor visibility
 - change hidden_columns from set() to list()
 - make unselectable_indices work with filtering
 - look at adjustment for cursor position and hidden unselectable indices
 - each time we pass options it will resort and refilter; add an option to simply load the items that are passed
 - sendReq()...
 - flickering when "watching"
    - Is it the delay caused by fetching the data? Maybe fetch and then refresh?
 - moving columns:
    - ruins highlighting
    - is not preserved when in function_data
 - when visually selecting sometimes single rows above are highlighted (though not selected)
 - add key-chain support 
    - gg
    - count
 - change the cursor tracker from current_row, current_page to current_pos
 - add tabs for quick switching
 - add header for title
 - add header tabs
 - add colour for active setting; e.g., when filter is being entered the bg should be blue
 - check if mode filter in query when updating the query and if not change the mode
 - when sorting on empty data it throws an error
 - add option to require options
 - filter problems
    - "--1 error .*" doesn't work but ".* --1" error does
 - add return value; e.g., refreshing
 - when filter string is too long it crashes
 - option to number columns or not
 - make sure `separator` works with header
 - add cursor when inputing filter, opts, etc.
 - weird alignment problem when following characters are in cells:
    - ： 
 - add support for multiple aria servers
 - hiding a column doesn't hide the corresponding header cell
 - add colour for selected column
 - highlighting doesn't disappear when columns are hidden
 - add scroll bar

COPY:

    copy IDs of selected rows (currently 'y')
    copy selected rows, visible values of visible cols (currently 'Y')
    copy selected rows, full values of visible cols (currently 'c') (NEW 'y')
    copy full python table (currently/NEW 'C')

    copy selected rows, full values of all cols (NEW 'Y')

    copy selected rows as python table
    copy selected rows as python table without hidden cols (NEW 'c')

    m + c: copies all visible rows
    
    Y = toggle_cols() + y
    C = toggle_cols() + c
    
    hidden cols, selected rows, 

???
        selections = [False] * len(items)
        selections = {i: False for i in range(len(items))}

DONE
 - Make escape work with : (as it does with | and f)
 - make filter work with regular expressions
   - adjust page after resize
   - fix not resizing properly
   - fix header columns not being aligned (fixed by replacing tabs with spaces so char count clipped properly)
 - rows not aligned with chinese characters (need to trim display rows based on wcswidth)
- fix problems with empty lists both [] and [[],[]] 
 - fix issue where item when filtering the cursor goes to a nonexistent item
 - add unselectable_indices support for filtered rows and visual selection
 - allow a keyword match for colors in columns (error, completed)
 - fix time sort
 - add colour highlighting for search and filter
 - fix highlights when columns are shortened
 - highlights wrap on bottom row
 - add search count
    - add option to continue search rather than finding all matches every time
        - problem when filter is applied
- (!!!) Fix visual selection in the entries are sorted differently.
  - when filtered it selects entries outside of those visible and throws an error
 - add config file
 - add highlight colour differentiation for selected and under cursor
 - remain on same row when sorting (23-5-25)
 - add option to stay on item when sorting
 - fix highlighting when cols are hidden
 - Add hidden columns to function so that they remain hidden on refresh
- Fix the position of a filter and options when terminal resizes
- fix the filtering so that it works with more than one arg
 - fix error when filtering to non-existing rows
 - implement settings:
     - !11 show/hide 11th column
     - ???
 - allow state to be restored
      - allow search/filter to be passed to list_picker so that search can resume
      - cursor postion (x)
      - page number
      - sort
      - filter state
      - search
      - show/hide cols
 - implement scroll as well as page view
 - why the delay when pressing escape to cancel selection, remove filter, search, etc.
    * the problem is that ESCDELAY has to be set
 - (!!!) high CPU usage
    * when val in `stdscr.timeout(val)` is low the cpu usage is high

"""

def list_picker(
        stdscr, 
        items,
        cursor_pos=0,
        colors=None,
        max_selected=None,
        top_gap=1,
        title="",
        header=None,
        max_width=70,
        timer=False,
        get_new_data=False,
        refresh_function=None,
        unselectable_indices=[],
        highlights=[],
        number_columns=True,


        current_row = 0,
        current_page = 0,
        sort_reverse = False,  # Default sort order (ascending)
        is_selecting = False,
        is_deselecting = False,
        start_selection = None,
        end_selection = None,
        user_opts = "",
        user_settings = "",
        separator = "    ",
        search_query = "",
        search_count = 0,
        search_index = 0,
        filter_query = "",
        hidden_columns = set(),  # Track hidden columns
        indexed_items = [],
        scroll_bar = True,

        selections = {},
        items_per_page = -1,
        sort_method = 0,
        sort_column = None,
        key_chain = "",

        paginate=False,
        mode_index=0,
        modes=[{}],
        display_modes=False,
        require_option=[],
):
    """
    A simple list picker using ncurses.
    Args:
        items (list of lists): A list of rows to be displayed in the list picker.
        colors (dict, optional): A dictionary mapping indices to color pairs. Defaults to None.
        max_selected (int, optional): The maximum number of items that can be selected. Defaults to None.
        top_gap (int, optional): The number of lines to leave at the top of the screen. Defaults to 1.
        header (str, optional): A string to display as a header above the list picker. Defaults to None.
        max_width (int, optional): The maximum width of the list picker window. Defaults to 70.
        timer (bool, optional): Whether to display a timer at the bottom of the screen. Defaults to False.
        get_new_data (bool, optional): Whether to call refresh_function when new data is available. Defaults to False.
        refresh_function (function, optional): A function to call when new data is available. Defaults to None.
        highlights (list[dicts]): any fields that should be highlighted with the given color pair
    Returns:
        list, opts, cursor_pos: A list of indices representing the selected items along with any options passed
        selected, opts, cursor_pos

        selected (list of ints): list of selected indices
        opts (str): any opts that are entered
        cursor_pos (int): the cursor_pos upon exit
    """
    def main():


        # Helper function to parse numerical values

        # def time_sort(time_str):
        #     """A sorting key function that converts a time string to total seconds."""
        #     return time_to_seconds(time_str)

        # Sort items initially
        # sort_items()


        def move_column(direction):
            nonlocal items, column_widths,sort_column, header
            try:
                if sort_column == None: return None
            except:
                return None
            if not (0 <= sort_column + direction < len(column_widths)):
                return
            new_index = sort_column + direction

            # Swap columns in each row
            for row in items:
                row[sort_column], row[new_index] = row[new_index], row[sort_column]
            header[sort_column], header[new_index] = header[new_index], header[sort_column]

            # Swap column widths
            column_widths[sort_column], column_widths[new_index] = column_widths[new_index], column_widths[sort_column]

            # Update current column index
            sort_column = new_index

            draw_screen()

        def draw_screen(clear=True):
            nonlocal filter_query, search_query, search_count, search_index, highlights, column_widths, start_selection, is_deselecting, is_selecting, paginate, title, modes, cursor_pos, hidden_columns, scroll_bar

            if clear:
                # stdscr.clear()
                stdscr.erase()
            h, w = stdscr.getmaxyx()

            # scroll
            ## start: 0, current_pos-items_per_page//2, or len(indexed_items)-items_per_page
            # start_index = max(0, current_pos - items_per_page//2)
            
            # paginate
            if paginate:
                start_index = (cursor_pos//items_per_page) * items_per_page
                end_index = min(start_index + items_per_page, len(indexed_items))
            # scroll
            else:
                scrolloff = items_per_page//2
                start_index = max(0, min(cursor_pos - (items_per_page-scrolloff), len(indexed_items)-items_per_page))
                end_index = min(start_index + items_per_page, len(indexed_items))
            if len(indexed_items) == 0: start_index, end_index = 0, 0

            top_space = top_gap
            # Display title (if applicable)
            if title:
                stdscr.addstr(top_gap, 0, f"{' ':^{w}}", curses.color_pair(17))
                title_x = (w-wcswidth(title))//2
                # title = f"{title:^{w}}"
                stdscr.addstr(top_gap, title_x, title, curses.color_pair(16) | curses.A_BOLD)
                top_space += 1
            if display_modes:
                stdscr.addstr(top_space, 0, ' '*w, curses.A_REVERSE)
                modes_list = [f"{mode['name']}" if 'name' in mode else f"{i}. " for i, mode in enumerate(modes)]
                # mode_colours = [mode["colour"] for mode ]
                mode_widths = get_mode_widths(modes_list)
                split_space = (w-sum(mode_widths))//len(modes)
                xmode = 0
                for i, mode in enumerate(modes_list):
                    if i == len(modes_list)-1:
                        mode_str = f"{mode:^{mode_widths[i]+split_space+(w-sum(mode_widths))%len(modes)}}"
                    else:
                        mode_str = f"{mode:^{mode_widths[i]+split_space}}"
                    # current mode
                    if i == mode_index:
                        stdscr.addstr(top_space, xmode, mode_str, curses.color_pair(14) | curses.A_BOLD)
                    # other modes
                    else:
                        stdscr.addstr(top_space, xmode, mode_str, curses.color_pair(15) | curses.A_UNDERLINE)
                    xmode += split_space+mode_widths[i]
                top_space += 1

                


            # Display header
            if header:
                # header_str = format_row(header)
                # stdscr.addstr(top_gap, 0, header_str, curses.color_pair(3))
                column_widths = get_column_widths(items, header=header, max_width=max_width, number_columns=number_columns)
                # header_str = ' '.join(f"{i+1}. {header[i].ljust(column_widths[i])}" for i in range(len(header)) if i not in hidden_columns)
                header_str = ""
                for i in range(len(header)):
                    if i in hidden_columns: continue
                    number = f"{i}. " if number_columns else ""
                    header_str += number
                    header_str +=f"{header[i].ljust(column_widths[i])}"
                    header_str += " "
                # header_str = ' '.join(f"{i}. " if number_columns else "" + f"{header[i].ljust(column_widths[i])}" for i in range(len(header)) if i not in hidden_columns)
                # header_str = format_row([f"{i+1}. {col}" for i, col in enumerate(header)])
                stdscr.addstr(top_space, 0, header_str[:w], curses.color_pair(4) | curses.A_BOLD)
                # stdscr.addstr(top_gap + 1, 0, '-' * len(header_str), curses.color_pair(3))
                # stdscr.addstr(top_gap, 0, header_str[:w], curses.color_pair(4) | curses.A_BOLD)


            # Display items
            for idx in range(start_index, end_index):
                y = idx - start_index + top_space + (1 if header else 0)
                item = indexed_items[idx]
                x = 0

                # Check item selection
                if idx == cursor_pos:
                    color_pair = curses.color_pair(5) | curses.A_BOLD  # Selected item
                else:
                    color_pair = curses.color_pair(2)  # Unselected item
                    if selections[item[0]]:
                        color_pair = curses.color_pair(1)  # Selected item
                    if is_selecting and item[0] == start_selection:
                        color_pair = curses.color_pair(1)  # Selected item
                    ## is_selecting and cursor is above start_selection and entryinforloop between start_line and cursor
                    elif is_selecting and idx <= cursor_pos and idx >= start_selection:
                        color_pair = curses.color_pair(1)  # Selected item
                    elif is_selecting and idx >= cursor_pos and idx <= start_selection:
                        color_pair = curses.color_pair(1)  # Selected item
                    elif is_deselecting and idx <= cursor_pos and idx >= start_selection:
                        color_pair = curses.color_pair(2)  # Selected item
                    # elif is_deselecting and cursor_pos <= start_selection and idx >= current_pos and idx <= start_selection:
                    elif is_deselecting and idx >=cursor_pos and idx <= start_selection:
                        color_pair = curses.color_pair(2)  # Selected item

                    # else:
                    #     color_pair = curses.color_pair(2)  # Unselected item

                stdscr.attron(color_pair)

                row_str = format_row(item[1], hidden_columns, column_widths, separator)
                h, w = stdscr.getmaxyx()

                try:
                    # Display row with potential clipping
                    stdscr.addstr(y, x, row_str[:w], color_pair)
                except curses.error:
                    pass  # Handle errors due to cursor position issues

                # Display selection indicator
                indicator = '[X]' if selections[item[0]] else '[ ]'
                indicator = ""
                try:
                    # stdscr.addstr(y, x + len(row_str), indicator, curses.color_pair(1) | curses.A_BOLD)
                    pass
                except curses.error:
                    pass  # Handle errors due to cursor position issues

                stdscr.attroff(color_pair)

                # Add color highlights
                # if len(highlights) > 0:
                #     os.system(f"notify-send 'match: {len(highlights)}'")
                for highlight in highlights:
                    try:
                        if highlight["field"] == "all":
                            match = re.search(highlight["match"], row_str, re.IGNORECASE)
                            if not match: continue
                            highlight_start = match.start()
                            highlight_end = match.end()
                        # elif type(highlight["field"]) == type(4) and  highlight["match"] == item[1][highlight["field"]].strip():
                        elif type(highlight["field"]) == type(4) and highlight["field"] not in hidden_columns:
                            match = re.search(highlight["match"], item[1][highlight["field"]][:column_widths[highlight["field"]]], re.IGNORECASE)
                            if not match: continue
                            field_start =  + sum([wcswidth(x) for x in item[1][:highlight["field"]]]) + highlight["field"]*len(separator) + 1
                            field_start =  + sum([wcswidth(x) for x in item[1][:highlight["field"]]]) + highlight["field"]*len(separator) + 1
                            field_start = sum(column_widths[:highlight["field"]]) + highlight["field"]*wcswidth(separator)
                            field_start = sum([width for i, width in enumerate(column_widths[:highlight["field"]]) if i not in hidden_columns]) + sum([1 for i in range(highlight["field"]) if i not in hidden_columns])*wcswidth(separator)
                            highlight_start = wcswidth(item[1][:match.start()]) + field_start
                            highlight_end = match.end() + field_start
                        else:
                            continue
                        color_pair = curses.color_pair(highlight["color"])  # Selected item
                        if idx == cursor_pos:
                            color_pair = curses.color_pair(highlight["color"])  | curses.A_REVERSE
                        stdscr.attron(color_pair)
                        # highlight_start = row_str.index(highlight["match"])
                        # highlight_end = highlight_start + len(highlight["match"])
                        highlight_len = highlight_start - highlight_end


                        # stdscr.addstr(y, highlight_start, highlight["match"], color_pair)
                        h, w = stdscr.getmaxyx()
                        stdscr.addstr(y, highlight_start, row_str[highlight_start:min(w, highlight_end)], color_pair | curses.A_BOLD)
                    # except curses.error:
                    except:
                        pass  # Handle errors due to cursor position issues
                    stdscr.attroff(color_pair)
                    # os.system(f"notify-send 'match: {y}, {highlight_start}'")

            if scroll_bar:
                pass
            # Display page number and count
            # stdscr.addstr(h - 3, 0, f"Page {current_page + 1}/{(len(indexed_items) + items_per_page - 1) // items_per_page}", curses.color_pair(4))

            # Display sort information
            sort_column_info = f"Column: {sort_column if sort_column is not None else 'None'}"
            sort_method_info = f"Method: {SORT_METHODS[sort_method]}"
            sort_order_info = "Desc." if sort_reverse else "Asc."
            stdscr.addstr(h - 3, 0, f" Sort: {sort_column_info} | {sort_method_info} | {sort_order_info} ", curses.color_pair(4))
            # Display selection count
            selected_count = sum(selections.values())
            
            # stdscr.addstr(h - 1, 0, f"Selected items: {selected_count}", curses.color_pair(3))
            # stdscr.addstr(h - 4, 0, f"Selected items: {selected_count}/{len(indexed_items)}", curses.color_pair(3))
            if paginate:
                stdscr.addstr(h - 2, 0, f" {cursor_pos+1}/{len(indexed_items)}  Page {cursor_pos//items_per_page + 1}/{(len(indexed_items) + items_per_page - 1) // items_per_page}  Selected {selected_count} ", curses.color_pair(4))
            else:
                stdscr.addstr(h - 2, 0, f" {cursor_pos+1}/{len(indexed_items)}  |  Selected {selected_count} ", curses.color_pair(4))

            select_mode = "Cursor"
            if is_selecting: select_mode = "Visual Selection"
            elif is_deselecting: select_mode = "Visual deselection"

            # stdscr.addstr(h - 1, 0, f" {select_mode} {int(bool(key_chain))*'    '}", curses.color_pair(4))
            # stdscr.addstr(h - 1, 0, f" {select_mode} ", curses.color_pair(4))

            try:
                if filter_query:
                    stdscr.addstr(h - 2, 50, f" Filter: {filter_query} ", curses.color_pair(4))  # Display filter query
                if search_query:
                    stdscr.addstr(h - 3, 50, f" Search: {search_query} [{search_index}/{search_count}] ", curses.color_pair(4))  # Display filter query
            except:
                pass
            try:
                if user_opts:
                    stdscr.addstr(h-1, 50, f" Opts: {user_opts} ", curses.color_pair(4))  # Display additional text
            except: pass

            stdscr.refresh()
            

        # Function to sort indexed_items

        # Use global color settings
        nonlocal colors, top_gap, header, max_width, items, unselectable_indices
        # global is_selecting, is_deselecting
        nonlocal current_row, current_page, cursor_pos, sort_reverse, user_opts, separator, search_query, search_count, filter_query, hidden_columns, selections, items_per_page, sort_method, sort_column, start_selection, end_selection, is_selecting, is_deselecting, indexed_items, highlights, key_chain, modes, mode_index, require_option, number_columns, scroll_bar


        if timer: initial_time = time.time()

        curses.curs_set(0)
        # stdscr.nodelay(1)  # Non-blocking input
        stdscr.timeout(2000)  # Set a timeout for getch() to ensure it does not block indefinitely
        if not timer: stdscr.clear()
        stdscr.refresh()

        ## Ensure that items is a List[List[Str]] object
        if items == []: items = [[]]
        if not isinstance(items[0], list):
            items = [[item] for item in items]
        items = [[str(cell) for cell in row] for row in items]


        # Ensure that header is of the same length as the rows
        if header and len(header) != len(items[0]):
            header = [header[i] if i < len(header) else f"" for i in range(len(items[0]))]

        # Constants
        h, w = stdscr.getmaxyx()
        # DEFAULT_ITEMS_PER_PAGE = os.get_terminal_size().lines - top_gap*2-2-int(bool(header))
        top_space = top_gap
        if title: top_space+=1
        if display_modes: top_space+=1
        DEFAULT_ITEMS_PER_PAGE = h - top_space*2-2-int(bool(header))
        HELP_LINES_PER_PAGE = h - top_space*2-2-int(bool(header))
        state_variables = {}
        SORT_METHODS = ['original', 'lexical', 'LEXICAL', 'alphanum', 'ALPHANUM', 'time', 'numerical', 'size']

        # Initialize colors
        # Check if terminal supports color
        if curses.has_colors() and colors != None:
            # raise Exception("Terminal does not support color")
            curses.start_color()
            curses.init_pair(1, colors['selected_fg'], colors['selected_bg'])       # selected colour
            curses.init_pair(2, colors['unselected_fg'], colors['unselected_bg'])
            curses.init_pair(3, colors['normal_fg'], colors['background'])
            curses.init_pair(4, colors['header_fg'], colors['header_bg'])
            curses.init_pair(5, colors['cursor_fg'], colors['cursor_bg'])             # cursor colour
            curses.init_pair(6, colors['normal_fg'], colors['background'])  # Filter color
            curses.init_pair(7, colors['error_fg'], colors['error_bg'])  # Filter color
            curses.init_pair(8, colors['complete_fg'], colors['complete_bg'])  # Filter color
            curses.init_pair(9, colors['active_fg'], colors['active_bg'])  # Filter color
            curses.init_pair(10, colors['search_fg'], colors['search_bg'])  # Filter color
            curses.init_pair(11, colors['waiting_fg'], colors['waiting_bg'])  # Filter color
            curses.init_pair(12, colors['paused_fg'], colors['paused_bg'])  # Filter color
            curses.init_pair(13, colors['active_input_fg'], colors['active_input_bg'])  # Filter color
            curses.init_pair(14, colors['modes_selected_fg'], colors['modes_selected_bg'])  # Filter color
            curses.init_pair(15, colors['modes_unselected_fg'], colors['modes_unselected_bg'])  # Filter color
            curses.init_pair(16, colors['title_fg'], colors['title_bg'])  # Filter color
            curses.init_pair(17, colors['normal_fg'], colors['title_bar'])  # Filter color

        # Set terminal background color
        stdscr.bkgd(' ', curses.color_pair(3))  # Apply background color

        # Initial states
        if len(selections) != len(items):
            selections = {i : False if i not in selections else bool(selections[i]) for i in range(len(items))}
        items_per_page = DEFAULT_ITEMS_PER_PAGE
        if indexed_items == []:
            indexed_items = list(enumerate(items))
        column_widths = get_column_widths(items, header=header, max_width=max_width, number_columns=number_columns)
        if require_option == []:
            require_option = [False for x in indexed_items]

        # If a filter is passed then refilter
        if filter_query:
            # prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
            # prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
            indexed_items = filter_items(items, indexed_items, filter_query)
            if cursor_pos in [x[0] for x in indexed_items]: cursor_pos = [x[0] for x in indexed_items].index(cursor_pos)
            else: cursor_pos = 0
        # If a sort is passed
        if sort_column != None and sort_method != 0:
            sort_items(indexed_items, sort_method=sort_method, sort_column=sort_column, sort_reverse=sort_reverse)  # Re-sort items based on new column
        if len(items[0]) == 1:
            number_columns = False

        # current_row = cursor_pos%items_per_page if cursor_pos < len(items) else 0
        # current_page = cursor_pos//items_per_page if cursor_pos < len(items) else 0

        ## Don't need to initialise (!?)
        # sort_column = None
        # sort_method = 0
        # sort_reverse = False  # Default sort order (ascending)
        # hidden_columns = set()  # Track hidden columns
        # is_selecting = False
        # is_deselecting = False
        # user_opts = ""
        # user_settings = ""
        # separator = "    "
        # search_query = ""
        # search_count = 0
        # search_index = 0
        # filter_query = ""
        # start_selection = None
        # end_selection = None

        h, w = stdscr.getmaxyx()
        # assert current_page*DEFAULT_ITEMS_PER_PAGE + current_row not in unselectable_indices

        # Adjust variables to ensure correctness if errors
        ## Move to a selectable row (if applicable)
        if len(items) <= len(unselectable_indices): unselectable_indices = []
        new_pos = (cursor_pos)%len(items)
        while new_pos in unselectable_indices and new_pos != cursor_pos:
            new_pos = (new_pos + 1) % len(items)

        assert new_pos < len(items)
        cursor_pos = new_pos
        

        # if not isinstance(items[0], str)
        # Determine if items is a list of lists

        # Create a list of tuples (index, item) to preserve original indices

        def get_function_data():
            function_data = {
                "selections": selections,
                "items_per_page":  items_per_page,
                "current_row":     current_row,
                "current_page":    current_page,
                "cursor_pos":      cursor_pos,
                "sort_column":     sort_column,
                "sort_method":     sort_method,
                "sort_reverse":    sort_reverse,
                "hidden_columns":  hidden_columns,
                "is_selecting":    is_selecting,
                "is_deselecting":  is_deselecting,
                "user_opts":       user_opts,
                "user_settings":   user_settings,
                "separator":       separator,
                "search_query":    search_query,
                "search_count":    search_count,
                "search_index":    search_index,
                "filter_query":    filter_query,
                "indexed_items":   indexed_items,
                "start_selection": start_selection,
                "end_selection":   end_selection,
                "highlights":      highlights,
                "max_width":       max_width,
                "mode_index":      mode_index,
                "modes":           modes,
                "title":           title,
                "display_modes":   display_modes,
                "require_option":  require_option,
                "top_gap":         top_gap,
                "number_columns":  number_columns,
                "items":           items,
                "indexed_items":   indexed_items,
                "scroll_bar":      scroll_bar,
            }
            return function_data
        # Calculate the maximum width for each column
        def pipe_to_command():
            draw_screen()
            # stdscr.addstr(h - 2, 50, "Command: ", curses.color_pair(6))
            # curses.echo()
            # stdscr.addstr(curses.LINES - 3, 58, " " * (curses.COLS - 8))  # Clear line
            cursor = 0
            # usrtxt = "sed -e 's/\\(.*\\)/new\\/\\1/' | xargs -d '\n' "
            usrtxt = "xargs -d '\n' -I{}  "
            # command = ""
            while True:
                stdscr.addstr(h - 2, 50, f"Command: {repr(usrtxt)}", curses.color_pair(13))
                if usrtxt and cursor != 0:
                    stdscr.addstr(h - 2, 50+len(usrtxt)-cursor+1+len("Command: "), f"{usrtxt[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
                else:
                    stdscr.addstr(h - 2, 50-cursor+len(usrtxt)+1+len("Command: "), f" ", curses.color_pair(13) | curses.A_REVERSE)
                # stdscr.addstr(curses.LINES - 3, 58, command.ljust(curses.COLS - 8))
                # stdscr.refresh()
                key = stdscr.getch()
                if key == 27:  # ESC key
                    break
                elif key == 10:  # Enter key
                    # selected_data = [f"'{format_full_row(items[i])}'" for i, selected in enumerate(selections) if selected]
                    selected_indices = print_selected_indices()
                    if not selected_indices:
                        selected_indices = [indexed_items[cursor_pos][0]]
                    full_values = [format_row_full(items[i], hidden_columns) for i in selected_indices]  # Use format_row_full for full data
                    # selected_data = [format_full_row(items[i]).strip() for i, selected in enumerate(selections) if selected and i not in hidden_columns]
                    if full_values:
                        # os.system("notify-send " + "'" + '\t'.join(full_values).replace("'", "*") + "'")
                        process = subprocess.Popen(usrtxt, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.communicate(input='\n'.join(full_values).encode('utf-8'))
                    break
                elif key == curses.KEY_BACKSPACE or key == "KEY_BACKSPACE" or key == 263:
                    if cursor == 0:
                        usrtxt = usrtxt[:-1]
                    else:
                        usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]
                elif key == 4: # ^d
                    pass

                elif key == curses.KEY_LEFT:
                    cursor = min(len(usrtxt), cursor + 1)
                elif key == curses.KEY_RIGHT:
                    cursor = max(0, cursor - 1)
                elif key == curses.KEY_UP:
                    cursor = max(0, cursor - 1)
                elif key == 21 or key == "^U": ## CTRL+U
                    usrtxt = ""
                    cursor = 0
                elif key == 1: ## CTRL+A (beginning)
                    cursor = len(usrtxt)
                elif key == 5: ## CTRL+E (end)
                    cursor = 0
                else:
                    if isinstance(key, int):
                        try:
                            val = chr(key) if chr(key).isprintable() else ''
                        except:
                            val = ''
                    else: val = key
                    if cursor == 0:
                        usrtxt += val
                    else:
                        usrtxt = usrtxt[:-cursor] + val + usrtxt[-cursor:]
            # curses.echo()
                draw_screen()

            curses.noecho()
            draw_screen()

        # Function to print the list of selected indices
        def print_selected_indices():
            selected_indices = [x[0] for x in indexed_items if selections[x[0]]]
            return selected_indices

        # Function to print the list of selected values
        def print_selected_values():
            selected_values = [items[x][0] for x in print_selected_indices()]
            return selected_values

        # Function to copy selected indices to clipboard
        def copy_indices():
            indices = print_selected_indices()
            pyperclip.copy(', '.join(map(str, indices)))

        # Function to copy selected values to clipboard
        def copy_values():
            values = print_selected_values()
            formatted_values = [format_row(item[1], hidden_columns, column_widths, separator) for item in indexed_items if item[0] in print_selected_indices()]
            pyperclip.copy('\n'.join(formatted_values))

        # Function to copy full values of selected entries to clipboard
        def copy_full_values():
            selected_indices = print_selected_indices()
            full_values = [format_row_full(items[i], hidden_columns) for i in selected_indices]  # Use format_row_full for full data
            pyperclip.copy('\n'.join(full_values))

        def copy_all_to_clipboard():
            formatted_items = [[x for i, x in enumerate(item) if i not in hidden_columns] for item in items]
            pyperclip.copy(repr(formatted_items))
            stdscr.addstr(h - 2, 50, f"{len(formatted_items)}R,{len(formatted_items[0])}C list copied to clipboard", curses.color_pair(6))
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to clear the message

        def copy_selected_rows_to_clipboard():
            formatted_items = [[x for i, x in enumerate(item)] for j, item in enumerate(items) if selections[j]]  # Convert to Python list representation

            pyperclip.copy(repr(formatted_items))
            # stdscr.addstr(h - 2, 50, "Items copied to clipboard", curses.color_pair(6))
            stdscr.addstr(h - 2, 50, f"{len(formatted_items)}R,{len(formatted_items[0])}C list copied to clipboard", curses.color_pair(6))
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to clear the message

        def copy_selected_visible_rows_to_clipboard():
            formatted_items = [[x for i, x in enumerate(item) if i not in hidden_columns] for j, item in enumerate(items) if selections[j]]  # Convert to Python list representation

            pyperclip.copy(repr(formatted_items))
            # stdscr.addstr(h - 2, 50, f"{len(formatted_items)}R,{len(formatted_items[0])}C list copied to clipboard", curses.color_pair(6))
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to clear the message

        def delete_entries():
            nonlocal indexed_items, selections, items
            # Remove selected items from the list
            selected_indices = [index for index, selected in selections.items() if selected]
            if not selected_indices:
                # Remove the currently focused item if nothing is selected
                selected_indices = [indexed_items[cursor_pos][0]]

            items = [item for i, item in enumerate(items) if i not in selected_indices]
            indexed_items = [(i, item) for i, item in enumerate(items)]
            selections = {i:False for i in range(len(indexed_items))}
            draw_screen()


        def search(query, reverse=False, continue_search=False):
            nonlocal indexed_items, current_row, current_page, items_per_page, highlights, search_query, search_count, search_index, cursor_pos
            # Clear previous search highlights

            highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]

            def apply_filter(row):
                for col, value in filters.items():
                    if case_sensitive or (value != value.lower()):
                        pattern = re.compile(value)
                    else:
                        pattern = re.compile(value, re.IGNORECASE)
                    if col == -1:  # Apply filter to all columns
                        if not any(pattern.search(str(item)) for item in row):
                            return invert_filter
                        # return not invert_filter
                    elif col >= len(row) or col < 0:
                        return False
                    else:
                        cell_value = str(row[col])
                        if not pattern.search(str(cell_value)):
                            return invert_filter
                        # return invert_filter

                return True

            filters = {}
            invert_filter = False
            case_sensitive = False

            # tokens = re.split(r'(\s+--\d+|\s+--i)', query)
            tokens = re.split(r'((\s+|^)--\w)', query)
            tokens = [token.strip() for token in tokens if token.strip()]  # Remove empty tokens
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token:
                    if token.startswith("--"):
                        flag = token
                        if flag == '--v':
                            invert_filter = True 
                            i += 1
                        elif flag == '--i':
                            case_sensitive = True
                            i += 1
                        else:
                            if i+1 >= len(tokens):
                                print("Not enough args")
                                break
                            col = int(flag[2:])
                            arg = tokens[i+1].strip()
                            filters[col] = arg
                            i+=2
                            highlights.append({
                                "match": arg,
                                "field": col,
                                "color": 10,
                                "type": "search",
                            })
                    else:
                        filters[-1] = token
                        highlights.append({
                            "match": token,
                            "field": "all",
                            "color": 10,
                            "type": "search",
                        })
                        i += 1
                else:
                    i += 1

            before_count = len(indexed_items)

            # for i in list(range(current_row+(current_page*items_per_page)+1, len(indexed_items))) + list(range(current_row+(current_page*items_per_page)+1)):
            searchables =  list(range(cursor_pos+1, len(indexed_items))) + list(range(cursor_pos+1))
            if reverse:
                searchables =  ((list(range(cursor_pos), len(indexed_items))) + list(range(cursor_pos)))[::-1]
            # search_indices = list(range(old_pos+1, len(indexed_items))) + list(range(old_pos+1, len(indexed_items)))
            # for i in list(range(old_pos+1, len(indexed_items))):
            # os.system(f"notify-send '{len(indexed_items)}'")
            found = False
            search_count = 0
            search_list = []
            
            for i in searchables:
                # if apply_filter(indexed_items[i][1]):
                if apply_filter(indexed_items[i][1]):
                    new_pos = i
                    if new_pos in unselectable_indices: continue
                    search_count += 1
                    search_list.append(i)
                    
                    if not found:
                        current_pos = new_pos
                        found = True
                    # break
                    # return False
                    # for i in range(diff):
                    #     cursor_down()
                    # break
            if search_list:
                search_index = sorted(search_list).index(cursor_pos)+1
            else:
                search_index = 0

            # number_of_pages_before = (len(indexed_items) + items_per_page - 1) // items_per_page
            # indexed_items = [(i, item) for i, item in enumerate(items) if apply_filter(item)]
            # after_count = len(indexed_items)
            # number_of_pages_after = (len(indexed_items) + items_per_page - 1) // items_per_page
            # cursor = (current_page * items_per_page) + current_row
            # if cursor > after_count:
            #     cursor = 0
            #     # current_row = 0
            #     current_page  = number_of_pages_after - 1
            #     current_row = (len(indexed_items) +items_per_page - 1) % items_per_page

            draw_screen()

        def open_submenu(stdscr):
            nonlocal user_opts
            h, w = stdscr.getmaxyx()
            submenu_win = curses.newwin(6, 50, h // 2 - 2, w // 2 - 25)
            submenu_win.box()
            submenu_win.addstr(0, 2, "Select an option", curses.A_BOLD)
            submenu_items = ["green", "blue", "red", "purple", "orange", "gray"]
            current_submenu_row = 0
            submenu_page = 0
            items_per_page_submenu = 4
            total_pages_submenu = (len(submenu_items) + items_per_page_submenu - 1) // items_per_page_submenu

            while True:
                submenu_win.clear()
                submenu_win.box()
                submenu_win.addstr(0, 2, "Select an option", curses.A_BOLD)
                start = submenu_page * items_per_page_submenu
                end = min(start + items_per_page_submenu, len(submenu_items))

                for i in range(start, end):
                    if i == start + current_submenu_row:
                        submenu_win.addstr(i - start + 1, 2, f"> {submenu_items[i]}", curses.A_REVERSE)
                    else:
                        submenu_win.addstr(i - start + 1, 2, f"  {submenu_items[i]}")

                # Show page numbers
                submenu_win.addstr(4, 40, f"Page {submenu_page + 1}/{total_pages_submenu}", curses.color_pair(7))
                submenu_win.refresh()

                key = submenu_win.getch()

                if key == ord('j'):
                    if current_submenu_row < min(items_per_page_submenu - 1, len(submenu_items) - start - 1):
                        current_submenu_row += 1
                    elif submenu_page < total_pages_submenu - 1:
                        submenu_page += 1
                        current_submenu_row = 0

                elif key == ord('k'):
                    if current_submenu_row > 0:
                        current_submenu_row -= 1
                    elif submenu_page > 0:
                        submenu_page -= 1
                        current_submenu_row = items_per_page_submenu - 1

                elif key == ord('n'):
                    if submenu_page < total_pages_submenu - 1:
                        submenu_page += 1


                elif key == ord('p'):
                    if submenu_page > 0:
                        submenu_page -= 1

                elif key == 27:  # ESC key
                    break

                elif key == 10:  # Enter key
                    choice = submenu_items[start + current_submenu_row]
                    user_opts = user_opts + choice
                    stdscr.addstr(h - 1, 50, f"Selected: {choice}")
                    stdscr.refresh()
                    break

        def notification(stdscr, message="", duration=4):
            message = "hello there how are you today? you absolute orange chunkmuffin of a nignog"
            nonlocal user_opts
            h, w = stdscr.getmaxyx()
            submenu_win = curses.newwin(6, 40, 3, w - 44)
            submenu_win.box()
            submenu_win.addstr(0, 2, "Select an option", curses.A_BOLD)
            message_width = 32
            submenu_items = [message[i*message_width:(i+1)*message_width] for i in range(len(message)//message_width+1)]
            # submenu_items = ["green", "blue", "red", "purple", "orange", "gray"]
            current_submenu_row = 0
            submenu_page = 0
            items_per_page_submenu = 3
            total_pages_submenu = (len(submenu_items) + items_per_page_submenu - 1) // items_per_page_submenu

            while True:
                submenu_win.clear()
                submenu_win.box()
                # submenu_win.bkgd(curses.color_pair((1)))
                submenu_win.addstr(0, 2, "Notification:", curses.color_pair(5) | curses.A_BOLD)
                submenu_win.addstr(5, 2, "ESC, RET, q to dismiss", curses.color_pair(5) | curses.A_BOLD)
                start = submenu_page * items_per_page_submenu
                end = min(start + items_per_page_submenu, len(submenu_items))

                for i in range(start, end):
                    if i == start + current_submenu_row or True == True:
                        submenu_win.addstr(i - start + 1, 2, f"{submenu_items[i]}", curses.A_REVERSE)
                    else:
                        submenu_win.addstr(i - start + 1, 2, f"  {submenu_items[i]}")

                # Show page numbers
                submenu_win.addstr(5, 30, f"Page {submenu_page + 1}/{total_pages_submenu}", curses.color_pair(4))
                submenu_win.refresh()


                key = submenu_win.getch()

                if key == ord('j'):
                    if current_submenu_row < min(items_per_page_submenu - 1, len(submenu_items) - start - 1):
                        current_submenu_row += 1
                    elif submenu_page < total_pages_submenu - 1:
                        submenu_page += 1
                        current_submenu_row = 0

                elif key == ord('k'):
                    if current_submenu_row > 0:
                        current_submenu_row -= 1
                    elif submenu_page > 0:
                        submenu_page -= 1
                        current_submenu_row = items_per_page_submenu - 1

                elif key == ord('n'):
                    if submenu_page < total_pages_submenu - 1:
                        submenu_page += 1


                elif key == ord('p'):
                    if submenu_page > 0:
                        submenu_page -= 1

                if key in [10, 27, ord('q')]:  # Enter, escape or q
                    break

        def settings(prompt):
            nonlocal user_settings
            draw_screen()
            usrtxt = ""
            cursor = 0

            while True:
                # stdscr.addstr(curses.LINES - 2, 58, filter_query.ljust(curses.COLS - 8))
                filter_query = usrtxt
                stdscr.addstr(h - 1, 50, f" Settings: {usrtxt} ", curses.color_pair(13))
                if usrtxt and cursor != 0:
                    stdscr.addstr(h - 1, 50+len(usrtxt)-cursor+1+len("Settings: "), f"{usrtxt[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
                else:
                    stdscr.addstr(h - 1, 50-cursor+len(usrtxt)+1+len("Settings: "), f" ", curses.color_pair(13) | curses.A_REVERSE)
                # stdscr.refresh()
                key = stdscr.getch()
                # os.system(f'notify-send "{key}"')
                if key == 27 or key == "^":  # ESC key
                    # filter_query = ""
                    draw_screen()
                    break
                elif key == curses.KEY_BACKSPACE or key == "KEY_BACKSPACE":
                    if cursor == 0:
                        usrtxt = usrtxt[:-1]
                    else:
                        usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]
                elif key == curses.KEY_LEFT:
                    cursor = min(len(usrtxt), cursor + 1)
                elif key == curses.KEY_RIGHT:
                    cursor = max(0, cursor - 1)
                elif key == curses.KEY_UP:
                    cursor = max(0, cursor - 1)
                elif key == 21 or key == "^U": ## CTRL+U
                    usrtxt = ""
                    cursor = 0
                elif key == 1: ## CTRL+A (beginning)
                    cursor = len(usrtxt)
                elif key == 5: ## CTRL+E (end)
                    cursor = 0
                elif key in [10, curses.KEY_ENTER]:  # Enter key
                    # filter_items(filter_query.strip())
                    user_settings += usrtxt
                    apply_settings()
                    break
                else:
                    if isinstance(key, int):
                        try:
                            val = chr(key) if chr(key).isprintable() else ''
                        except:
                            val = ''
                    else: val = key
                    if cursor == 0:
                        usrtxt += val
                    else:
                        usrtxt = usrtxt[:-cursor] + val + usrtxt[-cursor:]
                draw_screen()
            
        
        def toggle_column_visibility(col_index):
            if 0 <= col_index < len(items[0]):
                if col_index in hidden_columns:
                    hidden_columns.remove(col_index)
                else:
                    hidden_columns.add(col_index)

        def apply_settings():
            
            nonlocal user_settings, highlights, sort_column, current_page, current_row, cursor_pos
            # settings= usrtxt.split(' ')
            # split settings and appy them
            """
            ![0-9]+ show/hide column
            s[0-9]+ set column focus for sort
            g[0-9]+ go to index
            p[0-9]+ go to page
            nohl    hide search highlights
            """
            if user_settings:
                settings = re.split(r'\s+', user_settings)
                for setting in settings:
                    if len(setting) == 0: continue
                    if setting[0] == "!":
                        cols = setting[1:].split(",")
                        for col in cols:
                            toggle_column_visibility(int(col))
                    elif setting in ["nhl", "nohl", "nohighlights"]:
                        highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]
                    elif setting[0] == "s":
                        if 0 <= int(setting[1:]) < len(items[0]):
                            sort_column = int(setting[1:])
                            current_pos = indexed_items[cursor_pos][0]
                            sort_items(indexed_items, sort_method=sort_method, sort_column=sort_column, sort_reverse=sort_reverse)  # Re-sort items based on new column
                            new_pos = [row[0] for row in indexed_items].index(current_pos)
                            cursor_pos = new_pos
                    elif setting[0] == "":
                        cols = setting[1:].split(",")
                        for col in cols:
                            toggle_column_visibility(int(col))

                user_settings = ""
        def append_additional_text(prompt):
            nonlocal user_opts
            draw_screen()
            usrtxt = ""
            cursor = 0

            while True:
                # stdscr.addstr(curses.LINES - 2, 58, filter_query.ljust(curses.COLS - 8))
                filter_query = usrtxt
                # stdscr.addstr(h - 1, 50, "Opts: " + usrtxt, curses.color_pair(6))
                stdscr.addstr(h - 1, 50, f" Opts: {usrtxt} ", curses.color_pair(13))
                if usrtxt and cursor != 0:
                    stdscr.addstr(h - 1, 50+len(usrtxt)-cursor+1+len("Opts: "), f"{usrtxt[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
                else:
                    stdscr.addstr(h - 1, 50-cursor+len(usrtxt)+1+len("Opts: "), f" ", curses.color_pair(13) | curses.A_REVERSE)
                # stdscr.refresh()
                key = stdscr.getch()
                if key == 27 or key == "^":  # ESC key
                    # filter_query = ""
                    draw_screen()
                    break
                elif key in [10, curses.KEY_ENTER]:  # Enter key
                    # filter_items(filter_query.strip())
                    user_opts += usrtxt
                    break
                elif key == curses.KEY_BACKSPACE or key == "KEY_BACKSPACE":
                    if cursor == 0:
                        usrtxt = usrtxt[:-1]
                    else:
                        usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]
                elif key == curses.KEY_LEFT:
                    cursor = min(len(usrtxt), cursor + 1)
                elif key == curses.KEY_RIGHT:
                    cursor = max(0, cursor - 1)
                elif key == curses.KEY_UP:
                    cursor = max(0, cursor - 1)
                elif key == 4: # Ctrl+D
                    usrtxt = usrtxt[:cursor] + usrtxt[cursor+1:]
                    cursor = max(0, cursor - 1)
                elif key == 21 or key == "^U": ## CTRL+U
                    usrtxt = ""
                    cursor = 0
                elif key == 1: ## CTRL+A (beginning)
                    cursor = len(usrtxt)
                elif key == 5: ## CTRL+E (end)
                    cursor = 0
                else:
                    if isinstance(key, int):
                        try:
                            val = chr(key) if chr(key).isprintable() else ''
                        except:
                            val = ''
                    else: val = key
                    if cursor == 0:
                        usrtxt += val
                    else:
                        usrtxt = usrtxt[:-cursor] + val + usrtxt[-cursor:]
                draw_screen()

        # Function to display the help screen
        def show_help():
            help_text = (
                "List Picker Help\n\n"
                "Navigation:\n"
                "  Up/Down or k/j    - Move up/down\n"
                "  p/n               - Previous/Next page\n"
                "  P/N               - First/Last page\n"
                "  g or home         - Go to top of page\n"
                "  G or end          - Go to bottom of page\n"
                "\n"
                "Selection:\n"
                "  Space             - Toggle selection\n"
                "  m or C-a          - Select all\n"
                "  M or C-r          - Deselect all\n"
                "  v                 - Start and stop visual selection\n"
                "  V                 - Start and stop visual deselection\n"
                "  l/Enter           - Submit selection\n"
                "\n"
                "Sorting:\n"
                "  1-9               - Select column (1-based index)\n"
                "  s                 - Cycle sort method\n"
                "  t                 - Toggle sort order\n"
                "\n"
                "Filter or search rows (regexp):\n"
                "  f                 - Begin filtering rows\n"
                "  /                 - Begin searching rows\n"
                "      --[1-9]       - Specify column\n"
                "      --i           - Make match case sensitive\n"
                "      --v           - Invert filter\n"

                "Columns:\n"
                "  Shift+1-9         - Hide/show column\n"
                "  [/]               - Increase/Decrease column width\n"
                "  {                 - Move column left\n"
                "  }                 - Move column right\n"
                "\n"

                "Clipboard:\n"
                "  y                 - Copy selected indices to clipboard (tsv)\n"
                "  Y                 - Copy visible parts of selected indices to clipboard (tsv)\n"
                "  c                 - Copy selected entries to clipboard (python list)\n"
                "\n"
                "Misc:\n"
                "  ?                 - Show this help screen\n"
                "  :                 - Specify user optios to be returned with selection\n"
                "  `                 - Specify display option\n"
               r"      !\d+          - Show/hide column"
                "\n"
               r"  \                 - Clear user options\n"
                "  q                 - Exit without selection\n"
                "  o                 - Open submenu\n"
                "  +                 - Increase lines per page\n"
                "  -                 - Decrease lines per page\n"
                "  -                 - Decrease lines per page\n"
            )
            help_lines = help_text.split('\n')
            indexed_help_lines = enumerate(help_text)
            help_page = 0
            line_num = 0

            while True:
                total_pages = (len(help_lines) + items_per_page - 1) // items_per_page
                # stdscr.clear()
                h, w = stdscr.getmaxyx()
                
                start_line = help_page * items_per_page + line_num
                end_line = min(start_line + items_per_page, len(help_lines))
                
                # Print help text for the current page
                for i in range(start_line, end_line):
                    stdscr.addstr(i - start_line, 0, help_lines[i])

                # Display page number and count
                stdscr.addstr(h - 2, 0, f"Help Page {help_page + 1}/{total_pages}", curses.color_pair(3))
                
                stdscr.refresh()
                key = stdscr.getch()

                if key == ord('q') or key == 27:
                    break
                if key == ord('j') or key == curses.KEY_DOWN:
                    if line_num + items_per_page*(help_page+1) < len(help_lines):
                        line_num = (line_num + 1) % items_per_page
                        if line_num == 0: help_page += 1
                    stdscr.clear()
                    stdscr.refresh()
                if key == ord('k') or key == 259:
                    if line_num > 0: line_num -= 1
                    if line_num == 0 and help_page > 0:
                        line_num = items_per_page-1
                        help_page -= 1
                    stdscr.clear()
                    stdscr.refresh()

                elif key == 12:  # Ctrl-l, ^l
                    stdscr.clear()
                    stdscr.refresh()

                elif key == ord('n'):  # Next page
                    if help_page < total_pages - 1:
                        help_page += 1
                    line_num = 0
                    stdscr.clear()
                    stdscr.refresh()
                elif key == ord('p'):  # Previous page
                    if help_page > 0:
                        help_page -= 1
                    line_num = max(0, line_num - items_per_page)
                    stdscr.clear()
                    stdscr.refresh()
                elif key == ord('g'):

                    help_page = 0
                    line_num = 0
                    stdscr.clear()
                    stdscr.refresh()
                elif key == ord('G'):
                    help_page = total_pages-1
                        
                    line_num = 0
                    stdscr.clear()
                    stdscr.refresh()

        def format_full_row(row):
            return '\t'.join(row)

        # Function to draw the screen

        # Functions for item selection
        def toggle_item(index):
            selections[index] = not selections[index]
            draw_screen()

        def select_all():
            for i in range(len(indexed_items)):
                selections[indexed_items[i][0]] = True
            draw_screen()

        def deselect_all():
            for i in range(len(selections)):
                selections[i] = False
            draw_screen()

        def handle_visual_selection(selecting=True):
            nonlocal start_selection, end_selection, is_selecting, is_deselecting, cursor_pos
            if not is_selecting and not is_deselecting:
                # start_selection = indexed_items[current_page * items_per_page + current_row][0]
                start_selection = cursor_pos
                if selecting:
                    is_selecting = True
                else:
                    is_deselecting = True
            elif is_selecting:
                # end_selection = indexed_items[current_page * items_per_page + current_row][0]
                end_selection = cursor_pos
                if start_selection is not None:
                    start = min(start_selection, end_selection)
                    end = max(start_selection, end_selection)
                    for i in range(start, end + 1):
                        if indexed_items[i][0] not in unselectable_indices:
                            selections[indexed_items[i][0]] = True
                start_selection = None
                end_selection = None
                is_selecting = False
                draw_screen()
            elif is_deselecting:
                end_selection = indexed_items[cursor_pos][0]
                end_selection = cursor_pos
                if start_selection is not None:
                    start = min(start_selection, end_selection)
                    end = max(start_selection, end_selection)
                    for i in range(start, end + 1):
                        # selections[i] = False
                        selections[indexed_items[i][0]] = False
                start_selection = None
                end_selection = None
                is_deselecting = False
                draw_screen()

        # esc = False
        draw_screen()
        # Main loop
        
        while True:
            key = stdscr.getch()
            # os.system(f"notify-send '2'")
            
            # time.sleep(random.uniform(0.05, 0.1))
            # os.system(f"notify-send 'Timer {timer}'")
            # if timer:
                # os.system(f"notify-send '{time.time() - initial_time}, {timer} {bool(timer)}, {time.time() - initial_time > timer}'")
            if (timer and (time.time() - initial_time) > timer):
                stdscr.clear()
                if get_new_data and refresh_function:
                    # f = refresh_function[0]
                    # args = refresh_function[1]
                    # kwargs = refresh_function[2]
                    # items = f(*args, **kwargs)
                    items, header = refresh_function()


                
                function_data = get_function_data()
                return [], "refresh", function_data

            def cursor_down():
                # Returns: whether page is turned
                nonlocal cursor_pos
                new_pos = cursor_pos + 1
                while True:
                    if new_pos >= len(indexed_items): return False
                    if indexed_items[new_pos][0] in unselectable_indices: new_pos+=1
                    else: break
                cursor_pos = new_pos
                return True
                # elif current_page < (len(indexed_items) + items_per_page - 1) // items_per_page - 1:

            # def cursor_down_old():
            #     # Returns: whether page is turned
            #     nonlocal current_row, current_page
            #     if current_row < items_per_page - 1 and current_row + (current_page * items_per_page) < len(indexed_items) - 1:
            #         current_row += 1
            #     elif current_row == items_per_page - 1 and current_page < (len(indexed_items) + items_per_page - 1) // items_per_page - 1:
            #         current_page += 1
            #         current_row = 0
            #         return True
            #     return False
            def cursor_up():
                # Returns: whether page is turned
                nonlocal cursor_pos
                new_pos = cursor_pos - 1
                while True:
                    if new_pos < 0: return False
                    elif new_pos in unselectable_indices: new_pos -= 1
                    else: break
                cursor_pos = new_pos
                return True
            # def cursor_up_old():
            #     # Returns: whether page is turned
            #     nonlocal current_row, current_page
            #     if current_row > 0:
            #         current_row -= 1
            #     elif current_page > 0:
            #         current_page -= 1
            #         current_row = items_per_page - 1
            #         return True
            #     return False
            clear_screen=True
            if key == ord('?'):
                stdscr.clear()
                stdscr.refresh()
                show_help()
            # elif key == ord('['):
            #     max_width -= 10
            # elif key == ord(']'):
            #     if max_width > 10:
            #         max_width += 10
            elif key in [ord('q'), ord('h')]:
                stdscr.clear()
                # stdscr.addstr(0, 0, "Exited without selection.")
                # stdscr.refresh()
                # stdscr.getch()  # Wait for a key press before closing
                function_data = get_function_data()
                return [], "", function_data
            elif key == ord('`'):
                settings('')
            elif key == ord('{'):
                move_column(-1)

            elif key == ord('}'):
                move_column(1)
            elif key in [curses.KEY_DOWN, ord('j')]:
                page_turned = cursor_down()
                if not page_turned: clear_screen = False
            elif key == ord('d'):
                clear_screen = False
                for i in range(items_per_page//2): 
                    if cursor_down(): clear_screen = True
            elif key == ord('J'):
                clear_screen = False
                for i in range(5): 
                    if cursor_down(): clear_screen = True
            elif key in [curses.KEY_UP, ord('k')]:
                page_turned = cursor_up()
                if not page_turned: clear_screen = False
            elif key == ord('K'):
                clear_screen = False
                for i in range(5): 
                    if cursor_up(): clear_screen = True
            elif key == ord('u'):
                clear_screen = False
                for i in range(items_per_page//2): 
                    if cursor_up(): clear_screen = True
            elif key == ord(' '): # Space key
                if len(indexed_items) > 0:
                    item_index = indexed_items[cursor_pos][0]
                    selected_count = sum(selections.values())
                    if max_selected == None or selected_count >= max_selected:
                        toggle_item(item_index)
                cursor_down()
            elif key == ord('m') or key == 1:  # Select all (m or ctrl-a)
                select_all()
            elif key == ord('M') or key == 18:  # Deselect all (M or ctrl-r)
                deselect_all()
            # elif key == ord('g') or key == curses.KEY_HOME:
            #     current_row = 0
            #     draw_screen()
            elif key == ord('g') or key == curses.KEY_HOME:
                # current_row = 0
                new_pos = 0
                while True:
                    if new_pos in unselectable_indices: new_pos+=1
                    else: break
                if new_pos < len(indexed_items):
                    cursor_pos = new_pos

                draw_screen()

            elif key == ord('G') or key == curses.KEY_END:
                new_pos = len(indexed_items)-1
                while True:
                    if new_pos in unselectable_indices: new_pos-=1
                    else: break
                if new_pos < len(items) and new_pos >= 0:
                    cursor_pos = new_pos
                draw_screen()
                # current_row = items_per_page - 1
                # if current_page + 1 == (len(indexed_items) + items_per_page - 1) // items_per_page:
                #
                #     current_row = (len(indexed_items) +items_per_page - 1) % items_per_page
                # draw_screen()
            elif key in [curses.KEY_ENTER, ord('\n'), ord('l')]:
                # Print the selected indices if any, otherwise print the current index
                if is_selecting or is_deselecting: handle_visual_selection()
                if len(indexed_items) == 0:
                    function_data = get_function_data()
                    return [], "", function_data
                selected_indices = print_selected_indices()
                if not selected_indices:
                    selected_indices = [indexed_items[cursor_pos][0]]
                
                option_required = False
                for index in selected_indices:
                    if require_option[index]:
                        option_required = True
                        # notification(stdscr, message=f"opt required for {index}")
                        append_additional_text("")

                stdscr.clear()
                # stdscr.addstr(0, 0, "Selected indices: " + str(selected_indices))
                stdscr.refresh()
                # stdscr.getch()  # Wait for a key press before closing
                # return selected_indices
                # NOW RETURNING SELECTED INDICES AND OPTIONS
                function_data = get_function_data()
                return selected_indices, user_opts, function_data
            elif key == ord('n') or key == curses.KEY_NPAGE:  # Next page
                cursor_pos = min(len(indexed_items) - 1, cursor_pos+items_per_page)

            elif key == ord('p')  or key == curses.KEY_PPAGE:  # Previous page
                cursor_pos = max(0, cursor_pos-items_per_page)

            elif key == 12:  # Ctrl-l, ^l
                stdscr.clear()
                stdscr.refresh()

            elif key == ord('s'):  # Cycle sort method
                sort_method = (sort_method+1) % len(SORT_METHODS)
                current_index = indexed_items[cursor_pos][0]
                sort_items(indexed_items, sort_method=sort_method, sort_column=sort_column, sort_reverse=sort_reverse)  # Re-sort items based on new column
                cursor_pos = [row[0] for row in indexed_items].index(current_index)
            elif key == ord('S'):  # Cycle sort method
                sort_method = (sort_method-1) % len(SORT_METHODS)
                current_index = indexed_items[cursor_pos][0]
                sort_items(indexed_items, sort_method=sort_method, sort_column=sort_column, sort_reverse=sort_reverse)  # Re-sort items based on new column
                cursor_pos = [row[0] for row in indexed_items].index(current_index)
            elif key == ord('t'):  # Toggle sort order
                sort_reverse = not sort_reverse
                current_index = indexed_items[cursor_pos][0]
                sort_items(indexed_items, sort_method=sort_method, sort_column=sort_column, sort_reverse=sort_reverse)  # Re-sort items based on new column
                cursor_pos = [row[0] for row in indexed_items].index(current_index)
            elif key in [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')]:
                col_index = key - ord('0')
                if 0 <= col_index < len(items[0]):
                    sort_column = col_index
                    current_index = indexed_items[cursor_pos][0]
                    sort_items(indexed_items, sort_method=sort_method, sort_column=sort_column, sort_reverse=sort_reverse)  # Re-sort items based on new column
                    cursor_pos = [row[0] for row in indexed_items].index(current_index)
            elif key in [ord('!'), ord('@'), ord('#'), ord('$'), ord('%'), ord('^'), ord('&'), ord('*'), ord('('), ord(')')]:
                d = {'!': 0, '@': 1, '#': 2, '$': 3, '%': 4, '^': 5, '&': 6, '*': 7, '(': 8, ')': 9}
                d = {s:i for i,s in enumerate(")!@#$%^&*(")}
                col_index = d[chr(key)]
                toggle_column_visibility(col_index)
            # elif key == ord('i'):  # Copy selected indices to clipboard
            #     copy_indices()
            elif key == ord('Y'):  # Copy (visible) selected values to clipboard
                copy_values()
            elif key == ord('y'):  # Copy full values of selected entries to clipboard
                copy_full_values()
            elif key == ord('c'):
                copy_selected_visible_rows_to_clipboard()
            elif key == ord('C'):
                # copy_items_to_clipboard()
                copy_selected_rows_to_clipboard()
            elif key == curses.KEY_DC:  # Delete key
                delete_entries()
            elif key == ord('+'):  # Increase lines per page
                items_per_page += 1
                draw_screen()
            elif key == ord('-'):  # Decrease lines per page
                if items_per_page > 1:
                    items_per_page -= 1
                draw_screen()
            elif key == ord('['):
                if max_width > 10:
                    max_width -= 10
                    column_widths[:] = get_column_widths(items, header=header, max_width=max_width, number_columns=number_columns)
                    draw_screen()
            elif key == ord('v'):
                handle_visual_selection()
                draw_screen()

            elif key == ord('V'):
                handle_visual_selection(selecting=False)
                draw_screen()
            if key == curses.KEY_RESIZE:  # Terminal resize signal
                # if curses.is_term_resized()
                # os.system(f"notify-send '{h}, {w}'")
                h, w = stdscr.getmaxyx()
                # os.system(f"notify-send '{h}, {w}'")
                top_space = top_gap
                if title: top_space+=1
                if display_modes: top_space+=1
                items_per_page = os.get_terminal_size().lines - top_space*2-2-int(bool(header))

            elif key == ord('r'):
                top_space = top_gap
                if title: top_space+=1
                if display_modes: top_space+=1
                items_per_page = os.get_terminal_size().lines - top_space*2-2-int(bool(header))
                # if current_page + 1 > (len(indexed_items) + items_per_page - 1) // items_per_page:
                #     current_page = (len(indexed_items) + items_per_page - 1) // items_per_page - 1
                #     current_row = (len(indexed_items) +items_per_page - 1) % items_per_page
                stdscr.refresh()


            elif key == ord('f'):
                # filter_query = ""
                draw_screen()
                usrtxt = f" {filter_query}"
                cursor = len(filter_query)
                # stdscr.addstr(curses.LINES - 2, 8, " " * (curses.COLS - 8))  # Clear line

                # curses.echo()
                # filter_query = stdscr.getstr(curses.LINES - 2, 58).decode("utf-8")
                # curses.noecho()
                # filter_items(filter_query)
                while True:
                    # stdscr.addstr(curses.LINES - 2, 58, filter_query.ljust(curses.COLS - 8))
                    stdscr.addstr(h - 2, 50, f" Filter: {filter_query} ", curses.color_pair(13))
                    if filter_query and cursor != 0:
                        stdscr.addstr(h - 2, 50+len(filter_query)-cursor+1+len("Filter: "), f"{filter_query[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
                    else:
                        stdscr.addstr(h - 2, 50-cursor+len(filter_query)+1+len("Filter: "), f" ", curses.color_pair(13) | curses.A_REVERSE)
                    # stdscr.refresh()
                    key = stdscr.getch()
                    if key == 27:  # ESC key
                        filter_query = ""
                        draw_screen()
                        break
                    elif key == 10:  # Enter key
                        filter_query = filter_query
                        if "filter" in modes[mode_index] and modes[mode_index]["filter"] not in filter_query:
                            mode_index = 0
                        # elif "filter" in modes[mode_index] and modes[mode_index]["filter"] in filter_query:
                        #     filter_query.split(modes[mode_index]["filter"])

                        prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
                        indexed_items = filter_items(items, indexed_items, filter_query)
                        if prev_index in [x[0] for x in indexed_items]: new_index = [x[0] for x in indexed_items].index(prev_index)
                        else: new_index = 0
                        cursor_pos = new_index
                        break
                    elif key == curses.KEY_BACKSPACE or key == "KEY_BACKSPACE":
                        if cursor == 0:
                            filter_query = filter_query[:-1]
                        else:
                            filter_query = filter_query[:-(cursor+1)] + filter_query[-cursor:]
                    elif key == curses.KEY_LEFT:
                        cursor = min(len(filter_query), cursor + 1)
                    elif key == curses.KEY_RIGHT:
                        cursor = max(0, cursor - 1)
                    elif key == curses.KEY_UP:
                        cursor = max(0, cursor - 1)
                    elif key == 21 or key == "^U": ## CTRL+U
                        filter_query = ""
                        cursor = 0
                    elif key == 1: ## CTRL+A (beginning)
                        cursor = len(filter_query)
                    elif key == 5: ## CTRL+E (end)
                        cursor = 0
                    else:
                        if isinstance(key, int):
                            try:
                                val = chr(key) if chr(key).isprintable() else ''
                            except:
                                val = ''
                        else: val = key
                        if cursor == 0:
                            filter_query += val
                        else:
                            filter_query = filter_query[:-cursor] + val + filter_query[-cursor:]
                    draw_screen()
            elif key == ord('/'):
                search_query = ""
                draw_screen()
                cursor = 0
                usrtxt = ""
                # stdscr.addstr(curses.LINES - 2, 8, " " * (curses.COLS - 8))  # Clear line

                curses.noecho()
                # filter_query = stdscr.getstr(curses.LINES - 2, 58).decode("utf-8")
                # curses.noecho()
                # filter_items(filter_query)
                while True:
                    # stdscr.addstr(curses.LINES - 2, 58, filter_query.ljust(curses.COLS - 8))
                    stdscr.addstr(h - 3, 50, f" Search: {usrtxt} ", curses.color_pair(13))
                    if usrtxt and cursor != 0:
                        stdscr.addstr(h - 3, 50+len(usrtxt)-cursor+1+len("Search: "), f"{usrtxt[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
                    else:
                        stdscr.addstr(h - 3, 50-cursor+len(usrtxt)+1+len("Search: "), f" ", curses.color_pair(13) | curses.A_REVERSE)
                    # stdscr.refresh()
                    key = stdscr.getch()
                    if key == 27:  # ESC key
                        usrtxt = ""
                        draw_screen()
                        break
                    elif key == 10:  # Enter key
                        search_query = usrtxt
                        search(usrtxt.strip())
                        break
                    elif key == curses.KEY_BACKSPACE or key == "KEY_BACKSPACE":
                        if cursor == 0:
                            usrtxt = usrtxt[:-1]
                        else:
                            usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]
                    elif key == curses.KEY_LEFT:
                        cursor = min(len(usrtxt), cursor + 1)
                    elif key == curses.KEY_RIGHT:
                        cursor = max(0, cursor - 1)
                    elif key == curses.KEY_UP:
                        cursor = max(0, cursor - 1)
                    elif key == 21 or key == "^U": ## CTRL+U
                        usrtxt = ""
                        cursor = 0
                    elif key == 1: ## CTRL+A (beginning)
                        cursor = len(usrtxt)
                    elif key == 5: ## CTRL+E (end)
                        cursor = 0
                    else:
                        if isinstance(key, int):
                            try:
                                val = chr(key) if chr(key).isprintable() else ''
                            except:
                                val = ''
                        else: val = key
                        if cursor == 0:
                            usrtxt += val
                        else:
                            usrtxt = usrtxt[:-cursor] + val + usrtxt[-cursor:]
                    draw_screen()
            elif key == ord('i'):
                search(search_query.strip(), continue_search=True)
            elif key == ord('I'):
                search(search_query.strip(), reverse=True, continue_search=True)
            elif key == 27 or key == ord('e'):  # ESC key
                # order of escapes:
                # 1. selecting/deslecting
                # 2. search
                # 3. filter
                # 4. selecting
                # nonlocal highlights

                if is_selecting or is_deselecting:
                    start_selection = None
                    end_selection = None
                    is_selecting = False
                    is_deselecting = False
                elif search_query:
                    search_query = ""
                    highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]
                elif filter_query:
                    if "filter" in modes[mode_index] and modes[mode_index]["filter"] in filter_query and filter_query.strip() != modes[mode_index]["filter"]:
                        filter_query = modes[mode_index]["filter"]
                    # elif "filter" in modes[mode_index]:
                    else:
                        filter_query = ""
                        mode_index = 0
                    prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
                    indexed_items = filter_items(items, indexed_items, filter_query)
                    if prev_index in [x[0] for x in indexed_items]: new_index = [x[0] for x in indexed_items].index(prev_index)
                    else: new_index = 0
                    cursor_pos = new_index

                else:
                    search_query = ""
                    mode_index = 0
                    highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]
                    # esc = True
                    continue
                draw_screen()
            # elif esc and key == ord('j'):
            #     for i in range(5): cursor_down()
            # elif esc and key == ord('k'):
            #     for i in range(5): cursor_up()
            elif key == ord(':'):
                append_additional_text('')
            elif key == ord('o'):
                open_submenu(stdscr)
            elif key == ord('z'):
                notification(stdscr)
            elif key == 9: # tab key
                # apply setting 
                prev_mode_index = mode_index
                mode_index = (mode_index+1)%len(modes)
                mode = modes[mode_index]
                for key, val in mode.items():
                    if key == 'filter':
                        if 'filter' in modes[prev_mode_index]:
                            filter_query = filter_query.replace(modes[prev_mode_index]['filter'], '')
                        filter_query = f"{filter_query.strip()} {val.strip()}".strip()
                        prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0

                        indexed_items = filter_items(items, indexed_items, filter_query)
                        if prev_index in [x[0] for x in indexed_items]: new_index = [x[0] for x in indexed_items].index(prev_index)
                        else: new_index = 0
                        cursor_pos = new_index
            elif key == 353: # shift+tab key
                # apply setting 
                prev_mode_index = mode_index
                mode_index = (mode_index-1)%len(modes)
                mode = modes[mode_index]
                for key, val in mode.items():
                    if key == 'filter':
                        if 'filter' in modes[prev_mode_index]:
                            filter_query = filter_query.replace(modes[prev_mode_index]['filter'], '')
                        filter_query = f"{filter_query.strip()} {val.strip()}".strip()
                        prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
                        indexed_items = filter_items(items, indexed_items, filter_query)
                        if prev_index in [x[0] for x in indexed_items]: new_index = [x[0] for x in indexed_items].index(prev_index)
                        else: new_index = 0
                        cursor_pos = new_index
            elif key == ord('|'):
                pipe_to_command()
            elif key == ord("\\"):
                user_opts = ""
            elif key == ord(']'):
                if max_width < 300:
                    max_width += 10
                    column_widths[:] = get_column_widths(items, header=header, max_width=max_width, number_columns=number_columns)
                    draw_screen()
            # esc = False
            draw_screen(clear_screen)

    # Use curses.wrapper to handle initialization and cleanup
    # return curses.wrapper(main)
    return main()

# Example usage
if __name__ == "__main__":
    is_selecting = False
    is_deselecting = False
    # List of lists example
    items = [
        ["Title 1", "32 MB", "10 Files"],
        ["Title 2", "12 GB", "12 Files"],
        ["Title 3", "2 KB", "1 Files"],
        ["Title 4", "500 B", "8 Files"],
        ["Title 5", "1.5 MB/s", "5 Files"],
        ["Title 6", "300 KBps", "15 Files"]
    ]

    # Define custom colors
    custom_colors = {
        'background': curses.COLOR_BLACK,
        'normal_fg': curses.COLOR_WHITE,
        'unselected_fg': curses.COLOR_WHITE,
        'unselected_bg': curses.COLOR_BLACK,
        'selected_fg': curses.COLOR_BLACK,
        'selected_bg': curses.COLOR_YELLOW
    }

    # Optional header row
    header_row = ["Title", "Size", "Files"]

    items = [
        ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaTitle 1", "32.3 MB", "10 Files", "5KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 2", "12.3 MB", "12 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 3", "2.3 MB", "40 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 4", "2.3 KB", "5 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 5", "9.3 MB", "5 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 6", "2.3 MB", "13 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 7", "8.3 MB", "1 Files", "14GBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 8", "2.3 GB", "3 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 9", "2.2 MB", "5 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 10", "2.0 MB", "23 Files", "8MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 11", "2.3 MB", "1 Files", "17MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 12", "12.8 MB", "4 Files", "14MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 13", "82.1 MB", "3 Files", "3MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 14", "32.3 MB", "33 Files", "12GBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 15", "2.3 MB", "1 Files", "23MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 16", "82.13 MB", "2 Files", "25MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 17", "322.3 MB", "1 Files", "89KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 18", "102.0 MB", "6 Files", "26MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 19", "2.3 MB", "11 Files", "21MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 20", "5.1 MB", "2 Files", "9KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 21", "6.2 MB", "13 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 22", "22.1 MB", "5 Files", "31KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 23", "0.8 MB", "51 Files", "42MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
    ]

    # Define custom colors
    custom_colors = {
        'background': curses.COLOR_BLACK,
        'normal_fg': curses.COLOR_WHITE,
        'unselected_fg': curses.COLOR_WHITE,
        'cursor_fg': curses.COLOR_WHITE,
        'selected_fg': curses.COLOR_BLACK,
        'header_fg': curses.COLOR_BLACK,
        'unselected_bg': curses.COLOR_BLACK,
        'selected_bg': curses.COLOR_BLUE,
        'cursor_bg': curses.COLOR_BLUE,
        'header_bg': curses.COLOR_WHITE,
    }
    custom_colors2 = {
        'background': curses.COLOR_WHITE,
        'normal_fg': curses.COLOR_BLACK,
        'unselected_fg': curses.COLOR_BLACK,
        'cursor_fg': curses.COLOR_WHITE,
        'selected_fg': curses.COLOR_BLACK,
        'header_fg': curses.COLOR_WHITE,
        'unselected_bg': curses.COLOR_WHITE,
        'selected_bg': curses.COLOR_BLUE,
        'cursor_bg': curses.COLOR_BLUE,
        'header_bg': curses.COLOR_BLACK
    }
    items = [

            ]

    # Optional header row
    header_row = ["Title", "Size", "Files", "a"]
    # header_row = ["Title", "Size", "Files"]
    # header_row = ["(1) url", "(2) title", "(3) info"]
    # header_row = ["1. url", "2. title", "3. info"]
    # Run the list picker
    # selected_indices = list_picker(items, custom_colors, top_gap=0, header=header_row, max_width=70)
    # print("Final selected indices:", selected_indices)

# Example usage
if __name__ == "__main__":
    is_selecting = False
    is_deselecting = False
    # List of lists example
    items = [
        ["Title 1", "32 MB", "10 Files"],
        ["Title 2", "12 GB", "12 Files"],
        ["Title 3", "2 KB", "1 Files"],
        ["Title 4", "500 B", "8 Files"],
        ["Title 5", "1.5 MB/s", "5 Files"],
        ["Title 6", "300 KBps", "15 Files"]
    ]

    # Define custom colors
    custom_colors = {
        'background': curses.COLOR_BLACK,
        'normal_fg': curses.COLOR_WHITE,
        'unselected_fg': curses.COLOR_WHITE,
        'unselected_bg': curses.COLOR_BLACK,
        'selected_fg': curses.COLOR_BLACK,
        'selected_bg': curses.COLOR_YELLOW
    }

    # Optional header row
    header_row = ["Title", "Size", "Files"]

    items = [
        ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaTitle 1", "32.3 MB", "10 Files", "5KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 2", "12.3 MB", "12 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 3", "2.3 MB", "40 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 4", "2.3 KB", "5 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 5", "9.3 MB", "5 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 6", "2.3 MB", "13 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 7", "8.3 MB", "1 Files", "14GBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 8", "2.3 GB", "3 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 9", "2.2 MB", "5 Files", "15MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 10", "2.0 MB", "23 Files", "8MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 11", "2.3 MB", "1 Files", "17MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 12", "12.8 MB", "4 Files", "14MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 13", "82.1 MB", "3 Files", "3MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 14", "32.3 MB", "33 Files", "12GBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 15", "2.3 MB", "1 Files", "23MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 16", "82.13 MB", "2 Files", "25MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 17", "322.3 MB", "1 Files", "89KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 18", "102.0 MB", "6 Files", "26MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 19", "2.3 MB", "11 Files", "21MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 20", "5.1 MB", "2 Files", "9KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 21", "6.2 MB", "13 Files", "12MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 22", "22.1 MB", "5 Files", "31KBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
        ["Title 23", "0.8 MB", "51 Files", "42MBps", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"],
    ]

    # Optional header row
    header_row = ["Title", "Size", "Files", "a"]
    header_row = ["Title", "Size", "Files"]
    # header_row = ["(1) url", "(2) title", "(3) info"]
    # header_row = ["1. url", "2. title", "3. info"]
    # Run the list picker
    # selected_indices = list_picker(items, custom_colors, top_gap=0, header=header_row, max_width=70)
    # print("Final selected indices:", selected_indices)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert table to list of lists.')
    parser.add_argument('-i', dest='file', help='File containing the table to be converted')
    parser.add_argument('--stdin', action='store_true', help='Table passed on stdin')
    parser.add_argument('--stdin2', action='store_true', help='Table passed on stdin')
    parser.add_argument('-d', dest='delimiter', default='\t', help='Delimiter for rows in the table (default: tab)')
    parser.add_argument('-t', dest='file_type', choices=['tsv', 'csv', 'json', 'xlsx', 'ods'], help='Type of file (tsv, csv, json, xlsx, ods)')
    args = parser.parse_args()
    
    if args.file:
        input_arg = args.file
    elif args.stdin:
        input_arg = '--stdin'
    elif args.stdin2:
        input_arg = '--stdin2'
    else:
        print("Error: Please provide input file or use --stdin option.")
        return None, None
        # sys.exit(1)
    
    table_data = table_to_list(input_arg, args.delimiter, args.file_type)
    return args, table_data

if __name__ == '__main__':
    args, items = parse_arguments()
    header_row = ["Title", "Size", "Files"]
    
    function_data = {
        "items" : items,
        "unselectable_indices" : [],
        "colors": get_colours(0),
        "top_gap": 0,
        "header": header_row,
        "max_width": 70,
    }
    if items == None:
        function_data["items"] = test_items
        function_data["highlights"] = test_highlights
        
        # unselectable_indices=[0,1,3,7,59]

    # Run the list picker
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)
    stdscr.keypad(True)
    selected_indices, opts, function_data = list_picker(
        stdscr,
        # items,
        # colors=custom_colors,
        # top_gap=0,
        # header=header_row,
        # max_width=70,
        # highlights=highlights,
        # unselectable_indices=unselectable_indices
        **function_data,
    )

    # Clean up
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    print("Final selected indices:", selected_indices)
