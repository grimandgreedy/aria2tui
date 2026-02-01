#!/bin/python
# -*- coding: utf-8 -*-
"""
macros.py - UI macros for aria2tui

Interactive macros for download management operations including
file operations, queue management, and clipboard operations.

Author: GrimAndGreedy
License: MIT
"""

import os
from aria2tui.utils.logging_utils import get_logger

logger = get_logger()


def open_files_macro(picker) -> None:
    """Open files of selected downloads, or hovered if none selected."""
    from .files import openFiles

    # Get files to open
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    dl_types = [picker.items[selected_index][10] for selected_index in selections]
    dl_names = [picker.items[selected_index][2] for selected_index in selections]
    dl_paths = [picker.items[selected_index][9] for selected_index in selections]

    files_to_open = []

    for i in range(len(selections)):
        file_full_path = os.path.expanduser(os.path.join(dl_paths[i], dl_names[i]))
        if os.path.exists(file_full_path):
            files_to_open.append(file_full_path)

    openFiles(files_to_open)


def open_hovered_location(picker) -> None:
    """Open location of hovered download in a new GUI window."""
    from .files import openDownloadLocation

    if not picker.indexed_items:
        return None
    gid = picker.indexed_items[picker.cursor_pos][1][-1]
    openDownloadLocation(gid, new_window=True)


def reload_alternate_config(picker) -> None:
    """Reload config from alternate path."""
    from .core import config_manager

    logger.info("Before reload - Token: %s", config_manager.get_token()[:20] + "...")
    logger.info("Before reload - URL: %s", config_manager.get_url())

    config_manager.reload("/Users/noah/.config/torrents.toml")

    logger.info("After reload - Token: %s", config_manager.get_token()[:20] + "...")
    logger.info("After reload - URL: %s", config_manager.get_url())
    logger.info("Config reloaded from /Users/noah/.config/torrents.toml")


def yank_paths_macro(picker) -> None:
    """
    Yank (copy to clipboard) the paths of selected downloads.
    If no downloads are selected, yank the hovered download path.
    """
    import pyperclip

    # Get selected downloads or fallback to hovered
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    # Extract paths from selected downloads
    # picker.items[index][9] is the directory path
    # picker.items[index][2] is the filename
    paths = []
    for selected_index in selections:
        dl_path = picker.items[selected_index][9]
        dl_name = picker.items[selected_index][2]
        full_path = os.path.expanduser(os.path.join(dl_path, dl_name))
        paths.append(full_path)

    # Join all paths with newlines
    paths_text = "\n".join(paths)

    # Copy to clipboard
    try:
        pyperclip.copy(paths_text)
        logger.info("Yanked %d path(s) to clipboard", len(paths))
    except Exception as e:
        logger.exception("Error copying to clipboard: %s", e)


def clear_completed_macro(picker) -> None:
    """Clear all completed and errored downloads from the list."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import removeCompleted, sendReq

    try:
        req = removeCompleted()
        sendReq(req)
        logger.info("Cleared all completed and errored downloads")
    except Exception as e:
        logger.exception("Error clearing completed downloads: %s", e)


def toggle_pause_resume_macro(picker) -> None:
    """
    Toggle pause/resume for selected downloads.
    If no downloads are selected, toggle the hovered download.
    Paused downloads will be resumed, active/waiting downloads will be paused.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import pause, unpause, tellStatus, sendReq

    # Get selected downloads or fallback to hovered
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    # Get GIDs from selections
    gids = [picker.indexed_items[sel][1][-1] for sel in selections]

    for gid in gids:
        try:
            # Get current status
            status_req = tellStatus(gid)
            status_response = sendReq(status_req)
            status = status_response["result"]["status"]

            # Toggle based on current status
            if status == "paused":
                req = unpause(gid)
                sendReq(req)
                logger.info("Resumed download %s", gid)
            elif status in ["active", "waiting"]:
                req = pause(gid)
                sendReq(req)
                logger.info("Paused download %s", gid)
        except Exception as e:
            logger.exception("Error toggling pause/resume for %s: %s", gid, e)


