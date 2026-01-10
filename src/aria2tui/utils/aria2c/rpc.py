#!/bin/python
# -*- coding: utf-8 -*-
"""
rpc.py - RPC communication layer

Handles communication with the aria2c daemon over RPC, including
connection testing, batch data retrieval, and download status queries.

Author: GrimAndGreedy
License: MIT
"""

import os
import json
import tabulate
from urllib import request as rq
from typing import Tuple

from aria2tui.lib.aria2c_wrapper import (
    listMethods, getVersionFull, getOptionFull, getFilesFull,
    tellActiveFull, tellWaitingFull, tellStoppedFull,
    getServersFull, getPeersFull, getUrisFull, tellStatusFull, sendReqFull
)
from .format import dataToPickerRows, bytes_to_human_readable


def testConnectionFull(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests if we can connect to the url and port. """
    url = f'{url}:{port}/jsonrpc'
    try:
        with rq.urlopen(url, listMethods(), timeout=1) as c:
            response = c.read()
        return True
    except:
        return False


def testAriaConnectionFull(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests the connection to the Aria2 server. In particular we test if our token works to get protected data. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getVersion

    url = f'{url}:{port}/jsonrpc'
    try:
        with rq.urlopen(url, getVersion(), timeout=1) as c:
            response = c.read()
        return True
    except:
        return False


def te(url: str = "http://localhost", port: int = 6800) -> bool:
    """ Tests the connection to the Aria2 server. """
    url = f'{url}:{port}/jsonrpc'
    try:
        with rq.urlopen(url, listMethods(), timeout=1) as c:
            response = c.read()
        return True
    except:
        return False


def getOptionAndFileInfo(gids: list[str]) -> Tuple[list, list]:
    """
    Get option and file info for each GID. Used for fetching download data for Picker rows.
    We split the gid requests into batches of 2000 to ensure that we get a resposne.
    """
    options_batch = []
    files_info_batch = []
    for i in range(len(gids)//2000 + 1):
        tmp_options_batch, tmp_files_info_batch = getOptionAndFileInfoBatch(gids[i*2000:(i+1)*2000])
        options_batch += tmp_options_batch
        files_info_batch += tmp_files_info_batch
    return options_batch, files_info_batch


def getOptionAndFileInfoBatch(gids: list[str]) -> Tuple[list, list]:
    """ Batch-get option and file info for each GID. Used for fetching download data for Picker rows. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getOption, getFiles, sendReq

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


def getQueue(show_pc_bar: bool = True) -> Tuple[list[list[str]], list[str]]:
    """ Retrieves download queue and corresponding header from aria2 over rpc. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import sendReq, tellWaiting

    js_rs = sendReq(tellWaiting())
    gids = [dl["gid"] for dl in js_rs["result"]]
    options_batch, files_info_batch = getOptionAndFileInfo(gids)

    items, header = dataToPickerRows(js_rs["result"], options_batch, files_info_batch, show_pc_bar)
    items.sort(key=lambda x:x[1], reverse=True)

    return items, header


def getStopped(show_pc_bar: bool = True) -> Tuple[list[list[str]], list[str]]:
    """ Retrieves stopped downloads and corresponding header from aria2 over rpc. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import sendReq, tellStopped

    js_rs = sendReq(tellStopped())
    gids = [dl["gid"] for dl in js_rs["result"]]
    options_batch, files_info_batch = getOptionAndFileInfo(gids)

    items, header = dataToPickerRows(js_rs["result"], options_batch, files_info_batch, show_pc_bar)

    for item in items:
        item[0] = ""                # Remove indices; only useful for queue numbering


    return items[::-1], header


def getActive(show_pc_bar: bool = True) -> Tuple[list[list[str]], list[str]]:
    """ Retrieves active downloads and corresponding header from aria2 over rpc. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import sendReq, tellActive

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


def getAllInfo(gid: str) -> list[dict]:
    """
    Retrieves all information about an aria2 download.

    Returns:
        list: A list of key/value dictionaries containing the options and information about the downloads.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import sendReq, getFiles, getServers, getPeers, getUris, getOption, tellStatus

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


def getAll(items, header, visible_rows_indices, getting_data, state):
    """ Retrieves all downloads: active, stopped, and queue. Also returns the header. """
    active, aheader = getActive()
    stopped, sheader = getStopped()
    waiting, wheader = getQueue()

    dir_index = wheader.index("DIR")
    all = active + waiting + stopped, wheader
    home = "/home/" + os.getlogin()
    for row in all[0]:

        if row[dir_index].startswith(home):
            row[dir_index] = "~" + row[dir_index][len(home):]

    items[:] = active + waiting + stopped
    header[:] = wheader

    getting_data.set()


def returnAll() -> Tuple[list[list[str]], list[str]]:
    """ Retrieves all downloads: active, stopped, and queue. Also returns the header. """
    active, aheader = getActive()
    stopped, sheader = getStopped()
    waiting, wheader = getQueue()

    dir_index = wheader.index("DIR")
    all = active + waiting + stopped, wheader
    home = "/home/" + os.getlogin()
    for row in all[0]:

        if row[dir_index].startswith(home):
            row[dir_index] = "~" + row[dir_index][len(home):]

    return all


def getGlobalSpeed() -> str:
    """ Get global upload/download speeds and download counts. """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import sendReq, getGlobalStat

    resp = sendReq(getGlobalStat())
    up = bytes_to_human_readable(resp['result']['uploadSpeed'])
    down = bytes_to_human_readable(resp['result']['downloadSpeed'])
    numActive = resp['result']['numActive']
    numStopped = resp['result']['numStopped']
    numWaiting = resp['result']['numWaiting']
    return f"{down}/s 󰇚 {up}/s 󰕒 | {numActive}A {numWaiting}W {numStopped}S"
