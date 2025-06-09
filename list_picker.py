import curses
import re
from list_picker_colours import get_colours, help_colours, notification_colours
import pyperclip
import os
import subprocess
import argparse
from table_to_list_of_lists import *
import time
from wcwidth import wcwidth, wcswidth
from utils import *
from sorting import *
from filtering import *
from input_field import *
from clipboard_operations import *
from searching import search
from help_screen import help_lines
from keys import keys_dict, notification_keys
from typing import Callable, Optional, Tuple

try:
    from data_stuff import test_items, test_highlights, test_header
except:
    test_items, test_highlights, test_header = [[]], [], []

def list_picker(
        stdscr: curses.window, 
        items: list = [[]],
        cursor_pos: int = 0,
        colours: dict = {},
        max_selected: int = -1,
        top_gap: int =0,
        title: str ="",
        header: list =[],
        max_column_width: int =70,
        
        auto_refresh: bool =False,
        timer: float = 5,

        get_new_data: bool =False,
        refresh_function: Optional[Callable] =None,
        get_data_startup: bool =False,

        unselectable_indices: list =[],
        highlights: list =[],
        highlights_hide: bool =False,
        number_columns: bool =True,
        column_widths = [],


        current_row : int = 0,
        current_page : int = 0,
        is_selecting : bool = False,
        is_deselecting : int = False,
        start_selection: int = -1,
        end_selection: int = -1,
        user_opts : str = "",
        user_settings : str = "",
        separator : str = "    ",
        search_query : str = "",
        search_count : int = 0,
        search_index : int = 0,
        filter_query : str = "",
        hidden_columns: set = set(),
        indexed_items: list[list[str]] = [[]],
        scroll_bar : int = True,

        selections: dict = {},
        highlight_full_row: bool =False,

        items_per_page : int = -1,
        sort_method : int = 0,
        sort_reverse: list[int] = [0],
        sort_column : int = 0,
        columns_sort_method: list[int] = [0],
        key_chain: str = "",
        last_key: Optional[str] = None,

        paginate: bool =False,
        mode_index: int =0,
        modes: list[dict] = [{}],
        display_modes: bool =False,
        require_option: list=[],
        disabled_keys: list=[],

        show_footer: bool =True,
        colours_start: int =0,
        colours_end: int =-1,
        key_remappings: dict = {},
        display_infobox : bool = False,
        infobox_items: list[list[str]] = [[]],
        display_only: bool = False,

        editable_columns: list[int] = [],
        
        centre_in_terminal: bool = False,
        centre_in_terminal_vertical: bool = True,
        centre_in_cols: bool = False,
        
) -> Tuple[list[int], str, dict]:
    """
    A list picker implemented using curses. Pass a list of lists and a header (optional) and it will display them as tabulated data.


    Returns:
        list, opts, cursor_pos: A list of indices representing the selected items along with any options passed
        selected, opts, funcition_data

        selected (list of ints): list of selected indices
        opts (str): any opts that are entered
        cursor_pos (int): the cursor_pos upon exit
    """


    curses.set_escdelay(25)

    def move_column(direction: int) -> None:
        nonlocal items, header, column_widths, sort_column
        """ 
        Cycles the column $direction places. 
        E.g., If $direction == -1 and the sort column is 3, then column 3 will swap with column 2
            in each of the rows in $items and 2 will become the new sort column.

        sort_column = 3, direction = -1
            [[0,1,2,*3*,4],
             [5,6,7,*8*,9]]
                -->
            [[0,1,*3*,2,4],
             [5,6,*8*,7,9]]

        returns:
            adjusted items, header, sort_column and column_widths
        """
        if len(items) < 1: return None
        if (sort_column+direction) < 0 or (sort_column+direction) >= len(items[0]): return None

        new_index = sort_column + direction

        # Swap columns in each row
        for row in items:
            row[sort_column], row[new_index] = row[new_index], row[sort_column]
        if header:
            header[sort_column], header[new_index] = header[new_index], header[sort_column]

        # Swap column widths
        column_widths[sort_column], column_widths[new_index] = column_widths[new_index], column_widths[sort_column]

        # Update current column index
        sort_column = new_index


    def set_colours(colours: dict, start: int = 0) -> None:
        """ Initialise curses colour pairs using dictionary with colour keys. """

        if not colours: return None
        curses.init_pair(start+1, colours['selected_fg'], colours['selected_bg'])
        curses.init_pair(start+2, colours['unselected_fg'], colours['unselected_bg'])
        curses.init_pair(start+3, colours['normal_fg'], colours['background'])
        curses.init_pair(start+4, colours['header_fg'], colours['header_bg'])
        curses.init_pair(start+5, colours['cursor_fg'], colours['cursor_bg'])
        curses.init_pair(start+6, colours['normal_fg'], colours['background'])
        curses.init_pair(start+7, colours['error_fg'], colours['error_bg'])
        curses.init_pair(start+8, colours['complete_fg'], colours['complete_bg'])
        curses.init_pair(start+9, colours['active_fg'], colours['active_bg'])
        curses.init_pair(start+10, colours['search_fg'], colours['search_bg'])
        curses.init_pair(start+11, colours['waiting_fg'], colours['waiting_bg'])
        curses.init_pair(start+12, colours['paused_fg'], colours['paused_bg'])
        curses.init_pair(start+13, colours['active_input_fg'], colours['active_input_bg'])
        curses.init_pair(start+14, colours['modes_selected_fg'], colours['modes_selected_bg'])
        curses.init_pair(start+15, colours['modes_unselected_fg'], colours['modes_unselected_bg'])
        curses.init_pair(start+16, colours['title_fg'], colours['title_bg'])
        curses.init_pair(start+17, colours['normal_fg'], colours['title_bar'])
        curses.init_pair(start+18, colours['normal_fg'], colours['scroll_bar_bg'])
        curses.init_pair(start+19, colours['selected_header_column_fg'], colours['selected_header_column_bg'])
        curses.init_pair(start+20, colours['footer_fg'], colours['footer_bg'])
        curses.init_pair(start+21, colours['refreshing_fg'], colours['refreshing_bg'])
        curses.init_pair(start+22, colours['40pc_fg'], colours['40pc_bg'])
        return start+21

    def infobox(stdscr: curses.window, message: str ="", title: str ="Infobox",  colours_end: int = 0, duration: int = 4) -> curses.window:
        """ Display non-interactive infobox window. """
        h, w = stdscr.getmaxyx()
        notification_width, notification_height = w//2, h-8
        message_width = notification_width-5

        if not message: message = "!!"
        if isinstance(message, str):
            submenu_items = ["  "+message[i*message_width:(i+1)*message_width] for i in range(len(message)//message_width+1)]
        else:
            submenu_items = message

        notification_remap_keys = { 
            curses.KEY_RESIZE: curses.KEY_F5,
            27: ord('q')
        }
        while True:
            h, w = stdscr.getmaxyx()

            submenu_win = curses.newwin(notification_height, notification_width, 3, w - (notification_width+4))
            s, o, f = list_picker(
                submenu_win,
                submenu_items,
                colours=notification_colours,
                title=title,
                show_footer=False,
                colours_start=150,
                disabled_keys=[ord('z'), ord('c')],
                top_gap=0,
                key_remappings = notification_remap_keys,
                display_only = True,
            )
            if o != "refresh": break

        return submenu_win

    def draw_screen(indexed_items: list[list[str]], highlights: list[dict] = [{}], clear: bool = True) -> None:
        """ Draw the list_picker screen. """
        nonlocal items, header
        nonlocal filter_query, search_query, search_count, search_index 
        nonlocal column_widths, hidden_columns 
        nonlocal start_selection, is_deselecting, is_selecting
        nonlocal paginate, title, modes, cursor_pos, scroll_bar,top_gap, show_footer, highlights_hide, centre_in_terminal, centre_in_cols, highlight_full_row

        if clear:
            stdscr.erase()

        ## Terminal too small to display list_picker
        h, w = stdscr.getmaxyx()
        if h<3 or w<len("Terminal"): return None
        if show_footer and (h<20 or w<45) or (h<12 and w<10):
            stdscr.addstr(h//2-1, (w-len("Terminal"))//2, "Terminal")
            stdscr.addstr(h//2, (w-len("Too"))//2, "Too")
            stdscr.addstr(h//2+1, (w-len("Small"))//2, "Small")
            return None

        column_widths = get_column_widths(items, header=header, max_column_width=max_column_width, number_columns=number_columns)
        visible_column_widths = [c for i,c in enumerate(column_widths) if i not in hidden_columns]
        visible_columns_total_width = sum(visible_column_widths) + len(separator)*(len(visible_column_widths)-1)
        startx = 0 if highlight_full_row else 2
        if visible_columns_total_width < w and centre_in_terminal:
            startx += (w - visible_columns_total_width) // 2
        
        top_space = top_gap

        ## Display title (if applicable)
        if title:
            stdscr.addstr(top_gap, 0, f"{' ':^{w}}", curses.color_pair(colours_start+17))
            title_x = (w-wcswidth(title))//2
            # title = f"{title:^{w}}"
            stdscr.addstr(top_gap, title_x, title, curses.color_pair(colours_start+16) | curses.A_BOLD)
            top_space += 1

        ## Display modes
        if display_modes and modes not in [[{}], []]:
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
                    stdscr.addstr(top_space, xmode, mode_str, curses.color_pair(colours_start+14) | curses.A_BOLD)
                # other modes
                else:
                    stdscr.addstr(top_space, xmode, mode_str, curses.color_pair(colours_start+15) | curses.A_UNDERLINE)
                xmode += split_space+mode_widths[i]
            top_space += 1

        ## Display header
        if header:
            header_str = ""
            up_to_selected_col = ""
            for i in range(len(header)):
                if i == sort_column: up_to_selected_col = header_str
                if i in hidden_columns: continue
                number = f"{i}. " if number_columns else ""
                number = f"{intStringToExponentString(i)}. " if number_columns else ""
                header_str += number
                header_str +=f"{header[i]:^{column_widths[i]}}"
                header_str += " "

            stdscr.addstr(top_space, 0, ' '*w, curses.color_pair(colours_start+4) | curses.A_BOLD)
            stdscr.addstr(top_space, startx, header_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+4) | curses.A_BOLD)

            # Highlight sort column
            if sort_column != None and sort_column not in hidden_columns and len(up_to_selected_col) < w and len(header) > 1: 
                number = f"{sort_column}. " if number_columns else ""
                number = f"{intStringToExponentString(sort_column)}. " if number_columns else ""
                stdscr.addstr(top_space, startx + len(up_to_selected_col), (number+f"{header[sort_column]:^{column_widths[sort_column]}}")[:w-len(up_to_selected_col)], curses.color_pair(colours_start+19) | curses.A_BOLD)
        ## Paginate
        if paginate:
            start_index = (cursor_pos//items_per_page) * items_per_page
            end_index = min(start_index + items_per_page, len(indexed_items))
        ## Scroll
        else:
            scrolloff = items_per_page//2
            start_index = max(0, min(cursor_pos - (items_per_page-scrolloff), len(indexed_items)-items_per_page))
            end_index = min(start_index + items_per_page, len(indexed_items))
        if len(indexed_items) == 0: start_index, end_index = 0, 0

        if centre_in_terminal_vertical and len(indexed_items) < items_per_page:
            top_space += (items_per_page - len(indexed_items)) //2 

        ## Display rows and highlights
        for idx in range(start_index, end_index):
            item = indexed_items[idx]
            y = idx - start_index + top_space + int(bool(header))

            row_str = format_row(item[1], hidden_columns, column_widths, separator, centre_in_cols)
            if idx == cursor_pos:
                stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+5) | curses.A_BOLD)
            else:
                stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+2))
            # Highlight the whole string of the selected rows
            if highlight_full_row:
                if selections[item[0]]:
                    stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+1))
                # Visually selected
                if is_selecting and start_selection <= idx <= cursor_pos:
                    stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+1))
                elif is_selecting and start_selection >= idx >= cursor_pos:
                    stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+1))
                # Visually deslected
                if is_deselecting and start_selection >= idx >= cursor_pos:
                    stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+1))
                elif is_deselecting and start_selection <= idx <= cursor_pos:
                    stdscr.addstr(y, startx, row_str[:min(w-startx, visible_columns_total_width)], curses.color_pair(colours_start+1))

            # Highlight the first char of the selected rows
            else:
                if selections[item[0]]:
                    stdscr.addstr(y, max(startx-2,0), ' ', curses.color_pair(colours_start+1))
                # Visually selected
                if is_selecting and start_selection <= idx <= cursor_pos:
                    stdscr.addstr(y, max(startx-2,0), ' ', curses.color_pair(colours_start+1))
                elif is_selecting and start_selection >= idx >= cursor_pos:
                    stdscr.addstr(y, max(startx-2,0), ' ', curses.color_pair(colours_start+1))
                # Visually deslected
                if is_deselecting and start_selection >= idx >= cursor_pos:
                    stdscr.addstr(y, max(startx-2,0), ' ', curses.color_pair(colours_start+10))
                elif is_deselecting and start_selection <= idx <= cursor_pos:
                    stdscr.addstr(y, max(startx-2,0), ' ', curses.color_pair(colours_start+10))

            if not highlights_hide:
                for highlight in highlights:
                    try:
                        if highlight["field"] == "all":
                            match = re.search(highlight["match"], row_str, re.IGNORECASE)
                            if not match: continue
                            highlight_start = match.start()
                            highlight_end = match.end()
                        elif type(highlight["field"]) == type(4) and highlight["field"] not in hidden_columns:
                            match = re.search(highlight["match"], truncate_to_display_width(item[1][highlight["field"]], column_widths[highlight["field"]], centre_in_cols), re.IGNORECASE)
                            if not match: continue
                            field_start = sum([width for i, width in enumerate(column_widths[:highlight["field"]]) if i not in hidden_columns]) + sum([1 for i in range(highlight["field"]) if i not in hidden_columns])*wcswidth(separator)
                            highlight_start = field_start + match.start()
                            highlight_end = match.end() + field_start
                        else:
                            continue
                        color_pair = curses.color_pair(colours_start+highlight["color"])  # Selected item
                        if idx == cursor_pos:
                            color_pair = curses.color_pair(colours_start+highlight["color"])  | curses.A_REVERSE
                        stdscr.addstr(y, startx+highlight_start, row_str[highlight_start:min(w-startx, highlight_end)], curses.color_pair(colours_start+highlight["color"]) | curses.A_BOLD)
                    except:
                        pass
            
        ## Display scrollbar
        if scroll_bar and len(indexed_items) and len(indexed_items) > (items_per_page):
            scroll_bar_length = int(items_per_page*items_per_page/len(indexed_items))
            if cursor_pos <= items_per_page//2:
                scroll_bar_start=top_space+int(bool(header))
            elif cursor_pos + items_per_page//2 >= len(indexed_items):
                scroll_bar_start = h - int(bool(show_footer))*3 - scroll_bar_length
            else:
                scroll_bar_start = int(((cursor_pos)/len(indexed_items))*items_per_page)+top_space+int(bool(header)) - scroll_bar_length//2
            scroll_bar_length = min(scroll_bar_length, h - scroll_bar_start-1)
            for i in range(scroll_bar_length):
                v = max(top_space+int(bool(header)), scroll_bar_start-scroll_bar_length//2)
                stdscr.addstr(scroll_bar_start+i, w-1, ' ', curses.color_pair(colours_start+18))

        ## Display footer
        if show_footer:
            # Fill background
            stdscr.addstr(h-3, 0, ' '*w, curses.color_pair(colours_start+20))
            stdscr.addstr(h-2, 0, ' '*w, curses.color_pair(colours_start+20))
            stdscr.addstr(h-1, 0, ' '*(w-1), curses.color_pair(colours_start+20)) # Problem with curses that you can't write to the last char

            if filter_query:
                stdscr.addstr(h - 2, 2, f" Filter: {filter_query} "[:w-40], curses.color_pair(colours_start+20) | curses.A_BOLD)
            if search_query:
                stdscr.addstr(h - 3, 2, f" Search: {search_query} [{search_index}/{search_count}] "[:w-3], curses.color_pair(colours_start+20) | curses.A_BOLD)
            if user_opts:
                stdscr.addstr(h-1, 2, f" Opts: {user_opts} "[:w-3], curses.color_pair(colours_start+20) | curses.A_BOLD)
            # Display sort information
            sort_column_info = f"{sort_column if sort_column is not None else 'None'}"
            sort_method_info = f"{SORT_METHODS[columns_sort_method[sort_column]]}" if sort_column != None else "NA"
            sort_order_info = "Desc." if sort_reverse[sort_column] else "Asc."
            stdscr.addstr(h - 2, w-35, f" Sort: ({sort_column_info}, {sort_method_info}, {sort_order_info}) ", curses.color_pair(colours_start+20) | curses.A_BOLD)

            # Display selection count
            selected_count = sum(selections.values())
            if paginate:
                stdscr.addstr(h - 1, w-35, f" {cursor_pos+1}/{len(indexed_items)}  Page {cursor_pos//items_per_page + 1}/{(len(indexed_items) + items_per_page - 1) // items_per_page}  Selected {selected_count} ", curses.color_pair(colours_start+20) | curses.A_BOLD)
            else:
                stdscr.addstr(h - 1, w-35, f" {cursor_pos+1}/{len(indexed_items)}  |  Selected {selected_count} ", curses.color_pair(colours_start+20) | curses.A_BOLD)

            # Display cursor mode
            select_mode = "Cursor"
            if is_selecting: select_mode = "Visual Selection"
            elif is_deselecting: select_mode = "Visual deselection"
            stdscr.addstr(h - 3, w-35, f" {select_mode}", curses.color_pair(colours_start+4) | curses.A_BOLD)
            # Show auto-refresh
            if auto_refresh:
                stdscr.addstr(h - 3, w-35+len(select_mode)+2, f"Auto-refresh", curses.color_pair(colours_start+21) | curses.A_BOLD | curses.A_REVERSE)

            stdscr.refresh()
        
        ## Display infobox
        if display_infobox:
            infobox(stdscr, message=infobox_items)
            stdscr.timeout(2000)  # timeout is set to 50 in order to get the infobox to be displayed so here we reset it to 2000

    def initialise_variables(get_data: bool = False) -> None:
        """ Initialise the variables that keep track of the data. """
        nonlocal items, indexed_items, header, selections, indexed_items, unselectable_indices, editable_columns
        nonlocal filter_query, search_query, search_count, search_index
        nonlocal columns_sort_method, hidden_columns, sort_reverse
        nonlocal refresh_function
        nonlocal start_selection, is_deselecting, is_selecting
        nonlocal paginate, title, modes, cursor_pos, scroll_bar,top_gap, show_footer, highlights_hide, centre_in_terminal, centre_in_cols, highlight_full_row, require_option, number_columns, max_column_width

        if get_data and refresh_function != None:
            items, header = refresh_function()

        if items == []: items = [[]]
        ## Ensure that items is a List[List[Str]] object
        if not isinstance(items[0], list):
            items = [[item] for item in items]
        items = [[str(cell) for cell in row] for row in items]


        # Ensure that header is of the same length as the rows
        if header and len(header) != len(items[0]):
            header = [str(header[i]) if i < len(header) else "" for i in range(len(items[0]))]

        # Constants
        # DEFAULT_ITEMS_PER_PAGE = os.get_terminal_size().lines - top_gap*2-2-int(bool(header))
        top_space = top_gap
        if title: top_space+=1
        if display_modes: top_space+=1

        state_variables = {}
        SORT_METHODS = ['original', 'lexical', 'LEXICAL', 'alphanum', 'ALPHANUM', 'time', 'numerical', 'size']


        # Initial states
        if len(selections) != len(items):
            selections = {i : False if i not in selections else bool(selections[i]) for i in range(len(items))}
        h, w = stdscr.getmaxyx()
        items_per_page = h - top_space-int(bool(header)) - 3*int(bool(show_footer))
        indexed_items = list(enumerate(items))
        column_widths = get_column_widths(items, header=header, max_column_width=max_column_width, number_columns=number_columns)
        if require_option == []:
            require_option = [False for x in indexed_items]

        if len(items)>0 and len(columns_sort_method) < len(items[0]):
            columns_sort_method = columns_sort_method + [0 for i in range(len(items[0])-len(columns_sort_method))]
        if len(items)>0 and len(sort_reverse) < len(items[0]):
            sort_reverse = sort_reverse + [False for i in range(len(items[0])-len(sort_reverse))]
        if len(items)>0 and len(editable_columns) < len(items[0]):
            editable_columns = editable_columns + [False for i in range(len(items[0])-len(editable_columns))]
        if sort_reverse == [] and len(items) > 0:
            sort_reverse = [False for i in items[0]]

        # If a filter is passed then refilter
        if filter_query:
            # prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
            # prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
            indexed_items = filter_items(items, indexed_items, filter_query)
            if cursor_pos in [x[0] for x in indexed_items]: cursor_pos = [x[0] for x in indexed_items].index(cursor_pos)
            else: cursor_pos = 0
        # If a sort is passed
        if len(indexed_items) > 0 and sort_column != None and columns_sort_method[sort_column] != 0:
            sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
        if len(items[0]) == 1:
            number_columns = False



        h, w = stdscr.getmaxyx()

        # Adjust variables to ensure correctness if errors
        ## Move to a selectable row (if applicable)
        if len(items) <= len(unselectable_indices): unselectable_indices = []
        new_pos = (cursor_pos)%len(items)
        while new_pos in unselectable_indices and new_pos != cursor_pos:
            new_pos = (new_pos + 1) % len(items)

        assert new_pos < len(items)
        cursor_pos = new_pos
        return SORT_METHODS, h, w, items_per_page

    SORT_METHODS, h, w, items_per_page = initialise_variables(get_data=True)

    draw_screen(indexed_items, highlights)
    
    def get_function_data() -> dict:
        """ Returns a dict of the main variables needed to restore the state of list_pikcer. """
        function_data = {
            "selections": selections,
            "items_per_page":       items_per_page,
            "current_row":          current_row,
            "current_page":         current_page,
            "cursor_pos":           cursor_pos,
            "sort_column":          sort_column,
            "sort_method":          sort_method,
            "sort_reverse":         sort_reverse,
            "hidden_columns":       hidden_columns,
            "is_selecting":         is_selecting,
            "is_deselecting":       is_deselecting,
            "user_opts":            user_opts,
            "user_settings":        user_settings,
            "separator":            separator,
            "search_query":         search_query,
            "search_count":         search_count,
            "search_index":         search_index,
            "filter_query":         filter_query,
            "indexed_items":        indexed_items,
            "start_selection":      start_selection,
            "end_selection":        end_selection,
            "highlights":           highlights,
            "max_column_width":     max_column_width,
            "mode_index":           mode_index,
            "modes":                modes,
            "title":                title,
            "display_modes":        display_modes,
            "require_option":       require_option,
            "top_gap":              top_gap,
            "number_columns":       number_columns,
            "items":                items,
            "indexed_items":        indexed_items,
            "header":               header,
            "scroll_bar":           scroll_bar,
            "columns_sort_method":  columns_sort_method,
            "disabled_keys":        disabled_keys,
            "show_footer":          show_footer,
            "colours_start":        colours_start,
            "colours_end":          colours_end,
            "display_only":         display_only,
            "infobox_items":        infobox_items,
            "display_infobox":      display_infobox,
            "key_remappings":       key_remappings,
            "auto_refresh":         auto_refresh,
            "get_new_data":         get_new_data,
            "refresh_function":     refresh_function,
            "get_data_startup":     get_data_startup,
            "editable_columns":     editable_columns,
            "last_key":             None,
            "centre_in_terminal":   centre_in_terminal,
            "centre_in_cols":       centre_in_cols,
            "highlight_full_row":   highlight_full_row,
            "column_widths":        column_widths,
            
        }
        return function_data




    def delete_entries() -> None:
        """ Delete entries from view. """
        nonlocal indexed_items, selections, items
        # Remove selected items from the list
        selected_indices = [index for index, selected in selections.items() if selected]
        if not selected_indices:
            # Remove the currently focused item if nothing is selected
            selected_indices = [indexed_items[cursor_pos][0]]

        items = [item for i, item in enumerate(items) if i not in selected_indices]
        indexed_items = [(i, item) for i, item in enumerate(items)]
        selections = {i:False for i in range(len(indexed_items))}
        draw_screen(indexed_items, highlights)


    def choose_option(stdscr: curses.window, options: list =[str], field_name: str = "Input", x:int=0, y:int=0, literal:bool=False, colours_start:int=0) -> None:
        """
        Display input field at x,y

        ---Arguments
            stdscr: curses screen
            usrtxt (str): text to be edited by the user
            field_name (str): The text to be displayed at the start of the text input
            x (int): prompt begins at (x,y) in the screen given
            y (int): prompt begins at (x,y) in the screen given
            colours_start (bool): start index of curses init_pair.

        ---Returns
            usrtxt, return_code
            usrtxt: the text inputted by the user
            return_code: 
                            0: user hit escape
                            1: user hit return
        """
        if options == []: options = [str(i) for i in range(256)]
        cursor = 0
        h, w = stdscr.getmaxyx()

        window_width = min(max([len(x) for x in options] + [len(field_name)] + [10]) + 6, w//2)
        window_height = min(h//2, len(options)-4)

        submenu_win = curses.newwin(window_height, window_width, (h-window_height)//2, (w-window_width)//2)

        
        s, o, f = list_picker(
            submenu_win,
            items=options,
            colours=notification_colours,
            colours_start=50,
            title=field_name,
            # show_footer=False,
            disabled_keys=[ord('z'), ord('c')],
            top_gap=0,
            show_footer=False,
            # scroll_bar=False,
        )
        if s:
            return {x: options[x] for x in s}

        return {}


    def notification(stdscr: curses.window, message: str="", colours_end: int=0, duration:int=4) -> None:
        """ Notification box. """
        notification_width, notification_height = 50, 7
        message_width = notification_width-5

        if not message: message = "!!"
        submenu_items = ["  "+message[i*message_width:(i+1)*message_width] for i in range(len(message)//message_width+1)]

        notification_remap_keys = { 
            curses.KEY_RESIZE: curses.KEY_F5,
            27: ord('q')
        }
        while True:
            h, w = stdscr.getmaxyx()

            submenu_win = curses.newwin(notification_height, notification_width, 3, w - (notification_width+4))
            s, o, f = list_picker(
                submenu_win,
                submenu_items,
                colours=notification_colours,
                title="Notification",
                show_footer=False,
                colours_start=50,
                disabled_keys=[ord('z'), ord('c')],
                top_gap=0,
                # scroll_bar=False,
                key_remappings = notification_remap_keys,
            )
            if o != "refresh": break
            submenu_win.clear()
            submenu_win.refresh()
            del submenu_win
            stdscr.clear()
            stdscr.refresh()
            draw_screen(indexed_items, highlights)
        # set_colours(colours=get_colours(0))

    def toggle_column_visibility(col_index:int) -> None:
        """ Toggle the visibility of the column at col_index. """
        if 0 <= col_index < len(items[0]):
            if col_index in hidden_columns:
                hidden_columns.remove(col_index)
            else:
                hidden_columns.add(col_index)

    def apply_settings() -> None:
        """ The users settings will be stored in the user_settings variable. This function applies those settings. """
        
        nonlocal user_settings, highlights, sort_column, columns_sort_method
        nonlocal auto_refresh, cursor_pos, centre_in_cols, centre_in_terminal, highlights_hide, centre_in_terminal_vertical
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

                if setting[0] == "!" and len(setting) > 1:
                    if setting[1:].isnumeric():
                        cols = setting[1:].split(",")
                        for col in cols:
                            toggle_column_visibility(int(col))
                    elif setting[1] == "r":
                        auto_refresh = not auto_refresh
                    elif setting[1] == "h":
                        highlights_hide = not highlights_hide

                elif setting in ["nhl", "nohl", "nohighlights"]:
                    highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]
                elif setting[0] == "s":
                    if 0 <= int(setting[1:]) < len(items[0]):
                        sort_column = int(setting[1:])
                        current_pos = indexed_items[cursor_pos][0]
                        sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
                        new_pos = [row[0] for row in indexed_items].index(current_pos)
                        cursor_pos = new_pos
                elif setting == "ct":
                    centre_in_terminal = not centre_in_terminal
                elif setting == "cc":
                    centre_in_cols = not centre_in_cols
                elif setting == "cv":
                    centre_in_terminal_vertical = not centre_in_terminal_vertical
                elif setting[0] == "":
                    cols = setting[1:].split(",")
                    for col in cols:
                        toggle_column_visibility(int(col))

            user_settings = ""

    def toggle_item(index: int) -> None:
        """ Toggle selection of item at index. """
        selections[index] = not selections[index]
        draw_screen(indexed_items, highlights)

    def select_all() -> None:
        """ Select all in indexed_items. """
        for i in range(len(indexed_items)):
            selections[indexed_items[i][0]] = True
        draw_screen(indexed_items, highlights)

    def deselect_all() -> None:
        """ Deselect all items in indexed_items. """
        for i in range(len(selections)):
            selections[i] = False
        draw_screen(indexed_items, highlights)

    def handle_visual_selection(selecting:bool = True) -> None:
        """ Toggle visual selection or deselection. """
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
            if start_selection != -1:
                start = min(start_selection, end_selection)
                end = max(start_selection, end_selection)
                for i in range(start, end + 1):
                    if indexed_items[i][0] not in unselectable_indices:
                        selections[indexed_items[i][0]] = True
            start_selection = -1
            end_selection = -1
            is_selecting = False
            draw_screen(indexed_items, highlights)
        elif is_deselecting:
            end_selection = indexed_items[cursor_pos][0]
            end_selection = cursor_pos
            if start_selection != -1:
                start = min(start_selection, end_selection)
                end = max(start_selection, end_selection)
                for i in range(start, end + 1):
                    # selections[i] = False
                    selections[indexed_items[i][0]] = False
            start_selection = -1
            end_selection = -1
            is_deselecting = False
            draw_screen(indexed_items, highlights)
    def cursor_down() -> None:
        """ Move cursor down. """
        # Returns: whether page is turned
        nonlocal cursor_pos
        new_pos = cursor_pos + 1
        while True:
            if new_pos >= len(indexed_items): return False
            if indexed_items[new_pos][0] in unselectable_indices: new_pos+=1
            else: break
        cursor_pos = new_pos
        return True

    def cursor_up() -> None:
        """ Move cursor up. """
        # Returns: whether page is turned
        nonlocal cursor_pos
        new_pos = cursor_pos - 1
        while True:
            if new_pos < 0: return False
            elif new_pos in unselectable_indices: new_pos -= 1
            else: break
        cursor_pos = new_pos
        return True

    def remapped_key(key: int, val: int, key_remappings: dict) -> bool:
        """ Check if key has been remapped to val in key_remappings. """
        if key in key_remappings:
            if key_remappings[key] == val or (isinstance(key_remappings[key], list) and val in key_remappings[key]):
                return True
        return False
    def check_key(function: str, key: int,  keys_dict: dict) -> bool:
        """
        Check if $key is assigned to $function in the keys_dict. 
            Allows us to redefine functions to different keys in the keys_dict.

        E.g., keys_dict = { $key, "help": ord('?') }, 
        """
        if function in keys_dict and key in keys_dict[function]:
            return True
        return False


    initial_time = time.time()-timer

    curses.curs_set(0)
    # stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(2000)  # Set a timeout for getch() to ensure it does not block indefinitely
    stdscr.clear()
    stdscr.refresh()

    

    # Initialize colours
    # Check if terminal supports color
    if curses.has_colors() and colours != None:
        # raise Exception("Terminal does not support color")
        curses.start_color()
        colours_end = set_colours(colours, start=colours_start)
        # os.system(f"notify-send cs{colours_start},{colours_end}")

    # Set terminal background color
    stdscr.bkgd(' ', curses.color_pair(colours_start+3))  # Apply background color
    draw_screen(indexed_items, highlights)

    if display_only:
        stdscr.timeout(50)
        stdscr.getch()
        function_data = get_function_data()
        return [], "", function_data

    # Main loop
    data_refreshed = False
    
    while True:
        key = stdscr.getch()
        if key in disabled_keys: continue
        clear_screen=True
        # os.system(f"notify-send '2'")
        
        # time.sleep(random.uniform(0.05, 0.1))
        # os.system(f"notify-send 'Timer {timer}'")
        # if timer:
            # os.system(f"notify-send '{time.time() - initial_time}, {timer} {bool(timer)}, {time.time() - initial_time > timer}'")
        if check_key("refresh", key, keys_dict) or remapped_key(key, curses.KEY_F5, key_remappings) or (auto_refresh and (time.time() - initial_time) > timer):
            h, w = stdscr.getmaxyx()
            stdscr.addstr(0,w-3,"⟲")
            stdscr.refresh()
            if get_new_data and refresh_function:
                # f = refresh_function[0]
                # args = refresh_function[1]
                # kwargs = refresh_function[2]
                # items = f(*args, **kwargs)

                items, header = refresh_function()
                SORT_METHODS, h, w, items_per_page = initialise_variables(get_data=True)

                initial_time = time.time()
                draw_screen(indexed_items, highlights, clear=False)
            else:

                function_data = get_function_data()
                return [], "refresh", function_data

        if check_key("help", key, keys_dict):
            stdscr.clear()
            stdscr.refresh()
            list_picker(
                stdscr,
                items = help_lines,
                colours=help_colours,
                max_selected=1,
                top_gap=0,
                title=f"{title} Help",
                disabled_keys=[ord('?'), ord('v'), ord('V'), ord('m'), ord('M'), ord('l'), curses.KEY_ENTER, ord('\n')],
                colours_start=100,
                paginate=paginate,
            )

        elif check_key("exit", key, keys_dict):
            stdscr.clear()
            function_data = get_function_data()
            function_data["last_key"] = key
            return [], "", function_data
        elif check_key("settings_input", key, keys_dict):
            usrtxt = f"{user_settings.strip()} " if user_settings else ""
            usrtxt, return_val = input_field(
                stdscr,
                usrtxt=usrtxt,
                field_name="Settings",
                x=2,
                y=h-1,
            )
            if return_val:
                user_settings = usrtxt
                apply_settings()
                user_settings = ""

        elif check_key("move_column_left", key, keys_dict):
            move_column(direction=-1)

        elif check_key("move_column_right", key, keys_dict):
            move_column(direction=1)
        elif check_key("cursor_down", key, keys_dict):
            page_turned = cursor_down()
            if not page_turned: clear_screen = False
        elif check_key("half_page_down", key, keys_dict):
            clear_screen = False
            for i in range(items_per_page//2): 
                if cursor_down(): clear_screen = True
        elif check_key("five_down", key, keys_dict):
            clear_screen = False
            for i in range(5): 
                if cursor_down(): clear_screen = True
        elif check_key("cursor_up", key, keys_dict):
            page_turned = cursor_up()
            if not page_turned: clear_screen = False
        elif check_key("five_up", key, keys_dict):
            clear_screen = False
            for i in range(5): 
                if cursor_up(): clear_screen = True
        elif check_key("half_page_up", key, keys_dict):
            clear_screen = False
            for i in range(items_per_page//2): 
                if cursor_up(): clear_screen = True

        elif check_key("toggle_select", key, keys_dict):
            if len(indexed_items) > 0:
                item_index = indexed_items[cursor_pos][0]
                selected_count = sum(selections.values())
                if max_selected == -1 or selected_count >= max_selected:
                    toggle_item(item_index)
            cursor_down()
        elif check_key("select_all", key, keys_dict):  # Select all (m or ctrl-a)
            select_all()

        elif check_key("select_none", key, keys_dict):  # Deselect all (M or ctrl-r)
            deselect_all()

        elif check_key("cursor_top", key, keys_dict):
            new_pos = 0
            while True:
                if new_pos in unselectable_indices: new_pos+=1
                else: break
            if new_pos < len(indexed_items):
                cursor_pos = new_pos

            draw_screen(indexed_items, highlights)

        elif check_key("cursor_bottom", key, keys_dict):
            new_pos = len(indexed_items)-1
            while True:
                if new_pos in unselectable_indices: new_pos-=1
                else: break
            if new_pos < len(items) and new_pos >= 0:
                cursor_pos = new_pos
            draw_screen(indexed_items, highlights)
            # current_row = items_per_page - 1
            # if current_page + 1 == (len(indexed_items) + items_per_page - 1) // items_per_page:
            #
            #     current_row = (len(indexed_items) +items_per_page - 1) % items_per_page
            # draw_screen(indexed_items, highlights)
        elif check_key("enter", key, keys_dict):
            # Print the selected indices if any, otherwise print the current index
            if is_selecting or is_deselecting: handle_visual_selection()
            if len(indexed_items) == 0:
                function_data = get_function_data()
                function_data["last_key"] = key
                return [], "", function_data
            selected_indices = get_selected_indices(indexed_items, selections)
            if not selected_indices:
                selected_indices = [indexed_items[cursor_pos][0]]
            
            for index in selected_indices:
                if require_option[index]:
                    # notification(stdscr, message=f"opt required for {index}")
                    usrtxt = f"{user_opts} " if user_opts else ""
                    usrtxt, return_val = input_field(
                        stdscr,
                        usrtxt=usrtxt,
                        field_name="Opts",
                        x=2,
                        y=h-1,
                    )
                    if return_val:
                        user_opts = usrtxt

            stdscr.clear()
            stdscr.refresh()
            function_data = get_function_data()
            function_data["last_key"] = key
            return selected_indices, user_opts, function_data
        elif check_key("page_down", key, keys_dict):  # Next page
            cursor_pos = min(len(indexed_items) - 1, cursor_pos+items_per_page)

        elif check_key("page_up", key, keys_dict):
            cursor_pos = max(0, cursor_pos-items_per_page)

        elif check_key("redraw_screen", key, keys_dict):
            stdscr.clear()
            stdscr.refresh()
            draw_screen(indexed_items, highlights)

        elif check_key("cycle_sort_method", key, keys_dict):
            columns_sort_method[sort_column] = (columns_sort_method[sort_column]+1) % len(SORT_METHODS)
            if len(indexed_items) > 0:
                current_index = indexed_items[cursor_pos][0]
                sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
                cursor_pos = [row[0] for row in indexed_items].index(current_index)
        elif check_key("cycle_sort_method_reverse", key, keys_dict):  # Cycle sort method
            columns_sort_method[sort_column] = (columns_sort_method[sort_column]-1) % len(SORT_METHODS)
            if len(indexed_items) > 0:
                current_index = indexed_items[cursor_pos][0]
                sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
                cursor_pos = [row[0] for row in indexed_items].index(current_index)
        elif check_key("cycle_sort_order", key, keys_dict):  # Toggle sort order
            sort_reverse[sort_column] = not sort_reverse[sort_column]
            if len(indexed_items) > 0:
                current_index = indexed_items[cursor_pos][0]
                sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
                cursor_pos = [row[0] for row in indexed_items].index(current_index)
        elif check_key("col_select", key, keys_dict):
            col_index = key - ord('0')
            if 0 <= col_index < len(items[0]):
                sort_column = col_index
                if len(indexed_items) > 0:
                    current_index = indexed_items[cursor_pos][0]
                    sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
                    cursor_pos = [row[0] for row in indexed_items].index(current_index)
        elif check_key("col_hide", key, keys_dict):
            d = {'!': 0, '@': 1, '#': 2, '$': 3, '%': 4, '^': 5, '&': 6, '*': 7, '(': 8, ')': 9}
            d = {s:i for i,s in enumerate(")!@#$%^&*(")}
            col_index = d[chr(key)]
            toggle_column_visibility(col_index)
        elif key == ord('Y'):  # Copy (visible) selected values to clipboard
            copy_values(indexed_items, selections, hidden_columns, column_widths, separator)
            notification(stdscr, f"{sum(selections.values())} full rows copied to clipboard", colours_end=colours_end)
        elif key == ord('y'):  # Copy full values of selected entries to clipboard
            copy_full_values(indexed_items, selections, hidden_columns)
            notification(stdscr, f"{sum(selections.values())} full rows copied to clipboard")
        elif key == ord('c'):
            copy_selected_visible_rows_to_clipboard(items, selections, hidden_columns)
            notification(stdscr, f"{sum(selections.values())} visible rows copied to clipboard", colours_end=colours_end)
        elif key == ord('C'):
            # copy_items_to_clipboard()
            copy_selected_rows_to_clipboard(items, selections)
            notification(stdscr, f"{sum(selections.values())} full rows copied to clipboard", colours_end=colours_end)
        elif check_key("delete", key, keys_dict):  # Delete key
            delete_entries()
        elif check_key("increase_lines_per_page", key, keys_dict):
            items_per_page += 1
            draw_screen(indexed_items, highlights)
        elif check_key("decrease_lines_per_page", key, keys_dict):
            if items_per_page > 1:
                items_per_page -= 1
            draw_screen(indexed_items, highlights)
        elif check_key("decrease_column_width", key, keys_dict):
            if max_column_width > 10:
                max_column_width -= 10
                column_widths[:] = get_column_widths(items, header=header, max_column_width=max_column_width, number_columns=number_columns)
                draw_screen(indexed_items, highlights)
        elif check_key("increase_column_width", key, keys_dict):
            if max_column_width < 1000:
                max_column_width += 10
                column_widths[:] = get_column_widths(items, header=header, max_column_width=max_column_width, number_columns=number_columns)
                draw_screen(indexed_items, highlights)
        elif check_key("visual_selection_toggle", key, keys_dict):
            handle_visual_selection()
            draw_screen(indexed_items, highlights)

        elif check_key("visual_deselection_toggle", key, keys_dict):
            handle_visual_selection(selecting=False)
            draw_screen(indexed_items, highlights)

        if key == curses.KEY_RESIZE:  # Terminal resize signal
            h, w = stdscr.getmaxyx()
            top_space = top_gap
            if title: top_space+=1
            if display_modes: top_space+=1
            items_per_page = os.get_terminal_size().lines - top_space*2-2-int(bool(header))
            h, w = stdscr.getmaxyx()
            items_per_page = h - top_space-int(bool(header)) - 3*int(bool(show_footer))
            column_widths[:] = get_column_widths(items, header=header, max_column_width=max_column_width, number_columns=number_columns)


        elif key == ord('r'):
            # Refresh
            top_space = top_gap +  int(bool(display_modes)) + int(bool(title)) + int(bool(header))
            bottom_space = 3*int(bool(show_footer))
            items_per_page = os.get_terminal_size().lines - top_space
            h, w = stdscr.getmaxyx()
            items_per_page = h - top_space - bottom_space
            stdscr.refresh()

        elif check_key("filter_input", key, keys_dict):
            draw_screen(indexed_items, highlights)
            usrtxt = f" {filter_query}" if filter_query else ""
            h, w = stdscr.getmaxyx()
            usrtxt, return_val = input_field(
                stdscr,
                usrtxt=usrtxt,
                field_name="Filter",
                x=2,
                y=h-2,
            )
            if return_val:
                filter_query = usrtxt

                # If the current mode filter has been changed then go back to the first mode
                if "filter" in modes[mode_index] and modes[mode_index]["filter"] not in filter_query:
                    mode_index = 0
                # elif "filter" in modes[mode_index] and modes[mode_index]["filter"] in filter_query:
                #     filter_query.split(modes[mode_index]["filter"])

                prev_index = indexed_items[cursor_pos][0] if len(indexed_items)>0 else 0
                indexed_items = filter_items(items, indexed_items, filter_query)
                if prev_index in [x[0] for x in indexed_items]: new_index = [x[0] for x in indexed_items].index(prev_index)
                else: new_index = 0
                cursor_pos = new_index
                # Re-sort items after applying filter
                if columns_sort_method[sort_column] != 0:
                    sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column


        elif check_key("search_input", key, keys_dict):
            draw_screen(indexed_items, highlights)
            usrtxt = f"{search_query} " if search_query else ""
            usrtxt, return_val = input_field(
                stdscr,
                usrtxt=usrtxt,
                field_name="Search",
                x=2,
                y=h-3,
            )
            if return_val:
                search_query = usrtxt
                return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                    query=search_query,
                    indexed_items=indexed_items,
                    highlights=highlights,
                    cursor_pos=cursor_pos,
                    unselectable_indices=unselectable_indices,
                )
                if return_val:
                    cursor_pos, search_index, search_count, highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights

        elif check_key("continue_search_forward", key, keys_dict):
            return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                query=search_query,
                indexed_items=indexed_items,
                highlights=highlights,
                cursor_pos=cursor_pos,
                unselectable_indices=unselectable_indices,
                continue_search=True,
            )
            if return_val:
                cursor_pos, search_index, search_count, highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights
        elif check_key("continue_search_backward", key, keys_dict):
            return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                query=search_query,
                indexed_items=indexed_items,
                highlights=highlights,
                cursor_pos=cursor_pos,
                unselectable_indices=unselectable_indices,
                continue_search=True,
                reverse=True,
            )
            if return_val:
                cursor_pos, search_index, search_count, highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights
        elif check_key("cancel", key, keys_dict):  # ESC key
            # order of escapes:
            # 1. selecting/deslecting
            # 2. search
            # 3. filter
            # 4. selecting
            # nonlocal highlights

            if is_selecting or is_deselecting:
                start_selection = -1
                end_selection = -1
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
                # Re-sort items after applying filter
                if columns_sort_method[sort_column] != 0:
                    sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column

            else:
                search_query = ""
                mode_index = 0
                highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]
                continue
            draw_screen(indexed_items, highlights)
        elif check_key("opts_input", key, keys_dict):
            usrtxt = f"{user_opts} " if user_opts else ""
            usrtxt, return_val = input_field(
                stdscr,
                usrtxt=usrtxt,
                field_name="Opts",
                x=2,
                y=h-1,
            )
            if return_val:
                user_opts = usrtxt
        elif check_key("opts_select", key, keys_dict):
            s = choose_option(stdscr)
            if user_opts.strip(): user_opts += " "
            user_opts += " ".join(s.values())
        elif check_key("notification_toggle", key, keys_dict):
            notification(stdscr, colours_end=colours_end)
        elif check_key("mode_next", key, keys_dict): # tab key
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
                    # Re-sort items after applying filter
                    if columns_sort_method[sort_column] != 0:
                        sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
        elif check_key("mode_prev", key, keys_dict): # shift+tab key
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
                    # Re-sort items after applying filter
                    if columns_sort_method[sort_column] != 0:
                        sort_items(indexed_items, sort_method=columns_sort_method[sort_column], sort_column=sort_column, sort_reverse=sort_reverse[sort_column])  # Re-sort items based on new column
        elif check_key("pipe_input", key, keys_dict):
            usrtxt = "xargs -d '\n' -I{}  "
            usrtxt, return_val = input_field(
                stdscr,
                usrtxt=usrtxt,
                field_name="Command",
                x=2,
                y=h-2,
                literal=True,
            )
            if return_val:
                selected_indices = get_selected_indices(indexed_items, selections)
                if not selected_indices:
                    selected_indices = [indexed_items[cursor_pos][0]]
                full_values = [format_row_full(items[i], hidden_columns) for i in selected_indices]  # Use format_row_full for full data
                if full_values:
                    # os.system("notify-send " + "'" + '\t'.join(full_values).replace("'", "*") + "'")
                    process = subprocess.Popen(usrtxt, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.communicate(input='\n'.join(full_values).encode('utf-8'))

        elif check_key("reset_opts", key, keys_dict):
            user_opts = ""
        elif check_key("edit", key, keys_dict):
            if len(indexed_items) > 0 and sort_column >=0 and editable_columns[sort_column]:
                current_val = indexed_items[cursor_pos][1][sort_column]
                usrtxt = f"{current_val}"
                usrtxt, return_val = input_field(
                    stdscr,
                    usrtxt=usrtxt,
                    field_name="Edit value",
                    x=2,
                    y=h-2,
                )
                if return_val:
                    indexed_items[cursor_pos][1][sort_column] = usrtxt

        elif check_key("edit_picker", key, keys_dict):
            if len(indexed_items) > 0 and sort_column >=0 and editable_columns[sort_column]:
                current_val = indexed_items[cursor_pos][1][sort_column]
                usrtxt = f"{current_val}"
                usrtxt, return_val = input_field(
                    stdscr,
                    usrtxt=usrtxt,
                    field_name="Edit value",
                    x=2,
                    y=h-2,
                )
                if return_val:
                    indexed_items[cursor_pos][1][sort_column] = usrtxt
        draw_screen(indexed_items, highlights, clear=clear_screen)



def parse_arguments():
    """ Parse arguments. """
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
        print("Error: Please provide input file or use --stdin flag.")
        return None, None
        # sys.exit(1)
    
    table_data = table_to_list(input_arg, args.delimiter, args.file_type)
    return args, table_data

if __name__ == '__main__':
    args, items = parse_arguments()
    
    function_data = {
        "items" : items,
        "unselectable_indices" : [],
        "colours": get_colours(0),
        "top_gap": 0,
        "max_column_width": 70,
    }
    if items == None:
        function_data["items"] = test_items
        function_data["highlights"] = test_highlights
        function_data["header"] = test_header
        
        # unselectable_indices=[0,1,3,7,59]

    # Run the list picker
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)
    stdscr.keypad(True)
    selected_indices, opts, function_data = list_picker(
        stdscr,
        **function_data,
    )

    # Clean up
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    print("Final selected indices:", selected_indices)
