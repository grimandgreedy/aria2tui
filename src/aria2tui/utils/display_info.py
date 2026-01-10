import os
from aria2tui.utils.aria2c_utils import *
from listpick.listpick_app import Picker
from aria2tui.utils.logging_utils import get_logger

logger = get_logger()


def display_info_menu(stdscr, gids, fnames, operation):
    logger.info(
        "display_info_menu called with gids=%s fnames=%s operation=%s",
        gids,
        fnames,
        getattr(operation, "name", None),
    )
    from aria2tui.ui.aria2tui_menu_options import download_info_menu

    items = [opt.name for opt in download_info_menu]
    highlights = [
        {
            "match": "^DL INFO",
            "field": 0,
            "color": 9,
        },
    ]

    info_data = {
        "items": items,
        "highlights": highlights,
        "max_selected": 1,
    }
    info_menu = Picker(stdscr, **info_data)
    s, o, f = info_menu.run()
    if s:
        operation = download_info_menu[s[0]]
        applyToDownloads(
            stdscr = stdscr,
            operation = operation,
            gids = gids,
            user_opts = "",
            fnames = fnames,
        )

def display_files(stdscr, gids, fnames, operation):
    """
    Get file info for a list of gids and display as rows in a Picker


    """
    logger.info(
        "display_files called with gids=%s fnames=%s operation=%s",
        gids,
        fnames,
        getattr(operation, "name", None),
    )
    responses = []
    for gid in gids:
        response = sendReq(getFiles(gid))
        responses.append(response)

    l = []
    for i, response in enumerate(responses):
        gid = gids[i]
        l += [["Task Name", fnames[i]]]
        l += [["GID", gid]]
        if "result" in response: 
            response = response["result"]
            for i, item in enumerate(response):
                l += [[f"  File {i+1}", ""]]
                for key, val in item.items():
                    if key in ["length", "completedLength"]:
                        l += [[f"   {key}", bytes_to_human_readable(val)]]
                    elif key == "uris":
                        l += [["", ""]]
                        l += [["   URIs", ""]]
                        for j, uri in enumerate(val):
                            l += [[f"     URI {j+1}", ""]]
                            for key2, val2 in uri.items():
                                l += [[f"        {key2}", val2]]
                        if len(val) == 0:
                            l += [["        -", "-"]]


                    else:
                        l += [[f"   {key}", val]]
        l += [["", ""]]
    highlights = [
        {
            "match": "^GID.*",
            "field": "all",
            "color": 11,
        },
        {
            "match": "^Task Name.*",
            "field": "all",
            "color": 11,
        }
    ]

    x = Picker(
        stdscr,
        items=l,
        title=operation.name,
        header=["Key", "Value"],
        reset_colours=False,
        cell_cursor=False,
        highlights=highlights,
    )
    x.run()
