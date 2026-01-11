#!/bin/python
# -*- coding: utf-8 -*-
"""
options.py - Options and settings management

Functions for modifying download options through various interfaces
(dialogs, pickers, forms) and managing file selection for downloads.

Author: GrimAndGreedy
License: MIT
"""

import curses
import json
import subprocess
import tempfile
import pyperclip

from aria2tui.utils.logging_utils import get_logger
from aria2tui.ui.aria2tui_form import run_form
from listpick import *
from listpick.listpick_app import *
from listpick.ui.keys import *
from .format import flatten_data, unflatten_data, bytes_to_human_readable

logger = get_logger()


def changeOptionDialog(gid:str) -> str:
    """ Change the option(s) for the download. """
    logger.info("changeOptionDialog called gid=%s", gid)
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, sendReq, changeOption

    try:
        req = getOption(str(gid))
        response = sendReq(req)["result"]
        current_options = json.loads(json.dumps(response))
    except Exception as e:
        return str(e)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        for key, value in current_options.items():
            f.write(f"{key}={value}\n")

        temp_file = f.name

    cmd = rf"nvim  -i NONE -c 'set commentstring=#\ %s' {temp_file}"
    subprocess.run(cmd, shell=True)

    loaded_options = {}
    with open(temp_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            if "=" in line:
                ind = line.index("=")
                key, value = line[:ind], line[ind+1:]
                loaded_options[key.strip()] = value.strip()

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if key in loaded_options and current_options[key] != loaded_options.get(key, None))

    reqs = []
    for key in keys_with_diff_values:
        reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."


def changeOptionBatchDialog(gids:list) -> str:
    """ Change the option(s) for the download. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, sendReq, changeOption

    if len(gids) == 0: return ""
    gid = gids[0]

    reps = []

    try:
        req = getOption(str(gid))
        response = sendReq(req)["result"]
        current_options = json.loads(json.dumps(response))
    except Exception as e:
        return str(e)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        for key, value in current_options.items():
            f.write(f"{key}={value}\n")

        temp_file = f.name

    cmd = rf"nvim -c 'set commentstring=#\ %s' -i NONE {temp_file}"
    subprocess.run(cmd, shell=True)

    loaded_options = {}
    with open(temp_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            if "=" in line:
                ind = line.index("=")
                key, value = line[:ind], line[ind+1:]
                loaded_options[key.strip()] = value.strip()

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if key in loaded_options and current_options[key] != loaded_options.get(key, None))

    reqs = []
    for gid in gids:
        for key in keys_with_diff_values:
            reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."


def changeOptionPicker(stdscr: curses.window, gid:str) -> str:
    """ Change the option(s) for the download. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, sendReq, changeOption

    if not gid: return "0 options changed"
    try:
        req = getOption(str(gid))
        response = sendReq(req)["result"]
        current_options = json.loads(json.dumps(response))
    except Exception as e:
        return str(e)

    flattened_json = flatten_data(response)
    flattened_json = [[key,val] for key, val in flattened_json.items()]
    x = Picker(
        stdscr,
        items=flattened_json,
        header=["Key", "Value"],
        title=f"Change Options for gid={gid}",
        selected_column=1,
        editable_columns=[False, True],
        keys_dict=edit_menu_keys,
        startup_notification="'e' to edit cell. 'E' to edit selected cells in nvim. 'q' to exit. 'Return' to submit changes.",
        reset_colours=False,
    )
    selected_indices, opts, function_data = x.run()
    if not selected_indices: return "0 options changed"
    flattened_json = function_data["items"]
    unflattened_json = unflatten_data({row[0]: row[1] for row in flattened_json})
    loaded_options = unflattened_json

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if current_options[key] != loaded_options.get(key, None))

    reqs = []
    for key in keys_with_diff_values:
        reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."


