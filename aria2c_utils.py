from aria2c_wrapper import *
import os
import subprocess
import tomllib
from urllib import request as rq
from subprocess import run
import urllib
import copy
import json
from sqlalchemy.engine import cursor
from utils import *
import tempfile
from aria_adduri import addDownloadFull
import tabulate

def testConnectionFull(url="http://localhost", port=6800):
    url = f'{url}:{port}/jsonrpc'
    try:
        getVersion()
        with rq.urlopen(url, getVersion()) as c:
            response = c.read()
        return True
    except urllib.error.URLError:
        return False


def getQueue():
    js_rs = send_req(tellWaiting())

    items = []

    options_batch = []
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = send_req(json.dumps(options_batch).encode('utf-8'))

    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
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
    return items[::-1], header

def getFromQueue(pos=[]):
    if type(pos) ==  type(1): pos = [pos]

    jsonreq = tellWaiting()

    js_rs = send_req(jsonreq)
    entries = []


    for i in range(len(js_rs["result"])-1, -1, -1):
        if i not in pos: continue
        dl = js_rs["result"][i]
        colsize = 14
        try:
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])
        except:
            pass

def getQueueCompact():
    jsonreq = tellWaiting()
    js_rs = send_req(jsonreq)

    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        # print(f"{'Queue Position':<{colsize}}: {i}")
        try:
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            status = dl['status'].strip()
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            status_char = status_chars[status]
            
            fn_width = 65
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])

            line = f"{i:0>{len(str(len(js_rs['result'])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%"
        
        except:
            pass

def getStopped():
    jsonreq = tellStopped()

    js_rs = send_req(tellStopped())

    entries = []
    items = []

    options_batch = []
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = send_req(json.dumps(options_batch).encode('utf-8'))


    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        try:
            gid = dl['gid']
            options = options_batch[i]
            pth = options["result"]["dir"]
            orig_path = dl['files'][0]['path']
            fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
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
    return items, header

def getStoppedCompact():
    jsonreq = tellStopped()

    js_rs = send_req(jsonreq)
    entries = []

    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        try:
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            status = dl['status'].strip()
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            status_char = status_chars[status]
            
            fn_width = 65
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])

            line = f"{i:0>{len(str(len(js_rs['result'])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%"
        
        except:
            pass

def getActive(print_output=False):

    js_rs = send_req(tellActive())
    items = []

    if print_output:
        print(f"{' Active ':*^50}")
        print("*"*50)

    options_batch = []
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = send_req(json.dumps(options_batch).encode('utf-8'))

    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            colsize = 14
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

            if print_output:
                print(f"{'Path':<{colsize}}: {pth[:70]}")
                print(f"{'Filename':<{colsize}}: {fname}")
                print(f"{'Status':<{colsize}}: {dl['status']}")
                print(f"{'GID':<{colsize}}: {dl['gid']}")
                print(f"{'Size':<{colsize}}: {size/1024**2:.02f}MB")
                print(f"{'Completed':<{colsize}}: {completed/1024**2:.02f}MB")
                print(f"{'% Completed':<{colsize}}: {100*pc_complete:.02f}%")
                print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB/s")
                print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB/s")
                print(f"{'Time Left':<{colsize}}: {time_left_s}")

            row = ["NA", status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left_s, pth, gid]
            items.append(row)
        except:
            pass

        if print_output:
            print("*"*50)
    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
    return items, header

def getActiveCompact():
    jsonreq = tellActive()

    js_rs = send_req(jsonreq)

    fn_width = 65
    header = f"{'Q'} {'S'}  {'File Name':{fn_width}}  {'Size':8}  {'%done'}  {'DL speed'}  {'Time Left'}"
    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            colsize = 14
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left:
                time_left_s = ""
                time_left_s += f"{time_left//60**2%60}h" if time_left//60**2 > 1 else ""
                time_left_s += f"{time_left//60%60}m" if time_left//60 > 1 else ""
                time_left_s += f"{time_left%60}s"
            else: time_left_s = "INF"
            
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            status = dl['status'].strip()
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            status_char = status_chars[status]
            
            fn_width = 65
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])

            line = f"{i:0>{len(str(len(js_rs['result'])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size/1024**2:.02f}MB  {pc_complete*100:.01f}%  {dl_speed/1024:.02f}KB/s  {time_left_s}s"


        except:
            pass

def getPaused():
    jsonreq = tellWaiting()
    js_rs = send_req(jsonreq)
    gids=[]

    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        if "paused" not in dl['status']: continue
        try:
            colsize = 14
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]

            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left:
                time_left_s = ""
                time_left_s += f"{time_left//60**2%60}h" if time_left//60**2 > 1 else ""
                time_left_s += f"{time_left//60%60}m" if time_left//60 > 1 else ""
                time_left_s += f"{time_left%60}s"
            else: time_left_s = "INF"
            gids.append(dl['gid'])

        except:
            pass

def printResults(items, header=[]):
    if header:
        items=header+items
        print(tabulate.tabulate(items, headers='firstrow', tablefmt='grid'))
    else:
        print(tabulate.tabulate(items, tablefmt='grid'))

def restartAria():
    cmd = f"systemctl --user restart aria2d.service"
    subprocess.run(cmd, shell=True)

def editConfig():
    cmd = f"NVIM_APPNAME=nvim-nvchad nvim ~/.config/aria2/aria2.conf"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