def promote_to_top_macro(picker) -> None:
    """
    Promote selected downloads to the top of the queue.
    If no downloads are selected, promote the hovered download.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import changePosition, sendReq

    # Get selected downloads or fallback to hovered
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    # Get GIDs from selections
    gids = [picker.indexed_items[sel][1][-1] for sel in selections]

    for gid in gids:
        try:
            # Move to position 0 (top of queue)
            req = changePosition(gid, pos=0, how="POS_SET")
            sendReq(req)
            logger.info("Promoted download %s to top of queue", gid)
        except Exception as e:
            logger.exception("Error promoting download %s: %s", gid, e)


def send_to_back_macro(picker) -> None:
    """
    Send selected downloads to the back of the queue.
    If no downloads are selected, send the hovered download to the back.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import changePosition, sendReq

    # Get selected downloads or fallback to hovered
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    # Get GIDs from selections
    gids = [picker.indexed_items[sel][1][-1] for sel in selections]

    for gid in gids:
        try:
            # Move to end of queue using POS_END
            req = changePosition(gid, pos=0, how="POS_END")
            sendReq(req)
            logger.info("Sent download %s to back of queue", gid)
        except Exception as e:
            logger.exception("Error sending download %s to back: %s", gid, e)


def remove_download_macro(picker) -> None:
    """
    Remove selected downloads from the queue.
    If no downloads are selected, remove the hovered download.
    Handles active, waiting, paused, completed, and errored downloads.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c.downloads import remove_downloads

    # Get selected downloads or fallback to hovered
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    # Get GIDs from selections
    gids = [picker.indexed_items[sel][1][-1] for sel in selections]

    try:
        # Use the existing remove_downloads function which handles all statuses
        remove_downloads(gids)
        logger.info("Removed %d download(s)", len(gids))
    except Exception as e:
        logger.exception("Error removing downloads: %s", e)


def show_info_macro(picker) -> None:
    """
    Show detailed information about selected downloads.
    If no downloads are selected, show info for the hovered download.
    Displays all download info in a picker view.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getAllInfo
    from aria2tui.utils.aria2c.downloads import applyToDownloads
    from aria2tui.utils.aria2c.core import Operation

    # Get selected downloads or fallback to hovered
    selections = [i for i, selected in picker.selections.items() if selected]
    if not selections:
        if not picker.indexed_items:
            return None
        selections = [picker.indexed_items[picker.cursor_pos][0]]

    # Get GIDs and filenames from selections
    gids = [picker.indexed_items[sel][1][-1] for sel in selections]
    fnames = [picker.items[sel][2] for sel in selections]

    # Create operation for displaying all info
    info_operation = Operation(
        name="Download Information",
        function=lambda stdscr, gid, fname, operation, function_args: getAllInfo(gid),
        form_view=True,
    )

    try:
        # Get the stdscr from the picker
        stdscr = picker.stdscr

        # Apply the operation to show info
        applyToDownloads(
            stdscr=stdscr,
            operation=info_operation,
            gids=gids,
            user_opts="",
            fnames=fnames,
        )
        logger.info("Displayed info for %d download(s)", len(gids))
    except Exception as e:
        logger.exception("Error displaying download info: %s", e)


aria2tui_macros = [
    {
        "keys": [ord("o")],
        "description": "Open files of selected downloads.",
        "function": open_files_macro,
    },
    {
        "keys": [ord("O")],
        "description": "Open location of hovered download in a new (gui) window.",
        "function": open_hovered_location,
    },
    {
        "keys": [ord("y")],
        "description": "Yank (copy) paths of selected downloads to clipboard.",
        "function": yank_paths_macro,
    },
    {
        "keys": [ord("C")],
        "description": "Clear all completed and errored downloads.",
        "function": clear_completed_macro,
    },
    {
        "keys": [ord("p")],
        "description": "Toggle pause/resume for selected downloads.",
        "function": toggle_pause_resume_macro,
    },
    {
        "keys": [ord("+")],
        "description": "Promote selected downloads to top of queue.",
        "function": promote_to_top_macro,
    },
    {
        "keys": [ord("-")],
        "description": "Send selected downloads to back of queue.",
        "function": send_to_back_macro,
    },
    {
        "keys": [ord("d")],
        "description": "Remove selected downloads.",
        "function": remove_download_macro,
    },
    {
        "keys": [ord("i")],
        "description": "Show detailed information about selected downloads.",
        "function": show_info_macro,
    },
]
