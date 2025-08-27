from listpick.pane.pane_utils import escape_ansi
from aria2tui.utils.aria2c_utils import bytes_to_human_readable
import curses

def right_split_dl_graph(stdscr, x, y, w, h, state, row, cell, past_data: list = [], data: list = [], test: bool = False):
    """
    Display a graph of the data in right pane.

    data[0] = x_vals
    data[1] = y_vals
    data[2] = id
    """
    if test: return True

    # Title
    title = "Graph"
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

    # Separator
    for j in range(h):
        stdscr.addstr(j+y, x, ' ', curses.color_pair(state["colours_start"]+16))

    try:
        import plotille as plt
    except:
        s = f"No module named 'plotille'"
        stdscr.addstr(y+2, x+2, s[:w-2])
        return None


    # x_vals, y_vals = list(range(100)), [x**2 for x in range(100)]
    if data in [[], {}, None]:
        return None


    header = state["header"]
    gid_index, fname_index, status_index = header.index("GID"), header.index("Name"), header.index("Status")

    gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
    fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]
    status  = state["indexed_items"][state["cursor_pos"]][1][status_index]

    # if status == "paused": return None

    # Display file name
    if len(fname) < w:
        fname = f"{fname:^{w}}"
    stdscr.addstr(y+1, x+2, fname[:w-2])

    # We need at least 23 chars of width and at least 10 rows to display a meaningful graph.
    if w <= 23 or h < 10:
        stdscr.addstr(y+3, x+2, f'{"Pane"[:w-2]:^{w-2}}')
        stdscr.addstr(y+4, x+2, f'{"Too"[:w-2]:^{w-2}}')
        stdscr.addstr(y+5, x+2, f'{"Small"[:w-2]:^{w-2}}')
        return None

    x_vals, dl_speeds, ul_speeds = data[0], data[1], data[2]
    graph_str = get_graph_string(x_vals, dl_speeds, ul_speeds, width=w-3-7, height=h-4)

    for i, s in enumerate(graph_str.split("\n")):
        s = escape_ansi(s)
        s = s[3:]
        stdscr.addstr(y+3+i, x+2, s[:w-2])

    return []


def get_dl_data(data, state):
    """
    Get dl speed and add it to data[1]

    data[0]: 0,1,2,...,n+1
    data[1]: dl_speed_at_0, dl_speed_at_1, ...
    data[2]: ul_speed_at_0, ul_speed_at_1, ...
    data[3]: row id
    """
    from aria2tui.utils import aria2c_utils

    if len(state["indexed_items"]) == 0:
        return [[0], [0], [0], -1]

    header = state["header"]
    gid_index, fname_index = header.index("GID"), header.index("Name")

    gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
    fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]

    req = aria2c_utils.tellStatus(gid)
    info = aria2c_utils.sendReq(req)
    dl = info["result"]["downloadSpeed"]
    ul = info["result"]["uploadSpeed"]

    dl, ul = int(dl), int(ul)

    if data in [[], {}, None] or data[-1] != gid:
        return [[0], [dl], [ul], gid]
    else:
        data[0].append(data[0][-1]+1)
        data[1].append(dl)
        data[2].append(ul)
    return data



def get_graph_string(x_vals, dl_speeds, ul_speeds, width=50, height=20, title=None, x_label=None, y_label=None):
    """ Generate a graph of x_vals, y_vals using plotille"""

    import plotille as plt
    # Create a figure and axis object using plotille
    fig = plt.Figure()
    
    # Plot the data on the figure
    fig.plot(x_vals, dl_speeds)
    fig.plot(x_vals, ul_speeds)
    
    # Set the dimensions of the graph
    fig.width = width-10
    fig.height = height-4
    fig.x_ticks_fkt = lambda x, _: f"{int(x)}s"
    fig.y_ticks_fkt = lambda y, _: bytes_to_human_readable(int(y))
    fig.set_y_limits(min_=0)
    fig.set_x_limits(min_=0)


    fig.text([x_vals[-1]], [dl_speeds[0]], ['Dn'])
    fig.text([x_vals[0]], [ul_speeds[0]], ['Up'])
    
    # Set the title and labels if provided
    if title:
        fig.title = title
    if x_label:
        fig.xlabel = x_label
    if y_label:
        fig.ylabel = y_label
    
    # Generate the ASCII art of the graph
    ascii_art = str(fig.show())
    
    return ascii_art
