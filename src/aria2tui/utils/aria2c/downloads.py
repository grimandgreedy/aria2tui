#!/bin/python
# -*- coding: utf-8 -*-
"""
downloads.py - Download management operations

Functions for adding downloads (URIs, torrents, mixed), retrying failed
downloads, and applying operations to download lists.

Author: GrimAndGreedy
License: MIT
"""

import os
import json
import subprocess
import tempfile
import curses
from typing import Tuple

from aria2tui.lib.aria2c_wrapper import input_file_accepted_options
from aria2tui.ui.aria2tui_form import run_form, FormViewerApp
from aria2tui.utils.aria_adduri import addDownloadFull
from aria2tui.utils.logging_utils import get_logger
from listpick import *
from listpick.listpick_app import *
from listpick.ui.keys import *
from .core import Operation, classify_download_string
from .format import flatten_data, process_dl_dict

logger = get_logger()


def input_file_lines_to_dict(lines: list[str]) -> Tuple[list[dict], list[str]]:
    """
    Converts lines to list of download dicts.

    Syntax
        a line that begins with a # will be interpreted as a comment
        a line that begins with a ! will be interpreted as an argstring
        a line with no leading space will be interpreted as a uri for a new download
        a line with leading spaces will be interpreted as an option to be added to the preceeding download
        if the line immediately follows the url and has leading spaces it will be interpreted as the filename
        any other line that succeeds the uri that has leading whitespace must have a = separating the option from the value

    Example
        ```
        !!
        # comment
        https://example.com/image.iso
            exampleimage.iso
            dir=/home/user/images/
        ```
        returns [{"uri": "http://example.com/image.iso", "dir": "/home/user/images"}], []
    """

    downloads = []
    download = {}
    argstrings = []

    for line in lines:
        stripped_line = line.rstrip()

        # Comment
        if line.strip().startswith("#") or line.strip() == "":
            continue

        # If the line has no leading spaces then it is a url to add
        if line.startswith("!"):
            argstrings.append(line)
        elif not line.startswith(" "):
            if download:
                downloads.append(download)
                download = {}
            download["uri"] = stripped_line
        elif "=" in line and line.startswith(" "):
            key, value = stripped_line.split("=", 1)
            download[key.strip()] = value.strip()
        elif len(download) == 1 and line.startswith(" "):
            download["out"] = line.strip()

    if download:
        downloads.append(download)

    return downloads, argstrings


def addUrisFull(
    url: str = "http://localhost", port: int = 6800, token: str = None
) -> Tuple[list[str], str]:
    """
    Add URIs to aria server.

    Returns a list of the gids added along with a string message (e.g., "0 dls added")
    """
    logger.info("addUrisFull called url=%s port=%s", url, port)
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import addDownload

    s = "# URL\n"
    s += "#    indented_option=value\n"
    s += "\n"
    s += "# https://docs.python.org/3/_static/py.png\n"
    s += "# magnet:?xt=urn:btih:...\n"
    s += "# https://docs.python.org/3/_static/py.svg\n#    out=pythonlogo.svg\n#    dir=/home/user/Downloads/\n#    pause=true\n"
    s += "#    user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1\n"
    s += "\n"
    s += "# The full list of DL options can be viewed here:\n"
    s += "# https://aria2.github.io/manual/en/html/aria2c.html#input-file\n\n\n"

    ## Create tmpfile
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls, argstrs = input_file_lines_to_dict(lines)

    valid_keys = input_file_accepted_options
    gids = []
    for dl in dls:
        if "uri" not in dl:
            continue

        uri = dl["uri"]
        download_options_dict = {
            key: val for key, val in dl.items() if key in valid_keys
        }
        if "dir" in download_options_dict:
            download_options_dict["dir"] = os.path.expandvars(
                os.path.expanduser(download_options_dict["dir"])
            )
        return_val, gid = addDownload(uri, download_options_dict=download_options_dict)
        if return_val:
            gids.append(gid)

    return gids, f"{len(gids)} download(s) added."


