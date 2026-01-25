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
from .core import config_manager
from .rpc import testConnectionFull, testAriaConnectionFull
from .downloads import (
    addUrisFull, addUrisAndPauseFull, addTorrentsFull,
    addTorrentsFilePickerFull, addDownloadsAndTorrentsFull,
    addDownloadsAndTorrentsAndPauseFull, retryDownloadFull,
    retryDownloadAndPauseFull
)

# Helper functions to access config dynamically
# These allow backward compatibility for code that accesses config, url, port, token
def get_current_config():
    """Get current config (dynamically reloads)."""
    return config_manager.get_config()

def get_current_url():
    """Get current URL (dynamically reloads)."""
    return config_manager.get_url()

def get_current_port():
    """Get current port (dynamically reloads)."""
    return int(config_manager.get_port())

def get_current_token():
    """Get current token (dynamically reloads)."""
    return config_manager.get_token()

# For backward compatibility, expose these at module level
# These will reference the initial config, but lambdas use config_manager directly
config = config_manager.get_config()
url = config_manager.get_url()
port = config_manager.get_port()
token = config_manager.get_token()

# Create lambda functions that access config dynamically via config_manager
# This ensures they always use the latest config values after reload

addUri = lambda uri, out="", dir=None, queue_pos=10000: addUriFull(uri, out=out, dir=dir, queue_pos=queue_pos, token=config_manager.get_token())
addTorrent = lambda path, out="", dir=None, queue_pos=10000: addTorrentFull(path, out=out, dir=dir, queue_pos=queue_pos, token=config_manager.get_token())
addDownload = lambda uri, url=None, port=None, token=None, queue_pos=None, prompt=False, cookies_file="", download_options_dict={}: addDownloadFull(uri, queue_position=queue_pos, url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token(), prompt=prompt, cookies_file=cookies_file, download_options_dict=download_options_dict)
getOption = lambda gid: getOptionFull(gid, token=config_manager.get_token())
getServers = lambda gid: getServersFull(gid, token=config_manager.get_token())
getPeers = lambda gid: getPeersFull(gid, token=config_manager.get_token())
getUris = lambda gid: getUrisFull(gid, token=config_manager.get_token())
getGlobalOption = lambda: getGlobalOptionFull(token=config_manager.get_token())
changeGlobalOption = lambda options: changeGlobalOptionFull(options, token=config_manager.get_token())
getSessionInfo = lambda: getSessionInfoFull(token=config_manager.get_token())
getVersion = lambda: getVersionFull(token=config_manager.get_token())
getGlobalStat = lambda: getGlobalStatFull(token=config_manager.get_token())
pause = lambda gid: pauseFull(gid, token=config_manager.get_token())
retryDownload = lambda gid: retryDownloadFull(gid, url=config_manager.get_url(), port=int(config_manager.get_port()), token=config_manager.get_token())
retryDownloadAndPause = lambda gid: retryDownloadAndPauseFull(gid, url=config_manager.get_url(), port=int(config_manager.get_port()), token=config_manager.get_token())
pauseAll = lambda: pauseAllFull(token=config_manager.get_token())
forcePauseAll = lambda: forcePauseAllFull(token=config_manager.get_token())
unpause = lambda gid: unpauseFull(gid, token=config_manager.get_token())
remove = lambda gid: removeFull(gid, token=config_manager.get_token())
forceRemove = lambda gid: forceRemoveFull(gid, token=config_manager.get_token())
removeDownloadResult = lambda gid: removeDownloadResultFull(gid, token=config_manager.get_token())
getFiles = lambda gid: getFilesFull(gid, token=config_manager.get_token())
removeCompleted = lambda: removeCompletedFull(token=config_manager.get_token())
changePosition = lambda gid, pos, how="POS_SET": changePositionFull(gid, pos, how=how, token=config_manager.get_token())
changeOption = lambda gid, key, val: changeOptionFull(gid, key, val, token=config_manager.get_token())
tellActive = lambda offset=0, max=10000: tellActiveFull(offset=0, max=max, token=config_manager.get_token())
tellWaiting = lambda offset=0, max=10000: tellWaitingFull(offset=0, max=max, token=config_manager.get_token())
tellStopped = lambda offset=0, max=10000: tellStoppedFull(offset=0, max=max, token=config_manager.get_token())
tellStatus = lambda gid: tellStatusFull(gid, token=config_manager.get_token())
sendReq = lambda jsonreq, url=None, port=None: sendReqFull(jsonreq, url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()))
addTorrents = lambda url=None, port=None, token=None: addTorrentsFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token())
addTorrentsFilePicker = lambda url=None, port=None, token=None: addTorrentsFilePickerFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token())
addUris = lambda url=None, port=None, token=None: addUrisFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token())
addUrisAndPause = lambda url=None, port=None, token=None: addUrisAndPauseFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token())
addDownloadsAndTorrents = lambda url=None, port=None, token=None: addDownloadsAndTorrentsFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token())
addDownloadsAndTorrentsAndPause = lambda url=None, port=None, token=None: addDownloadsAndTorrentsAndPauseFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()), token=token or config_manager.get_token())
testConnection = lambda url=None, port=None: testConnectionFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()))
testAriaConnection = lambda url=None, port=None: testAriaConnectionFull(url=url or config_manager.get_url(), port=int(port) if port else int(config_manager.get_port()))
