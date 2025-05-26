import curses

def input_field(stdscr, usrtxt="", field_name="Input", x=0, y=0, literal=False):
    """
    Display input field at x,y

    ---Arguments
        stdscr: curses screen
        usrtxt (str): text to be edited by the user
        field_name (str): The text to be displayed at the start of the text input
        x (int): prompt begins at (x,y) in the screen given
        y (int): prompt begins at (x,y) in the screen given

    ---Returns
        usrtxt, return_code
        usrtxt: the text inputted by the user
        return_code: 
                        0: user hit escape
                        1: user hit return
    """
    cursor = 0
    h, w = stdscr.getmaxyx()
    while True:
        # stdscr.addstr(h - 2, 50, f"{field_name}: {repr(usrtxt)}", curses.color_pair(13))
        # if usrtxt and cursor != 0:
        #     stdscr.addstr(h - 2, 50+len(usrtxt)-cursor+1+len("Command: "), f"{usrtxt[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
        # else:
        #     stdscr.addstr(h - 2, 50-cursor+len(usrtxt)+1+len("Command: "), f" ", curses.color_pair(13) | curses.A_REVERSE)
        # stdscr.addstr(y, x, f"{field_name}: {repr(usrtxt)}", curses.color_pair(13))

        # Clear background to end of row
        stdscr.addstr(y, x, " "*((w-x)-2), curses.color_pair(3))

        # Display the field name and current text
        if literal:
            stdscr.addstr(y, x, f"{field_name}: {repr(usrtxt)}", curses.color_pair(13))
        else:
            stdscr.addstr(y, x, f" {field_name}: {usrtxt}", curses.color_pair(13))

        visible_cursor_x = x+len(usrtxt)-cursor+len(f" {field_name}: ")
        if literal:
            visible_cursor_x = x+len(repr(usrtxt))-cursor+len(f" {field_name}: ")-2


        # Display cursor
        if not literal:
            if usrtxt and cursor != 0:
                stdscr.addstr(y, visible_cursor_x, f"{usrtxt[-(cursor)]}", curses.color_pair(13) | curses.A_REVERSE)
            else:
                stdscr.addstr(y, visible_cursor_x, f" ", curses.color_pair(13) | curses.A_REVERSE)
        elif literal:
            stdscr.addstr(y, visible_cursor_x, f"{repr(usrtxt)[-(cursor+1)]}", curses.color_pair(13) | curses.A_REVERSE)

        key = stdscr.getch()
        if key == 27:                                                           # ESC key
            return "", 0
        elif key == 10:                                                         # Enter/return key
            return usrtxt, 1
            # selected_indices = print_selected_indices()
            # if not selected_indices:
            #     selected_indices = [indexed_items[cursor_pos][0]]
            # full_values = [format_row_full(items[i], hidden_columns) for i in selected_indices]  # Use format_row_full for full data
            # # selected_data = [format_full_row(items[i]).strip() for i, selected in enumerate(selections) if selected and i not in hidden_columns]
            # if full_values:
            #     # os.system("notify-send " + "'" + '\t'.join(full_values).replace("'", "*") + "'")
            #     process = subprocess.Popen(usrtxt, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #     process.communicate(input='\n'.join(full_values).encode('utf-8'))
            # break
        elif key in [curses.KEY_BACKSPACE, "KEY_BACKSPACE", key == 263]:
            if cursor == 0:
                usrtxt = usrtxt[:-1]
            else:
                usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]

        elif key in [curses.KEY_LEFT, 2]:                                       # CTRL+B
            cursor = min(len(usrtxt), cursor + 1)

        elif key in [curses.KEY_RIGHT, 6]:                                      # CTRL-F
            cursor = max(0, cursor - 1)

        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)

        elif key in [4, 330]:                                                   # Ctrl+D, Delete
            if cursor != 0 and usrtxt != "":
                if cursor == 1:
                    usrtxt = usrtxt[:-(cursor)]
                else:
                    usrtxt = usrtxt[:-(cursor)] + usrtxt[-(cursor-1):]
                cursor = max(0, cursor - 1)
                
        elif key == 21 or key == "^U":                                          # CTRL+U
            if cursor == 0:
                usrtxt = ""
            else:
                usrtxt = usrtxt[-(cursor+1):]
            cursor = len(usrtxt)
        elif key == 11 or key == "^K":                                          # CTRL+K
            if cursor: usrtxt = usrtxt[:-cursor]
            cursor = 0

        elif key in [1, 262]:                                                          # CTRL+A (beginning)
            cursor = len(usrtxt)
            
        elif key in [5, 360]:                                                          # CTRL+E (end)
            cursor = 0

        # elif key in [23,8]:                                                     # Ctrl+BACKSPACE, CTRL+W
        #     if cursor == 0: tmp = usrtxt[::-1]
        #     else: tmp = usrtxt[:-cursor][::-1]
        #     index = tmp.find(" ")
        #     if index == -1: index = len(usrtxt)-1-cursor
        #
        #     cursor = len(usrtxt)

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