def addUrisAndPauseFull(
    url: str = "http://localhost", port: int = 6800, token: str = ""
) -> Tuple[list[str], str]:
    logger.info("addUrisAndPauseFull called url=%s port=%s", url, port)
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import pause, sendReq

    gids, message = addUrisFull(url=url, port=port, token=token)
    if gids:
        reqs = [json.loads(pause(gid)) for gid in gids]
        batch = sendReq(json.dumps(reqs).encode("utf-8"))
    return gids, f"{len(gids)} downloads added and paused."


def addTorrentsFull(
    url: str = "http://localhost", port: int = 6800, token: str = None
) -> Tuple[list[str], str]:
    """
    Open a prompt to add torrents to Aria2. The file will accept torrent file paths or magnet links.
    """
    logger.info("addTorrentsFull called url=%s port=%s", url, port)
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import addTorrent, sendReq, addDownload

    s = "# /path/to/file.torrent\n"
    s += "# magnet:?xt=...\n\n"

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls = []
    uris = []
    gids = []
    for line in lines:
        if line and line[0] in ["#", "!"] or line.strip() == "":
            pass
        elif len(line) > len("magnet:") and line[: len("magnet:")] == "magnet:":
            uris.append({"uri": line.strip()})
        else:
            dls.append({"path": os.path.expanduser(line.strip())})

    torrent_count = 0
    for dl in dls:
        try:
            jsonreq = addTorrent(dl["path"])
            resp = sendReq(jsonreq)
            if "result" in resp:
                gids.append(resp["result"])
            torrent_count += 1
        except Exception as e:
            logger.exception(
                "Error adding torrent from path '%s': %s", dl.get("path"), e
            )
            pass

    for dl in uris:
        uri = dl["uri"]
        logger.info("addTorrentsFull adding magnet/URI: %s", uri)
        return_val, gid = addDownload(uri=uri)
        if return_val:
            gids.append(gid)

    return (
        gids,
        f"{torrent_count} torrent file(s) added. {len(uris)} magnet link(s) added.",
    )


def addTorrentsFilePickerFull(
    url: str = "http://localhost", port: int = 6800, token: str = None
) -> Tuple[list[str], str]:
    """Open file picker to add torrents to Aria2."""
    logger.info("addTorrentsFilePickerFull called url=%s port=%s", url, port)
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import addTorrent, sendReq

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        subprocess.run(f"yazi --chooser-file={tmpfile.name}", shell=True)
        lines = tmpfile.readlines()

    dls = []
    gids = []
    if lines:
        for line in lines:
            if line.strip():
                dls.append({"path": os.path.expanduser(line.decode("utf-8").strip())})

    torrent_count = 0
    for dl in dls:
        try:
            jsonreq = addTorrent(dl["path"])
            sendReq(jsonreq)
            torrent_count += 1
        except:
            pass

    return gids, f"{torrent_count}/{len(dls)} torrent file(s) added."