def _organize_options_into_sections(options: dict) -> dict:
    """
    Organize aria2 options into logical sections for the form interface.

    Args:
        options: Flat dictionary of aria2 options

    Returns:
        Dictionary organized by sections with nested option dictionaries
    """
    # Define section categorization
    basic_options = ["out", "dir", "input-file", "log", "max-concurrent-downloads",
                     "check-integrity", "continue", "all-proxy", "all-proxy-user",
                     "all-proxy-passwd"]

    connection_options = ["max-connection-per-server", "min-split-size", "split",
                          "max-tries", "retry-wait", "timeout", "connect-timeout",
                          "max-file-not-found", "max-overall-download-limit",
                          "max-download-limit", "lowest-speed-limit"]

    http_ftp_options = ["http-proxy", "http-proxy-user", "http-proxy-passwd",
                        "https-proxy", "https-proxy-user", "https-proxy-passwd",
                        "ftp-proxy", "ftp-proxy-user", "ftp-proxy-passwd",
                        "http-user", "http-passwd", "ftp-user", "ftp-passwd",
                        "user-agent", "referer", "load-cookies", "save-cookies",
                        "header", "use-head", "enable-http-pipelining",
                        "enable-http-keep-alive"]

    bittorrent_options = ["bt-enable-lpd", "bt-max-peers", "bt-request-peer-speed-limit",
                          "bt-max-open-files", "bt-seed-unverified", "bt-save-metadata",
                          "bt-tracker", "bt-exclude-tracker", "enable-dht", "enable-peer-exchange",
                          "seed-ratio", "seed-time", "max-upload-limit", "max-overall-upload-limit",
                          "bt-require-crypto", "bt-min-crypto-level", "follow-torrent",
                          "pause-metadata", "bt-detach-seed-only"]

    form_dict = {
        "Basic Options": {},
        "Connection Options": {},
        "HTTP/FTP Options": {},
        "BitTorrent Options": {},
        "Advanced Options": {}
    }

    # Categorize options
    for key, value in options.items():
        if key in basic_options:
            form_dict["Basic Options"][key] = value
        elif key in connection_options:
            form_dict["Connection Options"][key] = value
        elif key in http_ftp_options:
            form_dict["HTTP/FTP Options"][key] = value
        elif key in bittorrent_options:
            form_dict["BitTorrent Options"][key] = value
        else:
            form_dict["Advanced Options"][key] = value

    # Remove empty sections
    form_dict = {k: v for k, v in form_dict.items() if v}

    return form_dict


def changeOptionsBatchPicker(stdscr: curses.window, gids:str) -> str:
    """ Change the option(s) for the download using form interface. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, sendReq, changeOption

    if len(gids) == 0: return ""
    gid = gids[0]
    try:
        req = getOption(str(gid))
        response = sendReq(req)["result"]
        current_options = json.loads(json.dumps(response))
    except Exception as e:
        return str(e)

    # Convert flat options dict to form_dict format with sections
    # Group options by category for better organization
    form_dict = _organize_options_into_sections(current_options)

    # Convert boolean fields to cycle type and dir to file picker
    for section in form_dict:
        for key, value in list(form_dict[section].items()):
            if key == "dir":
                # Convert dir field to file picker type
                form_dict[section][key] = (value, "file")
            elif value.lower() in ["true", "false"]:
                # Convert boolean fields to cycle type
                form_dict[section][key] = (value, "cycle", ["true", "false"])

    # Run the form and get results
    result_dict = run_form(form_dict)

    # Flatten the result back to compare with original
    loaded_options = {}
    for section, fields in result_dict.items():
        for label, value in fields.items():
            loaded_options[label] = value

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if current_options[key] != loaded_options.get(key, None))

    reqs = []
    for gid in gids:
        for key in keys_with_diff_values:
            reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."


def changeFilenamePicker(stdscr: curses.window, gid:str) -> str:
    """ Change the filename """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, sendReq, changeOption

    if not gid: return "0 options changed"
    try:
        req = getOption(str(gid))
        response = sendReq(req)["result"]
        current_options = json.loads(json.dumps(response))
    except Exception as e:
        return str(e)

    flattened_json = flatten_data(response)
    flattened_json = [[key,val] for key, val in flattened_json.items() if key == "out"]
    x = Picker(
        stdscr,
        items=flattened_json,
        header=["Key", "Value"],
        title=f"Change Options for gid={gid}",
        selected_column=1,
        editable_columns=[False, True],
        keys_dict=edit_menu_keys,
        startup_notification="'e' to edit cell. 'E' to edit selected cells in nvim. 'q' to exit. 'Return' to submit changes.",
        disable_file_close_warning=True,
        reset_colours=False,
    )
    selected_indices, opts, function_data = x.run()
    if not selected_indices: return "0 options changed"
    flattened_json = function_data["items"]
    unflattened_json = unflatten_data({row[0]: row[1] for row in flattened_json})
    loaded_options = unflattened_json

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if current_options[key] != loaded_options.get(key, None) and key == "out")

    pyperclip.copy(repr(keys_with_diff_values))
    reqs = []
    for key in keys_with_diff_values:
        reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."

def changeFilenameForm(stdscr: curses.window, gid:str, fname:string) -> str:
    """Change the filename using the aria2tui form interface."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, sendReq, changeOption

    if not gid:
        return "0 options changed"

    current_out = fname

    form_dict = {
        "Filename": {
            "out": (current_out, "text"),
        }
    }

    result_dict = run_form(form_dict)

    # Safely extract the new filename from the result
    new_out = ""
    if isinstance(result_dict, dict):
        section = result_dict.get("Filename", {})
        if isinstance(section, dict):
            new_out = section.get("out", "")

    # If nothing changed, do not send a request
    if new_out == current_out:
        return "0 options changed"

    # Apply the updated filename via aria2 changeOption
    try:
        reqs = [json.loads(changeOption(gid, "out", new_out))]
        batch = sendReq(json.dumps(reqs).encode("utf-8"))
    except Exception as e:
        return str(e)

    return "1 filename changed."


