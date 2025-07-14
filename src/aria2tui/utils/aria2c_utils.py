#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2c_utils.py

Author: GrimAndGreedy
License: MIT
"""

import curses
import os
import subprocess
import toml
from urllib import request as rq
import json
import sys
sys.path.append("..")
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# os.chdir("../../..")
import tempfile
import tabulate
from typing import Callable, Tuple


from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria_adduri import addDownloadFull

from listpick import *
from listpick.listpick_app import *
from listpick.ui.keys import *

def testConnectionFull(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests if we can connect to the url and port. """
    url = f'{url}:{port}/jsonrpc'
    try:
        with rq.urlopen(url, listMethods()) as c:
            response = c.read()
        return True
    except:
        return False

def testAriaConnectionFull(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests the connection to the Aria2 server. In particular we test if our token works to get protected data. """
    url = f'{url}:{port}/jsonrpc'
    try:
        getVersion()
        with rq.urlopen(url, getVersion()) as c:
            response = c.read()
        return True
    except:
        return False

def te(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests the connection to the Aria2 server. """
    url = f'{url}:{port}/jsonrpc'
    try:
        with rq.urlopen(url, listMethods()) as c:
            response = c.read()
        return True
    except:
        return False

def getOptionAndFileInfo(gids: list[str]) -> Tuple[list, list]:
    """ Get option and file info for each GID. Used for fetching download data for Picker rows. """
    options_batch = []
    files_info_batch = []
    # for i in range(len(js_rs["result"])):
    for gid in gids:
        # gid = js_rs["result"][i]['gid']
        options_batch.append(json.loads(getOption(gid)))
        files_info_batch.append(json.loads(getFiles(gid)))
        
    all_reqs = sendReq(json.dumps(options_batch+files_info_batch).encode('utf-8'))

    options_batch = all_reqs[:len(gids)]
    files_info_batch = all_reqs[len(gids):]

    return options_batch, files_info_batch

def dataToPickerRows(dls, options_batch, files_info_batch, show_pc_bar: bool = True):
    items = []
    for i, dl in enumerate(dls):
        try:
            options = options_batch[i]
            files_info = files_info_batch[i]
            gid = dl['gid']
            pth = options["result"]["dir"]
            if "out" in options["result"]:
                fname = options["result"]["out"]
            else:
                orig_path = dl['files'][0]['path']
                fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            dltype = "direct"
            try:
                if "bittorrent" in dl:
                    dltype = "torrent"
                    fname = dl["bittorrent"]["info"]["name"]
            except: pass
            status = dl['status']

            size = 0
            for file in files_info['result']:
                if 'length' in file:
                    size += int(file['length'])
            # size = int(dl['files'][0]['length'])
            completed = 0
            for file in files_info['result']:
                if 'completedLength' in file:
                    completed += int(file['completedLength'])
            # completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left: time_left_s = convert_seconds(time_left)
            else: time_left_s = ""

            try:
                uri = files_info["result"][0]["uris"][0]["uri"]
            except:
                uri = ""

            row = [str(i), status, fname, format_size(size), format_size(completed), f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left_s, pth, dltype, uri, gid]
            if show_pc_bar: row.insert(5, pc_bar)
            items.append(row)
        except:
            pass

    header = ["", "Status", "Name", "Size", "Done", "%", "Speed", "Time", "DIR", "Type", "URI", "GID"]
    if show_pc_bar: header.insert(5, "%")
    return items, header

def getQueue(show_pc_bar: bool = True) -> Tuple[list[list[str]], list[str]]:
    """ Retrieves download queue and corresponding header from aria2 over rpc. """
    js_rs = sendReq(tellWaiting())
    gids = [dl["gid"] for dl in js_rs["result"]]
    options_batch, files_info_batch = getOptionAndFileInfo(gids)

    items, header = dataToPickerRows(js_rs["result"], options_batch, files_info_batch, show_pc_bar)

    return items, header


def getStopped(show_pc_bar: bool = True) -> Tuple[list[list[str]], list[str]]:
    """ Retrieves stopped downloads and corresponding header from aria2 over rpc. """
    js_rs = sendReq(tellStopped())
    gids = [dl["gid"] for dl in js_rs["result"]]
    options_batch, files_info_batch = getOptionAndFileInfo(gids)

    items, header = dataToPickerRows(js_rs["result"], options_batch, files_info_batch, show_pc_bar)

    for item in items: 
        item[0] = ""                # Remove indices; only useful for queue numbering
        

    return items[::-1], header


def getActive(show_pc_bar: bool = True) -> Tuple[list[list[str]], list[str]]:
    """ Retrieves active downloads and corresponding header from aria2 over rpc. """

    js_rs = sendReq(tellActive())
    gids = [dl["gid"] for dl in js_rs["result"]]
    options_batch, files_info_batch = getOptionAndFileInfo(gids)

    items, header = dataToPickerRows(js_rs["result"], options_batch, files_info_batch, show_pc_bar)

    rem_index = header.index("Time")
    for item in items: 
        item[0] = ""                # Remove indices; only useful for queue numbering
        if item[rem_index] == "":   # If time remaining is empty (dl_speed=0) then set to INF for active dls
            item[rem_index] = "INF"

    return items, header


def printResults(items: list[list[str]], header: list[str]=[]) -> None:
    """ Print download items along with the header to stdout """
    if header:
        items=[header]+items
        print(tabulate.tabulate(items, headers='firstrow', tablefmt='grid'))
    else:
        print(tabulate.tabulate(items, tablefmt='grid'))


def restartAria() -> None:
    """Restart aria2 daemon."""
    for cmd in config["general"]["restartcmds"]:
        subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    # cmd = f"systemctl --user restart aria2d.service"
    # subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    # Wait before trying to reconnect
    subprocess.run("sleep 2", shell=True, stderr=subprocess.PIPE)


def editConfig() -> None:
    """ Edit the config file in nvim. """
    config =  get_config()

    file = config["general"]["ariaconfigpath"]
    cmd = f"nvim {file}"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

def changeOptionDialog(gid:str) -> str:
    """ Change the option(s) for the download. """ 
    try:
        req = getOption(str(gid))
        response = sendReq(req)["result"]
        current_options = json.loads(json.dumps(response))
    except Exception as e:
        return str(e)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        json.dump(current_options, f, indent=4)
        temp_file = f.name

    cmd = f"nvim -i NONE {temp_file}"
    subprocess.run(cmd, shell=True)

    with open(temp_file, "r") as f:
        loaded_options = json.load(f)

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if current_options[key] != loaded_options.get(key, None))

    reqs = []
    for key in keys_with_diff_values:
        reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."