def addDownloadTasksForm() -> str:
    """Add a download using form interface."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import addDownload, pause, sendReq, getGlobalOption

    try:
        req = getGlobalOption()
        response = sendReq(req)["result"]
        current_options = response
    except Exception as e:
        return str(e)

    form_dict = {
        "Basic Download Options": {
            "URL": ("", "text"),
            "out": ("", "text"),
            # "dir": (os.path.expanduser("~/Downloads"), "file"),
            "dir": (os.path.expanduser(current_options["dir"]), "file"),
            "pause": ("false", "cycle", ["true", "false"]),
        },
        "Advanced Options": {
            "split": current_options.get("split", ""),
            "max-connection-per-server": current_options.get(
                "max-connection-per-server", ""
            ),
            "user-agent": current_options.get("user-agent", ""),
            "allow-overwrite": (
                current_options.get("allow-overwrite", "false"),
                "cycle",
                ["true", "false"],
            ),
        },
    }

    result_dict, saved = run_form(form_dict)

    # If user didn't save, return early
    if not saved:
        return "Download cancelled"

    options = {}
    for _, fields in result_dict.items():
        for label, value in fields.items():
            if value:
                options[label] = value

    if "URL" not in options or not options["URL"]:
        return "Error: URL is required"

    uri = options.pop("URL")

    if "dir" in options:
        options["dir"] = os.path.expandvars(os.path.expanduser(options["dir"]))

    should_pause = options.pop("pause", "false").lower() in ["true", "yes", "1"]

    download_options_dict = {key: val for key, val in options.items() if val}
    return_val, gid = addDownload(uri=uri, download_options_dict=download_options_dict)

    if not return_val:
        return f"Error: Failed to add download"

    if should_pause:
        pause_req = pause(gid)
        sendReq(pause_req)
        return f"Download added and paused. GID: {gid}"

    return f"Download added. GID: {gid}"


def process_downloads_list(dls_list: list[dict]) -> Tuple[list[str], str]:
    """
    Process a list of download dictionaries and add them to aria2.

    This function handles both URIs (HTTP, FTP, Magnet, Metalink) and torrent files.

    Args:
        dls_list: List of download dictionaries from input_file_lines_to_dict

    Returns:
        Tuple of (gids: list of successful download GIDs, message: status message)
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import addTorrent, sendReq, addDownload

    valid_keys = input_file_accepted_options
    dls = []
    uris = []
    gids = []

    for dl in dls_list:
        if "uri" not in dl:
            continue

        dl_type = classify_download_string(dl["uri"])
        if dl_type in ["HTTP", "FTP", "Magnet", "Metalink"]:
            download_options_dict = {
                key: val for key, val in dl.items() if key in valid_keys
            }
            if "dir" in download_options_dict:
                download_options_dict["dir"] = os.path.expandvars(
                    os.path.expanduser(download_options_dict["dir"])
                )
            uris.append({"uri": dl["uri"], "options": download_options_dict})
        else:
            dls.append({"path": os.path.expanduser(dl["uri"])})

    torrent_count = 0
    for dl in dls:
        try:
            jsonreq = addTorrent(dl["path"])
            resp = sendReq(jsonreq)
            torrent_count += 1
            if "result" in resp:
                gids.append(resp["result"])
        except:
            pass

    for dl in uris:
        uri = dl["uri"]
        options = dl["options"]
        return_val, gid = addDownload(uri=uri, download_options_dict=options)
        if return_val:
            gids.append(gid)

    if len(uris) and torrent_count:
        msg = f"{len(uris)} direct download(s) added. {torrent_count} torrent(s) added."
    elif len(uris):
        msg = f"{len(uris)} direct download(s) added."
    elif torrent_count:
        msg = f"{torrent_count} torrent(s) added."
    else:
        msg = ""
    return gids, msg


def addDownloadsAndTorrentsFull(
    url: str = "http://localhost", port: int = 6800, token: str = None
) -> Tuple[list[str], str]:
    """Add mixed downloads (URIs, magnets, torrents) via editor."""
    s = "# Add http(s) links, magnet links, metalinks, or torrent files (by path).\n"
    s += "# URL\n"
    s += "#    indented_option=value\n"
    s += "\n"
    s += "# https://docs.python.org/3/_static/py.png\n"
    s += "# magnet:?xt=urn:btih:...\n"
    s += "# /path/to/file.torrent\n"
    s += "# https://docs.python.org/3/_static/py.svg\n#    out=pythonlogo.svg\n#    dir=/home/user/Downloads/\n#    pause=true\n"
    s += "#    user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1\n"
    s += "\n"
    s += "# The full list of DL options can be viewed here:\n"
    s += "# https://aria2.github.io/manual/en/html/aria2c.html#input-file\n\n\n"

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls_list, argstrs = input_file_lines_to_dict(lines)

    return process_downloads_list(dls_list)