def download_selected_files(stdscr, gids):
    """
    Present the user with files for each given GID and allow them to select which files should be downloaded.

    Args:
        stdscr (ncurses.window): The main window for ncurses application.
        gids (list): A list of group IDs for which files are to be selected.

    Returns:
        None
    """

    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getFiles, sendReq, getOption, changeOption

    for gid in gids:
        req = getFiles(gid)
        files_dict = sendReq(req)["result"]
        options = sendReq(getOption(gid))
        dir = options["result"]["dir"]
        files = [f["path"].replace(dir, "") for f in files_dict]
        sizes = [bytes_to_human_readable(f["length"]) for f in files_dict]
        selected_indices = [i for i in range(len(files_dict)) if files_dict[i]['selected'] == 'true']
        selections = {i: f['selected'] == "true" for i, f in enumerate(files_dict)}

        file_progress = []
        for i in range(len(files)):
            done = files_dict[i]["completedLength"]
            total = files_dict[i]["length"]
            if total == '0':
                progress = "0%"
            else:
                progress = f"{100*int(done)/int(total):.1f}%"

            file_progress.append(progress)

        items = [[files[i], sizes[i], file_progress[i]] for i in range(len(files))]
        header = ["File", "Size", "Progress"]

        # from listpick.ui.keys import picker_keys as pk
        # from copy import copy
        # pk = copy(pk)
        # pk["edit"] = [ord('e')]
        selectionsPicker = Picker(
            stdscr,
            items=items,
            header=header,
            selections=selections,
            cell_cursor=False,
            editable_columns=[True, False],
            editable_by_default=True,
            keys_dict=picker_keys,
            startup_notification="Selected files will be downloaded. Non-selected will be skipped. 'e' to edit filename. 'E' to edit selected cells in nvim. 'q' to exit. 'Return' to submit changes.",
            selected_char = "☒",
            unselected_char = "☐",
            selecting_char = "☒",
            deselecting_char = "☐",
        )
        modified_selections, options, function_data = selectionsPicker.run()
        if selected_indices != modified_selections and function_data["last_key"] != ord("q"):
            selected = ",".join([str(x+1) for x in modified_selections])
            try:
                js_req = changeOption(gid, "select-file", selected)
                resp = sendReq(js_req)
            except:
                pass
        filename_changes = False
        for i, row in enumerate(selectionsPicker.items):
            if files[i] == row[0]: continue
            # If the values differ then a name has been changed

            filename_changes = True
            js_req = changeOption(gid, "index-out", f"{i+1}={row[0]}")
            resp = sendReq(js_req)
        if filename_changes:
            js_req = changeOption(gid, "check-integrity", "true")
            resp = sendReq(js_req)
