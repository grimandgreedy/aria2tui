import copy
import json
from urllib import request as rq
import base64


def addUriFull(uri, out="", dir=None, queue_pos=10000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.addUri"
    if "params" in jsonreq:
        jsonreq["params"] += [[uri], {"out": out}, queue_pos]
    else:
        jsonreq["params"] = [[uri], {"out": out}, queue_pos]
    return json.dumps(jsonreq).encode('utf-8')

def addTorrentFull(path, out="", dir=None, queue_pos=10000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.addTorrent"
    torrent = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    if "params" in jsonreq:
        # jsonreq["params"] += [[torrent], {"out": out}, queue_pos]
        jsonreq["params"] += [torrent]
    else:
        # jsonreq["params"] = [[torrent], {"out": out}, queue_pos]
        jsonreq["params"] = [torrent]
    return json.dumps(jsonreq).encode('utf-8')

def getOptionFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getOption"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def getServersFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getServers"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def getPeersFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getPeers"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def getUrisFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getUris"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def getGlobalOptionFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getGlobalOption"
    return json.dumps(jsonreq).encode('utf-8')

def getSessionInfoFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getSessionInfo"
    return json.dumps(jsonreq).encode('utf-8')

def getVersionFull(token=None):
    # if token: print(token)
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getVersion"
    return json.dumps(jsonreq).encode('utf-8')

def getGlobalStatFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getGlobalStat"
    return json.dumps(jsonreq).encode('utf-8')

def pauseFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.pause"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def pauseAllFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.pauseAll"
    return json.dumps(jsonreq).encode('utf-8')

def unpauseFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.unpause"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def removeFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.remove"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def forceRemoveFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.forceRemove"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def removeDownloadResultFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.removeDownloadResult"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def getFilesFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getFiles"
    if "params" in jsonreq: jsonreq["params"] += [gid]
    else: jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def removeCompletedFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.purgeDownloadResult"
    return json.dumps(jsonreq).encode('utf-8')

def changePositionFull(gid, pos, how="POS_SET", token=None):
    # how in POS_SET, POS_END, POS_CUR
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.changePosition"
    if "params" in jsonreq:
        jsonreq["params"] += [gid, pos, how]
    else:
        jsonreq["params"] = [gid, pos, how]
    return json.dumps(jsonreq).encode('utf-8')

def changeOptionFull(gid, key, val, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.changeOption"
    if "params" in jsonreq:
        jsonreq["params"] += [gid, {key:val}]
    else:
        jsonreq["params"] = [gid, {key:val}]
    return json.dumps(jsonreq).encode('utf-8')

def tellActiveFull(offset=0, max=5000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.tellActive"
    return json.dumps(jsonreq).encode('utf-8')

def tellWaitingFull(offset=0, max=5000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.tellWaiting"
    if "params" in jsonreq:
        jsonreq["params"] += [offset, max]
    else:
        jsonreq["params"] = [offset, max]
    return json.dumps(jsonreq).encode('utf-8')

def tellStoppedFull(offset=0, max=5000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.tellStopped"
    if "params" in jsonreq:
        jsonreq["params"] += [offset, max]
    else:
        jsonreq["params"] = [offset, max]
    return json.dumps(jsonreq).encode('utf-8')

def tellStatusFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.tellStatus"
    if "params" in jsonreq:
        jsonreq["params"] += [gid]
    else:
        jsonreq["params"] = [gid]
    return json.dumps(jsonreq).encode('utf-8')

def sendReqFull(jsonreq, url="http://localhost", port=6800):
    with rq.urlopen(f'{url}:{port}/jsonrpc', jsonreq) as c:
        response = c.read()
    js_rs = json.loads(response)
    # return response
    return js_rs

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#- TORRENT
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