def addDownloadsAndTorrentsAndPauseFull(
    url: str = "http://localhost", port: int = 6800, token: str = ""
) -> Tuple[list[str], str]:
    """Add mixed downloads and pause them."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import pause, sendReq

    gids, message = addDownloadsAndTorrentsFull(url=url, port=port, token=token)
    if gids:
        reqs = [json.loads(pause(gid)) for gid in gids]
        batch = sendReq(json.dumps(reqs).encode("utf-8"))
    return gids, f"{len(gids)} download(s) added and paused."


def retryDownloadFull(
    gid: str, url: str = "http://localhost", port: int = 6800, token: str = ""
) -> str:
    """Retry a failed download by creating a new download with same options."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import tellStatus, getOption, sendReq, addDownload

    status = sendReq(tellStatus(gid))
    options = sendReq(getOption(gid))

    if "bittorrent" not in status["result"]:
        uri = status["result"]["files"][0]["uris"][0]["uri"]
        dl = options["result"].copy()
        if "dir" in status["result"]:
            dl["dir"] = status["result"]["dir"]

        return_val, gid = addDownload(uri=uri, download_options_dict=dl)
        if return_val:
            return gid
        else:
            return ""

    return ""


def retryDownloadAndPauseFull(
    gid: str, url: str = "http://localhost", port: int = 6800, token: str = ""
) -> str:
    """Retry a failed download and pause it."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import tellStatus, getOption, sendReq, addDownload

    status = sendReq(tellStatus(gid))
    options = sendReq(getOption(gid))

    if "bittorrent" not in status["result"]:
        uri = status["result"]["files"][0]["uris"][0]["uri"]
        dl = options["result"].copy()
        if "dir" in status["result"]:
            dl["dir"] = status["result"]["dir"]

        dl["pause"] = "true"
        return_val, gid = addDownload(uri=uri, download_options_dict=dl)
        if return_val:
            return gid
        else:
            return ""

    return ""


def retryDownloadWithModifiedOptions(gid: str) -> str:
    """
    Retry a failed download with modified options using form interface.

    Shows a form to modify download options, then retries the download
    with the modified options.

    Args:
        gid: GID of the download to retry

    Returns:
        Status message with new GID or error message
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import tellStatus, getOption, sendReq, addDownload
    from aria2tui.ui.aria2tui_form import run_form

    if not gid:
        return "Error: No GID provided"

    try:
        # Get current download status and options
        status = sendReq(tellStatus(gid))
        options = sendReq(getOption(gid))

        # Only works for non-bittorrent downloads
        if "bittorrent" in status["result"]:
            return "Error: Cannot retry BitTorrent downloads with this method"

        # Get the URI from the download
        uri = status["result"]["files"][0]["uris"][0]["uri"]
        current_options = json.loads(json.dumps(options["result"]))

        # Add directory from status if available
        if "dir" in status["result"]:
            current_options["dir"] = status["result"]["dir"]

    except Exception as e:
        return f"Error getting download info: {str(e)}"

    # Organize options into sections for the form
    from aria2tui.utils.aria2c.options import _organize_options_into_sections

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

    form_dict["Basic Options"]["pause"] = ("false", "cycle", ["false", "true"])

    # Run the form and get results
    result_dict, saved = run_form(form_dict)

    # If user didn't save, return early
    if not saved:
        return "Retry cancelled"

    # Flatten the result back to a single dict
    loaded_options = {}
    for section, fields in result_dict.items():
        for label, value in fields.items():
            loaded_options[label] = value

    # Expand directory path if present
    if "dir" in loaded_options:
        loaded_options["dir"] = os.path.expandvars(
            os.path.expanduser(loaded_options["dir"])
        )

    # Add the download with modified options
    try:
        return_val, new_gid = addDownload(uri=uri, download_options_dict=loaded_options)
        if return_val:
            return f"Download retried successfully. New GID: {new_gid}"
        else:
            return "Error: Failed to retry download"
    except Exception as e:
        return f"Error retrying download: {str(e)}"


