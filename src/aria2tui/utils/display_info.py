import os
from aria2tui.utils.aria2c_utils import *
from listpick.listpick_app import Picker
import pyperclip

def display_files(stdscr, gids, fnames, operation):
    """
    Get file info for a list of gids and display as rows in a Picker


    """
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
