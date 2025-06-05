import curses
from aria2c_wrapper import *
import os
import subprocess
import tomllib
from urllib import request as rq
from subprocess import run
import json
from sqlalchemy.engine import cursor
from utils import *
import tempfile
from aria_adduri import addDownloadFull
import tabulate
from typing import Callable, Tuple

def testConnectionFull(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests the connection to the Aria2 server. """
    url = f'{url}:{port}/jsonrpc'
    try:
        getVersion()
        with rq.urlopen(url, getVersion()) as c:
            response = c.read()
        return True
    except:
        return False

def getQueue() -> Tuple[list[list[str]], list[str]]:
    """ Retrieves download queue and corresponding header from aria2 over rpc. """
    js_rs = sendReq(tellWaiting())

    items = []

    options_batch = []
    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = sendReq(json.dumps(options_batch).encode('utf-8'))

    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            gid = dl['gid']
            options = options_batch[i]
            pth = options["result"]["dir"]
            orig_path = dl['files'][0]['path']
            fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            try:
                if "bittorrent" in dl:
                    tmp = dl["bittorrent"]["info"]["name"]
                    fname = tmp
            except: pass

            status = dl['status']
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            dl_speed = int(dl['downloadSpeed'])
            time_left = "INF"
        
            row = [i, status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left, pth, gid]
            items.append(row)
        except:
            pass
    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
    return items, header


def getStopped() -> Tuple[list[list[str]], list[str]]:
    """ Retrieves stopped downloads and corresponding header from aria2 over rpc. """
    jsonreq = tellStopped()

    js_rs = sendReq(tellStopped())

    entries = []
    items = []

    options_batch = []
    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = sendReq(json.dumps(options_batch).encode('utf-8'))


    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            gid = dl['gid']
            options = options_batch[i]
            pth = options["result"]["dir"]
            orig_path = dl['files'][0]['path']
            fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            status = dl['status']
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = "INF"
        
            row = ["NA", status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left, pth, gid]
            items.append(row)
        except:
            pass
    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
    return items[::-1], header


def getActive() -> Tuple[list[list[str]], list[str]]:
    """ Retrieves active downloads and corresponding header from aria2 over rpc. """

    js_rs = sendReq(tellActive())
    items = []

    options_batch = []
    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = sendReq(json.dumps(options_batch).encode('utf-8'))

    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            gid = dl['gid']
            options = options_batch[i]
            pth = options["result"]["dir"]
            if "out" in options["result"]:
                fname = options["result"]["out"]
            else:
                orig_path = dl['files'][0]['path']
                fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            try:
                if "bittorrent" in dl:
                    tmp = dl["bittorrent"]["info"]["name"]
                    fname = tmp
            except: pass
            status = dl['status']
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left: time_left_s = convert_seconds(time_left)
            else: time_left_s = "INF"

            row = ["NA", status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left_s, pth, gid]
            items.append(row)
        except:
            pass

    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
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
    cmd = f"systemctl --user restart aria2d.service"
    subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    # Wait before trying to reconnect
    subprocess.run("sleep 2", shell=True, stderr=subprocess.PIPE)


def editConfig() -> None:
    """ Edit the config file in nvim. """
    cmd = f"NVIM_APPNAME=nvim-nvchad nvim ~/.config/aria2/aria2.conf"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)


def addUrisFull(url: str ="http://localhost", port: int =6800, token: str = None) -> None:
    """Add URIs to aria server"""

    s = "!!\n"
    s +=  '# https://docs.python.org/3/_static/py.svg\n#    pythonlogo.svg\n#    dir=/home/user/tmp/trash/'

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
    valid_keys = ["out", "uri", "dir"]
    for dl in dls:
        os.system(f"notify-send {dl}")
        addDownload(**{key:val for key,val in dl.items() if key in valid_keys})

    os.system(f"notify-send '{len(dls)} downloads added'")


def input_file_lines_to_dict(lines: list[str]) -> Tuple[list[str], list[dict]]:
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


def addTorrentsFull(url: str ="http://localhost", port: int = 6800, token: str =None) -> None:
    """
    Open a kitty prompt to add torrents to Aria2. The file will accept torrent file paths or magnet links and they should be placed on successive lines.

    Example entry for the prompt:
        ```
        /home/user/Downloads/torrents/example.torrent
        magnet:?xt=urn:btih:...
        ```
    """

    s = "!!\n"
    s +=  "# path\n\n"

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

    for uri in uris:
        addDownload(**uri)

    os.system(f"notify-send '{len(dls)} torrent files added'")
    os.system(f"notify-send '{len(uris)} magnet links added'")


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


def retryDownloadFull(gid: str, url: str ="http://localhost", port: int = 6800, token: str =None) -> None:
    """ Retries a download. By getting the key information and using it to add a new download. Does not remove the old download. """

    status = sendReq(tellStatus(gid))
    options = sendReq(getOption(gid))

    dir = status["result"]["dir"]
    uri = status["result"]["files"][0]["uris"][0]["uri"]
    fname = options["result"]["out"] if "out" in options["result"] else None
    os.system(f"notify-send '{dir}'")
    addDownload(uri=uri, dir=dir, out=fname)


def getAll() -> Tuple[list[list[str]], list[str]]:
    """ Retrieves all downloads: active, stopped, and queue. Also returns the header. """
    active, aheader = getActive()
    stopped, sheader = getStopped()
    waiting, wheader = getQueue()

    return active + waiting + stopped, wheader

def openDownloadLocation(gid: str, new_window: bool = True) -> None:
    """ Opens the download location for a given download in yazi. """
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
            loc = val["dir"]

        if new_window:
            cmd = f"kitty yazi {repr(loc)}"
            subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        else:
            cmd = f"yazi {repr(loc)}"
            subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    except:
        pass

def openFile(gids: list[str], group: bool = True) -> None:
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
                cmd = f"xdg-open {repr(loc)}"
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


def applyToDownloads(stdscr: curses.window, gids: list, operation_name: str, operation_function: Callable, user_opts: str, view) -> None:

    responses = []
    if operation_name in ["Open File(s) (do not group)", "Open File(s)"]:
        operation_function(gids)
    else:
        for gid in gids:
            try:
                jsonreq = {}
                if operation_name == "changePosition":
                    position = int(user_opts) if user_opts.strip().isdigit() else 0
                    jsonreq = operation_function(str(gid), position)
                elif operation_name == "getAllInfo":
                    js_rs = getAllInfo(str(gid))
                    responses.append(js_rs)
                elif operation_name == "sendToBackOfQueue":
                    jsonreq = operation_function(str(gid), pos=10000)
                elif operation_name == "sendToFrontOfQueue":
                    jsonreq = operation_function(str(gid), pos=0)
                # elif len(operation_list) > 2:
                #     operation_kwargs = operation_list[2]
                #     jsonreq = operation_function(str(gid), **operation_kwargs)
                else:
                    jsonreq = operation_function(str(gid))

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
            cmd = r"nvim -i NONE -c '/^\s*\"function\"'" + f" {tmpfile_path}"
            cmd = r"""nvim -i NONE -c 'setlocal bt=nofile' -c 'silent! %s/^\s*"function"/\0'""" + f" {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    stdscr.clear()

## Load config
CONFIGPATH = "~/scripts/utils/aria2tui/aria2tui.toml"

with open(os.path.expanduser(CONFIGPATH), "rb") as f:
    config = tomllib.load(f)
url = config["general"]["url"]
port = config["general"]["port"]
token = config["general"]["token"]
paginate = config["general"]["paginate"]

## Create lambda functions which fill the url, port, and token for our aria2c rpc operations


addUri = lambda uri, out="", dir=None, queue_pos=10000:  addUriFull(uri, out=out, dir=dir, queue_pos=queue_pos, token=token)
addTorrent = lambda path, out="", dir=None, queue_pos=10000:  addTorrentFull(path, out=out, dir=dir, queue_pos=queue_pos, token=token)
addDownload = lambda uri, out=None, dir=None, url=url, port=port, token=token, queue_pos=None, proxy=None, prompt=False, cookies_file=None:  addDownloadFull(uri, out=out, dir=dir, queue_position=queue_pos, url=url, port=port, token=token, prompt=prompt, proxy=proxy, cookies_file=cookies_file)
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
pauseAll = lambda : pauseAllFull(token=token)
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
testConnection = lambda url=url, port=port: testConnectionFull(url=url, port=port)