def applyToDownloads(
    stdscr: curses.window,
    operation: Operation,
    gids: list = [],
    user_opts: str = "",
    fnames: list = [],
) -> None:
    """Apply an operation to a list of downloads."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import sendReq, changePosition

    if len(gids) == 0:
        return None

    result = []
    if operation.accepts_gids_list:
        logger.info("Running dl operation on list of downloads")
        result = operation.function(
            stdscr=stdscr,
            gids=gids,
            fnames=fnames,
            operation=operation,
            function_args=operation.function_args,
        )
        if operation.send_request:
            result = sendReq(result)
    else:
        for i, gid in enumerate(gids):
            logger.info("Running dl operation on single download")
            try:
                if operation.name == "Change Position in Queue":
                    position = int(user_opts) if user_opts.strip().isdigit() else 0
                    result_part = changePosition(gid, pos=position)
                else:
                    result_part = operation.function(
                        stdscr=stdscr,
                        gid=gid,
                        fname=fnames[i],
                        operation=operation,
                        function_args=operation.function_args,
                    )

                if operation.send_request:
                    result_part = sendReq(result_part)
                result.append(result_part)
            except Exception as e:
                logger.error(f"Error when applying download operation {e}")

    if operation.picker_view:
        l = []
        for i, response in enumerate(result):
            l += [[gids[i], "------"]]
            if "result" in response:
                response = response["result"]
            response = process_dl_dict(response)
            l += [[key, val] for key, val in flatten_data(response).items()]
        x = Picker(
            stdscr,
            items=l,
            search_query="function",
            title=operation.name,
            header=["Key", "Value"],
            reset_colours=False,
            cell_cursor=False,
        )
        x.run()
    elif operation.view:
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmpfile:
            for i, _ in enumerate(result):
                tmpfile.write(
                    f"{'*' * 50}\n{str(i) + ': ' + gids[i]:^50}\n{'*' * 50}\n"
                )
                tmpfile.write(json.dumps(result, indent=4))
            tmpfile_path = tmpfile.name
        cmd = rf"nvim -c 'set commentstring=#\ %s' {tmpfile_path}"
        process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    elif operation.form_view:
        # Show structured results in the read-only form viewer
        if not result:
            stdscr.clear()
            return

        form_dict = {}

        for i, response in enumerate(result):
            # Use the GID as section name when available
            section_name = gids[i] if i < len(gids) else f"Item {i}"

            # Unwrap JSON-RPC style responses
            if isinstance(response, dict) and "result" in response:
                payload = response["result"]
            else:
                payload = response

            # Try to normalize and flatten the payload; fall back to string
            try:
                processed = process_dl_dict(payload)
                flat = flatten_data(processed)
            except Exception:
                flat = {"value": json.dumps(payload, indent=2, default=str)}

            section_fields = {}
            for key, val in flat.items():
                section_fields[str(key)] = str(val)

            form_dict[str(section_name)] = section_fields

        def is_string_dict(d):
            for key, val in d.items():
                if type(val) != type(""):
                    return False
            return True

        if is_string_dict(form_dict):
            form_dict = {operation.name: form_dict}

        viewer = FormViewerApp(stdscr, form_dict)
        viewer.run()

    stdscr.clear()


def remove_downloads(gids):
    """Remove downloads based on their status."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import tellStatus, sendReq, remove, removeDownloadResult

    for gid in gids:
        try:
            status_resp = sendReq(tellStatus(gid))
            status = status_resp["result"]["status"]

            if status in ["active", "waiting", "paused"]:
                sendReq(remove(gid))
            elif status in ["complete", "error", "removed"]:
                sendReq(removeDownloadResult(gid))
        except Exception:
            try:
                sendReq(removeDownloadResult(gid))
            except:
                pass