def addUrisFull(url="http://localhost", port=6800, token=None):
    s = "!!\n"
    s +=  "# URI,out\n\n"

    ## Create tmpfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    # process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls = []
    argstrs = []
    for line in lines:
        if line[0] == "!" and line.count("!") == 2:
            argstrs.append(line)
        elif line[0] in ["#", "!"] or line.strip() == "":
            pass
        else:
            sp = line.find(",")
            if sp == -1:
                dls.append({"uri": line.strip()})
            else:
                dls.append({"uri": line[:sp].strip(), "filename": line[sp+1:].strip()})

    for dl in dls:
        # addDownload(**dl, url=url, port=port, token=token)
        addDownload(**dl)
        # jsonreq = pyperclip.copy(addUri(**dl))
        # send_req(jsonreq)

    os.system(f"notify-send '{len(dls)} downloads added'")

def addTorrentsFull(url="http://localhost", port=6800, token=None):
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
            # sp = line.find(",")
            # if sp == -1:
            #     # os.system(f"notify-send '{len(dls)} downloads added'")
            #     dls.append({"path": line.strip()})
            # else:
            #     dls.append({"path": line[:sp].strip(), "filename": line[sp+1:].strip()})

    for dl in dls:
        # with open(dl["path"], "rb") as f:
        #     torrent_data = f.read()
        jsonreq = addTorrent(dl["path"])

        # jsonreq = pyperclip.copy(addUri(**dl))
        send_req(jsonreq)

    for uri in uris:
        addDownload(**uri)

    os.system(f"notify-send '{len(dls)} torrent files added'")
    os.system(f"notify-send '{len(uris)} magnet links added'")

def getAllInfo(gid):
    responses = []
    names = ["getFiles", "getServers", "getPeers", "getUris", "getOption", "tellStatus"]
    # for op in [getFiles, getServers, getPeers, getUris, getOption, tellStatus]:
    for i, op in enumerate([getFiles, getServers, getPeers, getUris, getOption, tellStatus]):
        try:
            response = send_req(op(gid))
            info = { "function" : names[i] }
            response = {**info, **response}
            responses.append(response)
        except:
            responses.append(json.loads(f'{{"function": "{names[i]}", "response": "NONE"}}'))
    return responses
    file_info = send_req(getFiles(gid))
    server_info = send_req(getServers(gid)) 

    vals = [file_info]
    return file_info
    return [val if val else json.loads("{}") for val in vals]

def retryDownloadFull(gid, url="http://localhost", port=6800, token=None):
    status = send_req(tellStatus(gid))
    options = send_req(getOption(gid))

    dir = status["result"]["dir"]
    uri = status["result"]["files"][0]["uris"][0]["uri"]
    fname = options["result"]["out"] if "out" in options["result"] else None
    os.system(f"notify-send '{dir}'")
    addDownload(uri=uri, directory=dir, filename=fname)

def getAll():
    active, aheader = getActive()
    stopped, sheader = getStopped()
    waiting, wheader = getQueue()

    return active + waiting + stopped, wheader

def openDownloadLocation(gid, new_window=True):
    """

    """
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        req = getFiles(str(gid))
        response = send_req(req)
        val = json.loads(json.dumps(response))
        files = val["result"]
        if len(files) == 0: return None
        loc = files[0]["path"]
        if "/" not in loc:
            req = getOption(str(gid))
            response = send_req(req)
            val = json.loads(json.dumps(response))
            loc = val["dir"]

        # val = json.loads(response.encode('utf-8'))
        if new_window:
            cmd = f"kitty yazi {repr(loc)}"
            # subprocess.run(cmd, shell=True)
            subprocess.Popen(cmd, shell=True)
            # os.system(f'kitty yazi "{loc}"')
        else:
            cmd = f"yazi {repr(loc)}"
            # subprocess.run(cmd, shell=True)
            subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
            # os.system(f'kitty yazi "{loc}"')

    except:
        pass

def openFile(gid):
    """

    """
    try:
        req = getFiles(str(gid))
        response = send_req(req)
        val = json.loads(json.dumps(response))
        files = val["result"]
        if len(files) == 0: return None
        loc = files[0]["path"]
        if "/" not in loc:
            req = getOption(str(gid))
            response = send_req(req)
            val = json.loads(json.dumps(response))
            loc = val["dir"]

        # val = json.loads(response.encode('utf-8'))
        cmd = f"xdg-open {repr(loc)}"
        # subprocess.run(cmd, shell=True)
        subprocess.Popen(cmd, shell=True)
        # os.system(f'kitty yazi "{loc}"')

    except:
        pass

CONFIGPATH = "~/scripts/utils/aria2tui/aria2tui.toml"
with open(os.path.expanduser(CONFIGPATH), "rb") as f:
    config = tomllib.load(f)
url = config["general"]["url"]
port = config["general"]["port"]
token = config["general"]["token"]
paginate = config["general"]["paginate"]

send_req = lambda req: sendReqFull(req, url=url, port=port)
addUri = lambda uri, out="", dir=None, queue_pos=10000:  addUriFull(uri, out=out, dir=dir, queue_pos=queue_pos, token=token)
addTorrent = lambda path, out="", dir=None, queue_pos=10000:  addTorrentFull(path, out=out, dir=dir, queue_pos=queue_pos, token=token)
addDownload = lambda uri, filename=None, directory=None, url=url, port=port, token=token, queue_pos=None, proxy=None, prompt=False, cookies_file=None:  addDownloadFull(uri, filename=filename, directory=directory, queue_position=queue_pos, url=url, port=port, token=token, prompt=prompt, proxy=proxy, cookies_file=cookies_file)
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
removeStopped = lambda gid:  removeStoppedFull(gid, token=token)
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