def flatten_data(y, delim="."):
    out = {}

    def flatten(x, name='', delim="."):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + delim)
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + delim)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y, delim=delim)
    return out

def unflatten_data(y, delim="."):
    out = {}

    def unflatten(x, parent_key='', delim="."):
        if type(x) is dict:
            for k, v in x.items():
                new_key = f"{parent_key}{delim}{k}" if parent_key else k
                unflatten(v, new_key, delim)
        else:
            keys = parent_key.split(delim)
            current_dict = out
            for key in keys[:-1]:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]
            current_dict[keys[-1]] = x

    unflatten(y)
    return out


def changeOptionBatchDialog(gids:list) -> str:
    """ Change the option(s) for the download. """ 
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
        json.dump(current_options, f, indent=4)
        temp_file = f.name

    cmd = f"nvim -i NONE {temp_file}"
    subprocess.run(cmd, shell=True)

    with open(temp_file, "r") as f:
        loaded_options = json.load(f)

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if current_options[key] != loaded_options.get(key, None))

    reqs = []
    for gid in gids:
        for key in keys_with_diff_values:
            reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."

def changeOptionPicker(stdscr: curses.window, gid:str) -> str:
    """ Change the option(s) for the download. """ 
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
            sort_column=1,
            editable_columns=[False, True],
            keys_dict=edit_menu_keys,
            startup_notification="'e' to edit cell. 'q' to exit. 'Return' to submit.",
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

