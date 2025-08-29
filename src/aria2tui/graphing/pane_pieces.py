from listpick.pane.pane_utils import escape_ansi
from aria2tui.utils.aria2c_utils import bytes_to_human_readable
import curses
from datetime import datetime


def right_split_piece_progress(stdscr, x, y, w, h, state, row, cell, past_data: list = [], data: list = [], test: bool = False):
    """
    Display a graph of the data in right pane.

    data[0] = x_vals
    data[1] = y_vals
    data[2] = id
    """
    if test: return True

    # Title
    title = "DL Pieces"
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

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
        header = state["header"]
        gid_index, fname_index, status_index = header.index("GID"), header.index("Name"), header.index("Status")

        gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
        fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]
        status  = state["indexed_items"][state["cursor_pos"]][1][status_index]
    except:
        return None

    # Display file name
    if len(fname) < w:
        fname = f"{fname:^{w}}"
    else:
        fname = f" {fname}"
    stdscr.addstr(y+1, x+1, fname[:w-1], curses.color_pair(state["colours_start"]+2) | curses.A_BOLD | curses.A_UNDERLINE)


    if data in [[], {}, None, ""]:
        return None


    disp_width = w -5
    split_bitfield = [data[i*disp_width: (i+1)*disp_width] for i in range(len(data)//disp_width + 1)]
    # stdscr.addstr(y+2, x+w - 8, f"{disp_width}x{len(split_bitfield)}")
    for i, s in enumerate(split_bitfield):
        if 3+i > h-2:
            stdscr.addstr(y+3+i-1, x+w-3-3, "...")
            break
        stdscr.addstr(y+3+i, x+3, s[:w-2])

    return []


def get_dl_pieces(data, state) -> str:
    """
    Get a bitstring indicating which pieces of the download have finished.
    """
    from aria2tui.utils import aria2c_utils

    if len(state["indexed_items"]) == 0:
        return ""

    try:
        header = state["header"]
        gid_index, fname_index = header.index("GID"), header.index("Name")

        gid = state["indexed_items"][state["cursor_pos"]][1][gid_index]
        fname  = state["indexed_items"][state["cursor_pos"]][1][fname_index]
        req = aria2c_utils.tellStatus(gid)
        info = aria2c_utils.sendReq(req)
        bitfield = info["result"]["bitfield"]

        status = info["result"]["status"]

        s = ""
        if status == "complete":
            return "■"*len(bitfield)

        for c in bitfield:
            if c == "f": s+= "■"
            elif c == "0": s+= "□"
            else: s += "◩"

        return s
    except:

        return ""
