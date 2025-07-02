#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2c_wrapper.py

Author: GrimAndGreedy
License: MIT
"""

import json
from urllib import request as rq
import base64

"""
Wrapper for rpc communication with aria2c daemon as described in https://aria2.github.io/manual/en/html/aria2c.html#rpc-interface
"""

def addUriFull(uri, out="", dir=None, queue_pos=10000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [[uri], {"out": out}, queue_pos]
    jsonreq["method"] = "aria2.addUri"
    return json.dumps(jsonreq).encode('utf-8')

def addTorrentFull(path, out="", dir=None, queue_pos=10000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    torrent = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    jsonreq["params"] += [torrent]
    jsonreq["method"] = "aria2.addTorrent"
    return json.dumps(jsonreq).encode('utf-8')

def getOptionFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.getOption"
    return json.dumps(jsonreq).encode('utf-8')

def getServersFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.getServers"
    return json.dumps(jsonreq).encode('utf-8')

def getPeersFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.getPeers"
    return json.dumps(jsonreq).encode('utf-8')

def getUrisFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.getUris"
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

def listMethods():
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer' }
    jsonreq["method"] = "system.listMethods"
    return json.dumps(jsonreq).encode('utf-8')

def listNotifications():
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer' }
    jsonreq["method"] = "system.listNotifications"
    return json.dumps(jsonreq).encode('utf-8')

def getGlobalStatFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.getGlobalStat"
    return json.dumps(jsonreq).encode('utf-8')

def pauseFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.pause"
    return json.dumps(jsonreq).encode('utf-8')

def pauseAllFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.pauseAll"
    return json.dumps(jsonreq).encode('utf-8')

def forcePauseAllFull(token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.forcePauseAll"
    return json.dumps(jsonreq).encode('utf-8')

def unpauseFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.unpause"
    return json.dumps(jsonreq).encode('utf-8')

def removeFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.remove"
    return json.dumps(jsonreq).encode('utf-8')

def forceRemoveFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.forceRemove"
    return json.dumps(jsonreq).encode('utf-8')

def removeDownloadResultFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.removeDownloadResult"
    return json.dumps(jsonreq).encode('utf-8')

def getFilesFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.getFiles"
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
    jsonreq["params"] += [gid, pos, how]
    jsonreq["method"] = "aria2.changePosition"
    return json.dumps(jsonreq).encode('utf-8')

def changeOptionFull(gid, key, val, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid, {key:val}]
    jsonreq["method"] = "aria2.changeOption"
    return json.dumps(jsonreq).encode('utf-8')

def tellActiveFull(offset=0, max=5000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["method"] = "aria2.tellActive"
    return json.dumps(jsonreq).encode('utf-8')

def tellWaitingFull(offset=0, max=5000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [offset, max]
    jsonreq["method"] = "aria2.tellWaiting"
    return json.dumps(jsonreq).encode('utf-8')

def tellStoppedFull(offset=0, max=5000, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [offset, max]
    jsonreq["method"] = "aria2.tellStopped"
    return json.dumps(jsonreq).encode('utf-8')

def tellStatusFull(gid, token=None):
    jsonreq = { 'jsonrpc': '2.0', 'id': 'qwer', 'params' : [f"token:{token}"] }
    jsonreq["params"] = [] if token in [None, ""] else [f"token:{token}"]
    jsonreq["params"] += [gid]
    jsonreq["method"] = "aria2.tellStatus"
    return json.dumps(jsonreq).encode('utf-8')

def sendReqFull(jsonreq, url="http://localhost", port=6800):
    with rq.urlopen(f'{url}:{port}/jsonrpc', jsonreq) as c:
        response = c.read()
    js_rs = json.loads(response)
    # return response
    return js_rs

# https://aria2.github.io/manual/en/html/aria2c.html#input-file
input_file_accepted_options = [
    "all-proxy",
    "all-proxy-passwd",
    "all-proxy-user",
    "allow-overwrite",
    "allow-piece-length-change",
    "always-resume",
    "async-dns",
    "auto-file-renaming",
    "bt-enable-hook-after-hash-check",
    "bt-enable-lpd",
    "bt-exclude-tracker",
    "bt-external-ip",
    "bt-force-encryption",
    "bt-hash-check-seed",
    "bt-load-saved-metadata",
    "bt-max-peers",
    "bt-metadata-only",
    "bt-min-crypto-level",
    "bt-prioritize-piece",
    "bt-remove-unselected-file",
    "bt-request-peer-speed-limit",
    "bt-require-crypto",
    "bt-save-metadata",
    "bt-seed-unverified",
    "bt-stop-timeout",
    "bt-tracker",
    "bt-tracker-connect-timeout",
    "bt-tracker-interval",
    "bt-tracker-timeout",
    "check-integrity",
    "checksum",
    "conditional-get",
    "connect-timeout",
    "content-disposition-default-utf8",
    "continue",
    "dir",
    "dry-run",
    "enable-http-keep-alive",
    "enable-http-pipelining",
    "enable-mmap",
    "enable-peer-exchange",
    "file-allocation",
    "follow-metalink",
    "follow-torrent",
    "force-save",
    "ftp-passwd",
    "ftp-pasv",
    "ftp-proxy",
    "ftp-proxy-passwd",
    "ftp-proxy-user",
    "ftp-reuse-connection",
    "ftp-type",
    "ftp-user",
    "gid",
    "hash-check-only",
    "header",
    "http-accept-gzip",
    "http-auth-challenge",
    "http-no-cache",
    "http-passwd",
    "http-proxy",
    "http-proxy-passwd",
    "http-proxy-user",
    "http-user",
    "https-proxy",
    "https-proxy-passwd",
    "https-proxy-user",
    "index-out",
    "lowest-speed-limit",
    "max-connection-per-server",
    "max-download-limit",
    "max-file-not-found",
    "max-mmap-limit",
    "max-resume-failure-tries",
    "max-tries",
    "max-upload-limit",
    "metalink-base-uri",
    "metalink-enable-unique-protocol",
    "metalink-language",
    "metalink-location",
    "metalink-os",
    "metalink-preferred-protocol",
    "metalink-version",
    "min-split-size",
    "no-file-allocation-limit",
    "no-netrc",
    "no-proxy",
    "out",
    "parameterized-uri",
    "pause",
    "pause-metadata",
    "piece-length",
    "proxy-method",
    "realtime-chunk-checksum",
    "referer",
    "remote-time",
    "remove-control-file",
    "retry-wait",
    "reuse-uri",
    "rpc-save-upload-metadata",
    "seed-ratio",
    "seed-time",
    "select-file",
    "split",
    "ssh-host-key-md",
    "stream-piece-selector",
    "timeout",
    "uri-selector",
    "use-head",
    "user-agent",
]
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#- TORRENT
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