def changeOptionsBatchPicker(stdscr: curses.window, gids:str) -> str:
    """ Change the option(s) for the download. """ 
    if len(gids) == 0: return ""
    gid = gids[0]
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
            title=f"Change Options for {len(gids)} download(s)",
            sort_column=1,
            editable_columns=[False, True],
            keys_dict=edit_menu_keys,
            startup_notification="Press 'e' to edit cell.",
    )
    selected_indices, opts, function_data = x.run()
    if not selected_indices: return "0 options changed"
    flattened_json = function_data["items"]
    unflattened_json = unflatten_data({row[0]: row[1] for row in flattened_json})
    loaded_options = unflattened_json

    # Get difference between dicts
    keys_with_diff_values = set(key for key in current_options if current_options[key] != loaded_options.get(key, None))

    reqs = []
    for gid in gids:
        for key in keys_with_diff_values:
            reqs.append(json.loads(changeOption(gid, key, loaded_options[key])))

    batch = sendReq(json.dumps(reqs).encode('utf-8'))

    return f"{len(keys_with_diff_values)} option(s) changed."

def addUrisFull(url: str ="http://localhost", port: int =6800, token: str = None) -> list:
    """Add URIs to aria server"""

    s = ""
    # s = "!!\n"
    # s += "# !! arguments inside !! will be applied to all downloads that follow\n"
    # s += "# !pause=true,queue=0! add and pause, send all to front of queue\n"
    # s += "# !!argstrings not yet fully implemented\n"
    s += '# https://docs.python.org/3/_static/py.png\n'
    s += '#    dir=/home/user/pngfiles/\n'
    s +=  '# https://docs.python.org/3/_static/py.jpg\n'
    s +=  '# https://docs.python.org/3/_static/py.svg\n#    pythonlogo.svg\n#    dir=/home/user/Downloads/\n#    pause=true\n'
    s += '#    user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1\n\n'
    s += "# Valid options can be found in the aria2c manual at: https://aria2.github.io/manual/en/html/aria2c.html#input-file\n\n"

    ## Create tmpfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls, argstrs = input_file_lines_to_dict(lines)

    # Restrict keys passed to the following
    # valid_keys = ["out", "uri", "dir", "on_download_start", "on_download_complete"]
    valid_keys = input_file_accepted_options
    gids = []
    for dl in dls:
        if "uri" not in dl:
            continue

        uri = dl["uri"]
        download_options_dict = {key: val for key,val in dl.items() if key in valid_keys}
        # return_val, gid = addDownload(**{key:val for key,val in dl.items() if key in valid_keys})
        return_val, gid = addDownload(uri, download_options_dict=download_options_dict)
        if return_val:
            gids.append(gid)

    # os.system(f"notify-send '{len(dls)} downloads added'")
    return gids

