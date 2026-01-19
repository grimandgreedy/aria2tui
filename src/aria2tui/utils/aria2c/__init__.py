#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2c utilities package - Public API

This package provides utilities for interacting with aria2c.
All public functions are re-exported from this module for backward compatibility.

Author: GrimAndGreedy
License: MIT
"""

# Import order matters for circular dependency prevention

# 1. Core (no internal dependencies)
from .core import (
    Operation,
    get_config,
    get_default_config,
    config_file_exists,
    get_config_path,
    get_default_config_for_form,
    create_config_from_form,
    restartAria,
    editConfig,
    classify_download_string,
)

# 2. Format (pure functions, no internal dependencies)
from .format import (
    bytes_to_human_readable,
    flatten_data,
    unflatten_data,
    dataToPickerRows,
    process_dl_dict,
)

# 3. RPC (depends on format)
from .rpc import (
    testConnectionFull,
    testAriaConnectionFull,
    te,
    getOptionAndFileInfo,
    getOptionAndFileInfoBatch,
    getActive,
    getQueue,
    getStopped,
    getAllInfo,
    getAll,
    returnAll,
    printResults,
    getGlobalSpeed,
)

# 4. Options (depends on format)
from .options import (
    changeOptionDialog,
    changeOptionBatchDialog,
    changeOptionPicker,
    changeOptionsBatchPicker,
    changeFilenamePicker,
    changeFilenameForm,
    download_selected_files,
)

# 5. Downloads (depends on core, format)
from .downloads import (
    addUrisFull,
    addUrisAndPauseFull,
    addTorrentsFull,
    addTorrentsFilePickerFull,
    addDownloadTasksForm,
    addDownloadsAndTorrentsFull,
    addDownloadsAndTorrentsAndPauseFull,
    input_file_lines_to_dict,
    retryDownloadFull,
    retryDownloadAndPauseFull,
    remove_downloads,
    applyToDownloads,
)

# 6. Files (depends on core)
from .files import (
    openDownloadLocation,
    openGidFiles,
    openFiles,
    open_files_macro,
    open_hovered_location,
    aria2tui_macros,
)

# 7. Initialize lambda wrappers (MUST BE LAST)
# These need config loaded and other modules available
from . import _lambdas

# Re-export all lambda wrappers for public API
addUri = _lambdas.addUri
addTorrent = _lambdas.addTorrent
addDownload = _lambdas.addDownload
getOption = _lambdas.getOption
getServers = _lambdas.getServers
getPeers = _lambdas.getPeers
getUris = _lambdas.getUris
getGlobalOption = _lambdas.getGlobalOption
getSessionInfo = _lambdas.getSessionInfo
getVersion = _lambdas.getVersion
getGlobalStat = _lambdas.getGlobalStat
pause = _lambdas.pause
retryDownload = _lambdas.retryDownload
retryDownloadAndPause = _lambdas.retryDownloadAndPause
pauseAll = _lambdas.pauseAll
forcePauseAll = _lambdas.forcePauseAll
unpause = _lambdas.unpause
remove = _lambdas.remove
forceRemove = _lambdas.forceRemove
removeDownloadResult = _lambdas.removeDownloadResult
getFiles = _lambdas.getFiles
removeCompleted = _lambdas.removeCompleted
changePosition = _lambdas.changePosition
changeOption = _lambdas.changeOption
tellActive = _lambdas.tellActive
tellWaiting = _lambdas.tellWaiting
tellStopped = _lambdas.tellStopped
tellStatus = _lambdas.tellStatus
sendReq = _lambdas.sendReq
addTorrents = _lambdas.addTorrents
addTorrentsFilePicker = _lambdas.addTorrentsFilePicker
addUris = _lambdas.addUris
addUrisAndPause = _lambdas.addUrisAndPause
addDownloadsAndTorrents = _lambdas.addDownloadsAndTorrents
addDownloadsAndTorrentsAndPause = _lambdas.addDownloadsAndTorrentsAndPause
testConnection = _lambdas.testConnection
testAriaConnection = _lambdas.testAriaConnection

# Also export config at module level for compatibility
config = _lambdas.config
url = _lambdas.url
port = _lambdas.port
token = _lambdas.token
paginate = _lambdas.paginate

# Define __all__ for wildcard imports (preserves current behavior)
__all__ = [
    # Core
    'Operation',
    'get_config',
    'get_default_config',
    'config_file_exists',
    'get_config_path',
    'get_default_config_for_form',
    'create_config_from_form',
    'restartAria',
    'editConfig',
    'classify_download_string',
    # Format
    'bytes_to_human_readable',
    'flatten_data',
    'unflatten_data',
    'dataToPickerRows',
    'process_dl_dict',
    # RPC
    'testConnectionFull',
    'testAriaConnectionFull',
    'te',
    'getOptionAndFileInfo',
    'getOptionAndFileInfoBatch',
    'getActive',
    'getQueue',
    'getStopped',
    'getAllInfo',
    'getAll',
    'returnAll',
    'printResults',
    'getGlobalSpeed',
    # Options
    'changeOptionDialog',
    'changeOptionBatchDialog',
    'changeOptionPicker',
    'changeOptionsBatchPicker',
    'changeFilenamePicker',
    'changeFilenameForm',
    'download_selected_files',
    # Downloads
    'addUrisFull',
    'addUrisAndPauseFull',
    'addTorrentsFull',
    'addTorrentsFilePickerFull',
    'addDownloadTasksForm',
    'addDownloadsAndTorrentsFull',
    'addDownloadsAndTorrentsAndPauseFull',
    'input_file_lines_to_dict',
    'retryDownloadFull',
    'retryDownloadAndPauseFull',
    'remove_downloads',
    'applyToDownloads',
    # Files
    'openDownloadLocation',
    'openGidFiles',
    'openFiles',
    'open_files_macro',
    'open_hovered_location',
    'aria2tui_macros',
    # Lambda wrappers
    'addUri',
    'addTorrent',
    'addDownload',
    'getOption',
    'getServers',
    'getPeers',
    'getUris',
    'getGlobalOption',
    'getSessionInfo',
    'getVersion',
    'getGlobalStat',
    'pause',
    'retryDownload',
    'retryDownloadAndPause',
    'pauseAll',
    'forcePauseAll',
    'unpause',
    'remove',
    'forceRemove',
    'removeDownloadResult',
    'getFiles',
    'removeCompleted',
    'changePosition',
    'changeOption',
    'tellActive',
    'tellWaiting',
    'tellStopped',
    'tellStatus',
    'sendReq',
    'addTorrents',
    'addTorrentsFilePicker',
    'addUris',
    'addUrisAndPause',
    'addDownloadsAndTorrents',
    'addDownloadsAndTorrentsAndPause',
    'testConnection',
    'testAriaConnection',
    # Config variables
    'config',
    'url',
    'port',
    'token',
    'paginate',
]
