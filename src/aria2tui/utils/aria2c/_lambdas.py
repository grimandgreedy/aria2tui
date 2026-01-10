#!/bin/python
# -*- coding: utf-8 -*-
"""
_lambdas.py - Lambda wrappers with config injection

This module provides lambda functions that wrap aria2c RPC functions
with pre-filled configuration values (url, port, token). These lambdas
simplify the API by removing the need to pass config on every call.

Note: This module is private (prefixed with _) and should not be imported
directly. Use the public API from __init__.py instead.

Author: GrimAndGreedy
License: MIT
"""

from aria2tui.lib.aria2c_wrapper import *
from aria2tui.utils.aria_adduri import addDownloadFull
from .core import get_config
from .rpc import testConnectionFull, testAriaConnectionFull
from .downloads import (
    addUrisFull, addUrisAndPauseFull, addTorrentsFull,
    addTorrentsFilePickerFull, addDownloadsAndTorrentsFull,
    addDownloadsAndTorrentsAndPauseFull, retryDownloadFull,
    retryDownloadAndPauseFull
)

# Get config once at module initialization
config = get_config()
url = config["general"]["url"]
port = config["general"]["port"]
token = config["general"]["token"]
paginate = config["general"]["paginate"]

# Create lambda functions which fill the url, port, and token for our aria2c rpc operations

addUri = lambda uri, out="", dir=None, queue_pos=10000: addUriFull(uri, out=out, dir=dir, queue_pos=queue_pos, token=token)
addTorrent = lambda path, out="", dir=None, queue_pos=10000: addTorrentFull(path, out=out, dir=dir, queue_pos=queue_pos, token=token)
addDownload = lambda uri, url=url, port=port, token=token, queue_pos=None, prompt=False, cookies_file="", download_options_dict={}: addDownloadFull(uri, queue_position=queue_pos, url=url, port=port, token=token, prompt=prompt, cookies_file=cookies_file, download_options_dict=download_options_dict)
getOption = lambda gid: getOptionFull(gid, token=token)
getServers = lambda gid: getServersFull(gid, token=token)
getPeers = lambda gid: getPeersFull(gid, token=token)
getUris = lambda gid: getUrisFull(gid, token=token)
getGlobalOption = lambda: getGlobalOptionFull(token=token)
getSessionInfo = lambda: getSessionInfoFull(token=token)
getVersion = lambda: getVersionFull(token=token)
getGlobalStat = lambda: getGlobalStatFull(token=token)
pause = lambda gid: pauseFull(gid, token=token)
retryDownload = lambda gid: retryDownloadFull(gid, url=url, port=port, token=token)
retryDownloadAndPause = lambda gid: retryDownloadAndPauseFull(gid, url=url, port=port, token=token)
pauseAll = lambda: pauseAllFull(token=token)
forcePauseAll = lambda: forcePauseAllFull(token=token)
unpause = lambda gid: unpauseFull(gid, token=token)
remove = lambda gid: removeFull(gid, token=token)
forceRemove = lambda gid: forceRemoveFull(gid, token=token)
removeDownloadResult = lambda gid: removeDownloadResultFull(gid, token=token)
getFiles = lambda gid: getFilesFull(gid, token=token)
removeCompleted = lambda: removeCompletedFull(token=token)
changePosition = lambda gid, pos, how="POS_SET": changePositionFull(gid, pos, how=how, token=token)
changeOption = lambda gid, key, val: changeOptionFull(gid, key, val, token=token)
tellActive = lambda offset=0, max=10000: tellActiveFull(offset=0, max=max, token=token)
tellWaiting = lambda offset=0, max=10000: tellWaitingFull(offset=0, max=max, token=token)
tellStopped = lambda offset=0, max=10000: tellStoppedFull(offset=0, max=max, token=token)
tellStatus = lambda gid: tellStatusFull(gid, token=token)
sendReq = lambda jsonreq, url=url, port=port: sendReqFull(jsonreq, url=url, port=port)
addTorrents = lambda url=url, port=port, token=token: addTorrentsFull(url=url, port=port, token=token)
addTorrentsFilePicker = lambda url=url, port=port, token=token: addTorrentsFilePickerFull(url=url, port=port, token=token)
addUris = lambda url=url, port=port, token=token: addUrisFull(url=url, port=port, token=token)
addUrisAndPause = lambda url=url, port=port, token=token: addUrisAndPauseFull(url=url, port=port, token=token)
addDownloadsAndTorrents = lambda url=url, port=port, token=token: addDownloadsAndTorrentsFull(url=url, port=port, token=token)
addDownloadsAndTorrentsAndPause = lambda url=url, port=port, token=token: addDownloadsAndTorrentsAndPauseFull(url=url, port=port, token=token)
testConnection = lambda url=url, port=port: testConnectionFull(url=url, port=port)
testAriaConnection = lambda url=url, port=port: testAriaConnectionFull(url=url, port=port)