def addUrisAndPauseFull(url: str ="http://localhost", port: int =6800, token: str = "") -> None:
    gids = addUrisFull(url=url, port=port,token=token)
    if gids:
        reqs = [json.loads(pause(gid)) for gid in gids]
        batch = sendReq(json.dumps(reqs).encode('utf-8'))



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
    """

    downloads = []
    download = {}
    argstrings = []

    for line in lines:
        stripped_line = line.rstrip()

        # Comment
        if line.strip().startswith('#') or line.strip() == '': continue
        
        # If the line has no leading spaces then it is a url to add
        if line.startswith('!'):
            argstrings.append(line)
        elif not line.startswith(' '):
            if download:
                downloads.append(download)
                download = {}
            download["uri"] = stripped_line
        elif '=' in line and line.startswith(' '):
            key, value = stripped_line.split('=', 1)
            download[key.strip()] = value.strip()
        elif len(download) == 1 and line.startswith(' '):
            download["out"] = line.strip()

    if download:
        downloads.append(download)

    return downloads, argstrings


def addTorrentsFull(url: str ="http://localhost", port: int = 6800, token: str =None) -> str:
    """
    Open a kitty prompt to add torrents to Aria2. The file will accept torrent file paths or magnet links and they should be placed on successive lines.

    Example entry for the prompt:
        ```
        /home/user/Downloads/torrents/example.torrent
        magnet:?xt=urn:btih:...
        ```
    """

    s = ""
    # s = "!!\n"
    # s += "# !! arguments inside !! will be applied to all downloads that follow\n"
    # s += "# !pause=true,queue=0! add and pause, send all to front of queue\n"
    # s += "# !!argstrings not yet fully implemented\n"
    s += "# /path/to/file.torrent\n"
    s += "# magnet:?xt=...\n\n"

    ## Create tmpfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls = []
    uris = []
    argstrs = []
    gids = []
    for line in lines:
        if line[0] == "!" and line.count("!") == 2:
            argstrs.append(line)
        elif line[0] in ["#", "!"] or line.strip() == "":
            pass
        elif len(line) > len("magnet:") and line[:len("magnet:")] == "magnet:":
            uris.append({"uri": line.strip()})
        else:
            dls.append({"path": line.strip()})

    for dl in dls:
        jsonreq = addTorrent(dl["path"])

        sendReq(jsonreq)

    for dl in uris:
        uri = dl["uri"]

        return_val, gid = addDownload(uri=uri)
        if return_val: gids.append(gid)

    return f'{len(dls)} torrent file(s) added. {len(uris)} magnet link(s) added.'


def getAllInfo(gid: str) -> list[dict]:
    """
    Retrieves all information about an aria2 download.

    Returns:
        list: A list of key/value dictionaries containing the options and information about the downloads.
    """

    responses = []
    names = ["getFiles", "getServers", "getPeers", "getUris", "getOption", "tellStatus"]
    # for op in [getFiles, getServers, getPeers, getUris, getOption, tellStatus]:
    for i, op in enumerate([getFiles, getServers, getPeers, getUris, getOption, tellStatus]):
        try:
            response = sendReq(op(gid))
            info = { "function" : names[i] }
            response = {**info, **response}
            responses.append(response)
        except:
            responses.append(json.loads(f'{{"function": "{names[i]}", "response": "NONE"}}'))
    return responses


def retryDownloadFull(gid: str, url: str ="http://localhost", port: int = 6800, token: str =None) -> str:
    """ Retries a download. By getting the key information and using it to add a new download. Does not remove the old download. Returns the gid of the new download or an empty string if there is an error. """

    status = sendReq(tellStatus(gid))
    options = sendReq(getOption(gid))

    uri = status["result"]["files"][0]["uris"][0]["uri"]
    dl = {
        "dir": status["result"]["dir"],
    }
    dl["out"] = options["result"]["out"] if "out" in options["result"] else ""
    return_val, gid = addDownload(uri=uri, download_options_dict=dl)
    if return_val: return gid
    else: return ""

def retryDownloadAndPauseFull(gid: str, url: str ="http://localhost", port: int = 6800, token: str ="") -> None:
    """ Retries a download by getting the options of the existing download and using it to add a new download and then pauses the download. Does not remove the old download. Returns the gid of the new download or an empty string if there is an error. """
    gid = retryDownloadFull(gid, url=url, port=port, token=token)
    if gid: sendReq(pause(gid))



def getAll() -> Tuple[list[list[str]], list[str]]:
    """ Retrieves all downloads: active, stopped, and queue. Also returns the header. """
    active, aheader = getActive()
    stopped, sheader = getStopped()
    waiting, wheader = getQueue()

    return active + waiting + stopped, wheader

def openDownloadLocation(gid: str, new_window: bool = True) -> None:
    """ Opens the download location for a given download. """
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        req = getFiles(str(gid))
        response = sendReq(req)
        val = json.loads(json.dumps(response))
        files = val["result"]
        if len(files) == 0: return None
        loc = files[0]["path"]
        if "/" not in loc:
            req = getOption(str(gid))
            response = sendReq(req)
            val = json.loads(json.dumps(response))
            loc = val["result"]["dir"]

        config = get_config()
        terminal_file_manager = config["general"]["terminal_file_manager"]
        gui_file_manager = config["general"]["gui_file_manager"]
        if new_window:
            cmd = f"{gui_file_manager} {repr(loc)}"
            subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        else:
            cmd = f"{terminal_file_manager} {repr(loc)}"
            subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    except:
        pass

def openGidFiles(gids: list[str], group: bool = True) -> None:
    """
    Open files downloads based on their gid.
        If group is False then we open each download separately.
        If group is True then we use xdg-mime and gio to get the default applications
            and group files by application and open them in one instance of the application. 
            E.g., video and audio files will be opened with mpv and images will be opened with gimp
    """
    if isinstance(gids, str): gids=[gids]
    files_list = []

    for gid in gids:
        try:
            req = getFiles(str(gid))
            response = sendReq(req)
            val = json.loads(json.dumps(response))
            files = val["result"]
            if len(files) == 0: continue
            loc = files[0]["path"]
            if "/" not in loc:
                req = getOption(str(gid))
                response = sendReq(req)
                val = json.loads(json.dumps(response))
                loc = val["dir"]

            files_list.append(repr(loc))

            if not group:
                config = get_config()
                launch_command = config["general"]["launch_command"]
                cmd = f"{launch_command} {repr(loc)}"
                subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            pass
    if group:
        openFiles(files_list)

def openFiles(files: list[str]) -> None:
    """
    Opens multiple files using their associated applications.
        Get mime types
        Get default application for each mime type
        Open all files; files with the same default application will be opened in one instance

    Args:
        files (list[str]): A list of file paths.

    Returns:
        None
    """
    def get_mime_types(files):
        types = {}

        for file in files:
            resp = subprocess.run(f"xdg-mime query filetype {file}", stdout=subprocess.PIPE, shell=True)
            ftype = resp.stdout.decode("utf-8").strip()
            if ftype in types:
                types[ftype] += [file]
            else:
                types[ftype] = [file]

        return types

    def get_applications(types):
        apps = {}

        for t in types:
            resp = subprocess.run(f"xdg-mime query default {t}", stdout=subprocess.PIPE, shell=True)
            app = resp.stdout.decode("utf-8").strip()
            if app in apps:
                apps[app] += [t]
            else:
                apps[app] = [t]

        return apps

    types = get_mime_types(files)
    apps = get_applications(types.keys())

    apps_files = {}
    for app, filetypes in apps.items():
        flist = []
        for filetype in filetypes:
            flist += types[filetype]
        apps_files[app] = flist

    for app, files in apps_files.items():
        files_str = ' '.join(files)
        subprocess.Popen(f"gio launch /usr/share/applications/{app} {files_str}", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)


def applyToDownloads(stdscr: curses.window, gids: list = [], operation_name: str = "", operation_function: Callable = lambda:None, operation_function_args: dict = {}, user_opts: str = "", view: bool =False, fnames:list=[], picker_view: bool = False) -> None:

    responses = []
    if len(gids) ==0 : return None
    if operation_name in ["Open File(s) (do not group)", "Open File(s)"]:
        operation_function(gids)
    elif operation_name in ["Change Options nvim (for all selected)"]:
        operation_function(gids)
    elif operation_name in ["Change Options Picker (for each selected)"]:
        operation_function(stdscr, gids[0])
    elif operation_name in ["Change Options Picker (for all selected)"]:
        operation_function(stdscr, gids)
    elif operation_name == "Transfer Speed Graph *experimental*":
        fname = fnames[0]
        if len(fname)>20: fname = fname[:17] + '...'

        operation_function_args["title"] = f"{repr(fname)} Transfer Speeds"
        operation_function(gid=str(gids[0]), **operation_function_args)

    else:
        for gid in gids:
            try:
                jsonreq = {}
                if operation_name == "Change Position":
                    position = int(user_opts) if user_opts.strip().isdigit() else 0
                    jsonreq = operation_function(str(gid), position)
                elif operation_name == "DL Info: Get All Info":
                    js_rs = getAllInfo(str(gid))
                    responses.append(js_rs)
                elif operation_name == "Send to Back of Queue":
                    jsonreq = operation_function(str(gid), pos=10000)
                elif operation_name == "Send to Front of Queue":
                    jsonreq = operation_function(str(gid), pos=0)
                # elif len(operation_list) > 2:
                #     operation_kwargs = operation_list[2]
                #     jsonreq = operation_function(str(gid), **operation_kwargs)
                else:
                    jsonreq = operation_function(gid=str(gid), **operation_function_args)

                js_rs = sendReq(jsonreq)
                responses.append(js_rs)
            except:
                pass
                # responses.append({})
        if view:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                for i, response in enumerate(responses):
                    tmpfile.write(f'{"*"*50}\n{str(i)+": "+gids[i]:^50}\n{"*"*50}\n')
                    tmpfile.write(json.dumps(response, indent=4))
                tmpfile_path = tmpfile.name
            # cmd = r"nvim -i NONE -c '/^\s*\"function\"'" + f" {tmpfile_path}"
            # cmd = r"""nvim -i NONE -c 'setlocal bt=nofile' -c 'silent! %s/^\s*"function"/\0' -c 'norm ggn'""" + f" {tmpfile_path}"
            cmd = f"nvim {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
        elif picker_view:
            l = []
            for i, response in enumerate(responses):
                l += [[gid, "------"]]
                l += [[key, val] for key, val in flatten_data(response).items()]
            x = Picker(
                    stdscr,
                    items=l,
                    search_query="function",
                    title=operation_name,
                    header=["Key", "Value"],
            )
            x.run()

    stdscr.clear()

def getGlobalSpeed() -> str:
    resp = sendReq(getGlobalStat())
    up = bytes_to_human_readable(resp['result']['uploadSpeed'])
    down = bytes_to_human_readable(resp['result']['downloadSpeed'])
    numActive = resp['result']['numActive']
    numStopped = resp['result']['numStopped']
    numWaiting = resp['result']['numWaiting']
    return f"{down}/s 󰇚 {up}/s 󰕒 | {numActive}A {numWaiting}W {numStopped}S"
    return f"{down}/s 󰇚  {up}/s 󰕒"
        
def bytes_to_human_readable(size: float) -> str:
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    if isinstance(size, str):
        size=float(size)
    i = 0
    while size >= 1024 and i < len(suffixes)-1:
        size /= 1024.0
        i += 1
    return f"{size:.1f} {suffixes[i]}"

def get_config(path="") -> dict:
    """ Get config from file. """
    full_config = get_default_config()
    default_path = "~/.config/aria2tui/config.toml"

    CONFIGPATH = default_path
    if "ARIA2TUI_CONFIG_PATH" in os.environ:
        if os.path.exists(os.path.expanduser(os.environ["ARIA2TUI_CONFIG_PATH"])):
            CONFIGPATH = os.environ["ARIA2TUI_CONFIG_PATH"]

    if os.path.exists(os.path.expanduser(CONFIGPATH)):
        with open(os.path.expanduser(CONFIGPATH), "r") as f:
            config = toml.load(f)

        if "general" in config:
            for key in config["general"]:
                full_config["general"][key] = config["general"][key]
        if "appearance" in config:
            for key in config["appearance"]:
                full_config["appearance"][key] = config["appearance"][key]

    return full_config

def get_default_config() -> dict:
    default_config = {
        "general" : {
            "url": "http://localhost",
            "port": "6800",
            "token": "",
            "startupcmds": ["aria2c"],
            "restartcmds": ["pkill aria2c && sleep 1 && aria2c"],
            "ariaconfigpath": "~/.config/aria2/aria2.conf",
            "paginate": False,
            "refresh_timer": 2,
            "global_stats_timer": 1,
            "terminal_file_manager": "yazi",
            "gui_file_manager": "kitty yazi",
            "launch_command": "xdg-open",
        },
        "appearance":{
            "theme": 0
        }
    }
    return default_config

# default = get_default_config()
config = get_config()
url = config["general"]["url"]
port = config["general"]["port"]
token = config["general"]["token"]
paginate = config["general"]["paginate"]
## Create lambda functions which fill the url, port, and token for our aria2c rpc operations


addUri = lambda uri, out="", dir=None, queue_pos=10000:  addUriFull(uri, out=out, dir=dir, queue_pos=queue_pos, token=token)
addTorrent = lambda path, out="", dir=None, queue_pos=10000:  addTorrentFull(path, out=out, dir=dir, queue_pos=queue_pos, token=token)
addDownload = lambda uri, url=url, port=port, token=token, queue_pos=None, prompt=False, cookies_file="", download_options_dict={}:  addDownloadFull(uri, queue_position=queue_pos, url=url, port=port, token=token, prompt=prompt, cookies_file=cookies_file, download_options_dict=download_options_dict)
getOption = lambda gid:  getOptionFull(gid, token=token)
getServers = lambda gid:  getServersFull(gid, token=token)
getPeers = lambda gid:  getPeersFull(gid, token=token)
getUris = lambda gid:  getUrisFull(gid, token=token)
getGlobalOption = lambda : getGlobalOptionFull(token=token)
getSessionInfo = lambda : getSessionInfoFull(token=token)
getVersion = lambda : getVersionFull(token=token)
getGlobalStat = lambda : getGlobalStatFull(token=token)
pause = lambda gid:  pauseFull(gid, token=token)
retryDownload = lambda gid:  retryDownloadFull(gid, url=url, port=port, token=token)
retryDownloadAndPause = lambda gid:  retryDownloadAndPauseFull(gid, url=url, port=port, token=token)
pauseAll = lambda : pauseAllFull(token=token)
forcePauseAll = lambda : forcePauseAllFull(token=token)
unpause = lambda gid:  unpauseFull(gid, token=token)
remove = lambda gid:  removeFull(gid, token=token)
forceRemove = lambda gid:  forceRemoveFull(gid, token=token)
# removeStopped = lambda gid:  removeStoppedFull(gid, token=token)
removeDownloadResult = lambda gid:  removeDownloadResultFull(gid, token=token)
getFiles = lambda gid:  getFilesFull(gid, token=token)
removeCompleted = lambda : removeCompletedFull(token=token)
changePosition = lambda gid, pos, how="POS_SET":  changePositionFull(gid, pos, how=how, token=token)
changeOption = lambda gid, key, val:  changeOptionFull(gid, key, val, token=token)
tellActive = lambda offset=0, max=10000:  tellActiveFull(offset=0, max=max, token=token)
tellWaiting = lambda offset=0, max=10000:  tellWaitingFull(offset=0, max=max, token=token)
tellStopped = lambda offset=0, max=10000:  tellStoppedFull(offset=0, max=max, token=token)
tellStatus = lambda gid:  tellStatusFull(gid, token=token)
sendReq = lambda jsonreq, url=url, port=port: sendReqFull(jsonreq, url=url, port=port)
addTorrents = lambda url=url, port=port, token=token: addTorrentsFull(url=url, port=port, token=token)
addUris = lambda url=url, port=port, token=token: addUrisFull(url=url, port=port, token=token)
addUrisAndPause = lambda url=url, port=port, token=token: addUrisAndPauseFull(url=url, port=port, token=token)
testConnection = lambda url=url, port=port: testConnectionFull(url=url, port=port)
testAriaConnection = lambda url=url, port=port: testAriaConnectionFull(url=url, port=port)
