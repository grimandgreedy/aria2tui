#!/bin/python
# -*- coding: utf-8 -*-

"""
cli.py

Command-line interface for aria2tui.

---

Called from the main app hook.

If we handle an argument in cli mode then we exit. Otherwise we continue
    to the TUI app loop.

1. parse_args
2. handle_cli_mode

---

Author: GrimAndGreedy
License: MIT
"""

import os
import sys
import time
import argparse
import subprocess
from typing import Tuple

from listpick.listpick_app import start_curses, close_curses

from aria2tui.utils.aria2c_utils import (
    testConnection,
    classify_download_string,
    addDownload,
    addTorrent,
    sendReq,
    get_config,
    config_manager,
)
from aria2tui.utils.aria_adduri import addDownloadFull
from aria2tui.utils.logging_utils import get_logger

logger = get_logger()


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for aria2tui.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        prog="aria2tui",
        description="Terminal UI for aria2c download manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--conf",
        metavar="INSTANCE",
        dest="conf",
        help="Specify config instance from aria2tui config. Specify instance index (0-indexed) or instance name.",
    )

    parser.add_argument(
        "--add_download",
        metavar="URI",
        dest="add_download",
        help="Add a download (magnet, HTTP, FTP, torrent file)",
    )

    parser.add_argument(
        "--add_download_bg",
        metavar="URI",
        dest="add_download_bg",
        help="Add a download in background mode (with gui prompt if connection isn't up). Useful for scripts not run directly from the command line.",
    )

    parser.add_argument(
        "--input_file",
        metavar="FILE",
        dest="input_file",
        help="Add downloads from an input file. File format is the same as aria2c input files.",
    )

    parser.add_argument(
        "--pause",
        metavar="GID",
        dest="pause_gid",
        help="Pause a specific download by GID.",
    )

    parser.add_argument(
        "--pause_all",
        action="store_true",
        dest="pause_all",
        help="Pause all active downloads.",
    )

    parser.add_argument(
        "--resume",
        metavar="GID",
        dest="resume_gid",
        help="Resume a specific paused download by GID.",
    )

    parser.add_argument(
        "--resume_all",
        action="store_true",
        dest="resume_all",
        help="Resume all paused downloads.",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        dest="clear_completed",
        help="Clear the list of stopped downloads and errors.",
    )

    return parser.parse_args()


def handle_download_addition_bg(uri: str) -> None:
    """
    Handle download addition in background mode with GUI prompts.

    Args:
        uri: The URI/path to add as a download
    """
    connection_up = testConnection()

    if not connection_up:
        exit_ = False
        try:
            import tkinter as tk
            from tkinter import messagebox

            # No main window
            root = tk.Tk()
            root.withdraw()

            response = messagebox.askyesno(
                "Aria2TUI", "Aria2c connection failed. Start daemon?"
            )

            if not response:
                exit_ = True
            else:
                # Attempt to start aria2c
                config = config_manager.get_current_instance()
                for cmd in config["general"]["startup_commands"]:
                    subprocess.run(
                        cmd,
                        shell=True,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                    )
                time.sleep(0.1)

        except Exception as e:
            logger.exception("Error in background download flow: %s", e)
            message = "Problem encountered. Download not added."
            # os.system(f"notify-send '{message}'")
            sys.exit(1)
        finally:
            if exit_:
                message = "Exiting. Download not added."
                # os.system(f"notify-send '{message}'")
                sys.exit(0)

            connection_up = testConnection()
            if not connection_up:
                message = "Problem encountered. Check your aria2tui config. Download not added."
                # os.system(f"notify-send '{message}'")
                sys.exit(1)

    # Add the download
    success, message = add_download_from_uri(uri)

    # Send notification
    # os.system(f"notify-send '{message}'")
    sys.exit(0 if success else 1)


def handle_download_addition(uri: str) -> None:
    """
    Handle download addition in foreground mode with TUI prompts.

    Args:
        uri: The URI/path to add as a download
    """
    from aria2tui.aria2tui_app import handleAriaStartPromt

    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    # Add the download
    success, message = add_download_from_uri(uri)

    print(message)
    sys.exit(0 if success else 1)


def add_download_from_uri(uri: str) -> Tuple[bool, str]:
    """
    Add a download based on URI type.

    Args:
        uri: The URI/path to add (magnet, HTTP, FTP, metalink, or torrent file)

    Returns:
        Tuple of (success: bool, message: str)
    """
    dl_type = classify_download_string(uri)
    logger.info("Adding download: uri=%s type=%s", uri, dl_type)

    if dl_type in ["Magnet", "Metalink", "FTP", "HTTP"]:
        try:
            url, port, token = (
                config_manager.get_url(),
                config_manager.get_port(),
                config_manager.get_token(),
            )
            return_val, gid = addDownloadFull(
                uri=uri, token=token, url=url, port=int(port)
            )
            if return_val:
                message = f"Success! download added: gid={gid}."
                return True, message
            else:
                message = "Error adding download."
                return False, message
        except Exception as e:
            logger.exception("Error adding download '%s': %s", uri, e)
            return False, "Error adding download."

    elif dl_type == "Torrent File":
        try:
            js_req = addTorrent(uri)
            sendReq(js_req)
            message = "Torrent added successfully."
            return True, message
        except Exception as e:
            logger.exception("Error adding torrent file '%s': %s", uri, e)
            return False, "Error adding torrent."

    else:
        logger.error("Unrecognized download type for uri: %s", uri)
        return False, "Error: unrecognized download type."


def handle_input_file(file_path: str) -> None:
    """
    Handle download addition from an input file.

    Args:
        file_path: Path to the input file containing download URIs and options
    """
    from aria2tui.utils.aria2c.downloads import (
        input_file_lines_to_dict,
        process_downloads_list,
    )
    from aria2tui.aria2tui_app import handleAriaStartPromt

    # Check connection
    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    # Read and process the input file
    try:
        expanded_path = os.path.expanduser(os.path.expandvars(file_path))

        if not os.path.exists(expanded_path):
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

        with open(expanded_path, "r") as f:
            lines = f.readlines()

        dls_list, argstrs = input_file_lines_to_dict(lines)

        if not dls_list:
            print("No downloads found in input file.")
            sys.exit(0)

        gids, message = process_downloads_list(dls_list)

        print(message)
        if gids:
            print(f"GIDs: {', '.join(gids)}")

        sys.exit(0 if gids else 1)

    except Exception as e:
        logger.exception("Error processing input file '%s': %s", file_path, e)
        print(f"Error processing input file: {str(e)}")
        sys.exit(1)


def handle_pause(gid: str) -> None:
    """Pause a specific download by GID."""
    from aria2tui.lib.aria2c_wrapper import pauseFull, sendReqFull
    from aria2tui.aria2tui_app import handleAriaStartPromt

    # Check connection
    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    try:
        url = config_manager.get_url()
        port = int(config_manager.get_port())
        token = config_manager.get_token()

        jsonreq = pauseFull(gid=gid, token=token)
        response = sendReqFull(jsonreq, url=url, port=port)

        if "result" in response:
            print(f"Download {gid} paused successfully.")
            sys.exit(0)
        else:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            print(f"Error pausing download: {error_msg}")
            sys.exit(1)

    except Exception as e:
        logger.exception("Error pausing download %s: %s", gid, e)
        print(f"Error pausing download: {str(e)}")
        sys.exit(1)


def handle_pause_all() -> None:
    """Pause all active downloads."""
    from aria2tui.lib.aria2c_wrapper import pauseAllFull, sendReqFull
    from aria2tui.aria2tui_app import handleAriaStartPromt

    # Check connection
    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    try:
        url = config_manager.get_url()
        port = int(config_manager.get_port())
        token = config_manager.get_token()

        jsonreq = pauseAllFull(token=token)
        response = sendReqFull(jsonreq, url=url, port=port)

        if "result" in response:
            print("All active downloads paused successfully.")
            sys.exit(0)
        else:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            print(f"Error pausing downloads: {error_msg}")
            sys.exit(1)

    except Exception as e:
        logger.exception("Error pausing all downloads: %s", e)
        print(f"Error pausing downloads: {str(e)}")
        sys.exit(1)


def handle_resume(gid: str) -> None:
    """Resume a specific paused download by GID."""
    from aria2tui.lib.aria2c_wrapper import unpauseFull, sendReqFull
    from aria2tui.aria2tui_app import handleAriaStartPromt

    # Check connection
    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    try:
        url = config_manager.get_url()
        port = int(config_manager.get_port())
        token = config_manager.get_token()

        jsonreq = unpauseFull(gid=gid, token=token)
        response = sendReqFull(jsonreq, url=url, port=port)

        if "result" in response:
            print(f"Download {gid} resumed successfully.")
            sys.exit(0)
        else:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            print(f"Error resuming download: {error_msg}")
            sys.exit(1)

    except Exception as e:
        logger.exception("Error resuming download %s: %s", gid, e)
        print(f"Error resuming download: {str(e)}")
        sys.exit(1)


def handle_resume_all() -> None:
    """Resume all paused downloads."""
    from aria2tui.lib.aria2c_wrapper import unpauseAllFull, sendReqFull
    from aria2tui.aria2tui_app import handleAriaStartPromt

    # Check connection
    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    try:
        url = config_manager.get_url()
        port = int(config_manager.get_port())
        token = config_manager.get_token()

        jsonreq = unpauseAllFull(token=token)
        response = sendReqFull(jsonreq, url=url, port=port)

        if "result" in response:
            print("All paused downloads resumed successfully.")
            sys.exit(0)
        else:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            print(f"Error resuming downloads: {error_msg}")
            sys.exit(1)

    except Exception as e:
        logger.exception("Error resuming all downloads: %s", e)
        print(f"Error resuming downloads: {str(e)}")
        sys.exit(1)


def handle_clear_completed() -> None:
    """Clear the list of stopped downloads and errors."""
    from aria2tui.lib.aria2c_wrapper import removeCompletedFull, sendReqFull
    from aria2tui.aria2tui_app import handleAriaStartPromt

    # Check connection
    connection_up = testConnection()

    if not connection_up:
        stdscr = start_curses()
        handleAriaStartPromt(stdscr)
        close_curses(stdscr)

    try:
        url = config_manager.get_url()
        port = int(config_manager.get_port())
        token = config_manager.get_token()

        jsonreq = removeCompletedFull(token=token)
        response = sendReqFull(jsonreq, url=url, port=port)

        if "result" in response:
            print("Completed downloads and errors cleared successfully.")
            sys.exit(0)
        else:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            print(f"Error clearing completed downloads: {error_msg}")
            sys.exit(1)

    except Exception as e:
        logger.exception("Error clearing completed downloads: %s", e)
        print(f"Error clearing completed downloads: {str(e)}")
        sys.exit(1)


def handle_cli_mode(args: argparse.Namespace) -> bool:
    """
    Handle CLI-only mode (non-interactive download additions).

    Args:
        args: Parsed command-line arguments

    Returns:
        True if CLI mode was handled (app should exit), False if TUI mode should start
    """
    config_set = False

    if args.conf:
        if not args.conf.isdigit():
            try:
                ind = config_manager.get_instance_names().index(args.conf)
                config_manager.switch_instance(ind)

            except ValueError:
                print(f"No config instance named {args.conf}.\nExiting...")
                return True
        else:
            ## Config specified by name
            ind = int(args.conf)
            if 0 <= ind < config_manager.get_instance_count():
                config_manager.switch_instance(ind)
            else:
                print(f"Config instance {ind} not in range.\nExiting...")
                return True

        print(f"Config set to {config_manager.get_current_instance()['name']}")

        config_set = True

    # Handle background download addition
    if args.add_download_bg:
        handle_download_addition_bg(args.add_download_bg)
        return True

    # Handle foreground download addition
    if args.add_download:
        handle_download_addition(args.add_download)
        return True

    # Handle input file
    if args.input_file:
        handle_input_file(args.input_file)
        return True

    # Handle pause by GID
    if args.pause_gid:
        handle_pause(args.pause_gid)
        return True

    # Handle pause all
    if args.pause_all:
        handle_pause_all()
        return True

    # Handle resume by GID
    if args.resume_gid:
        handle_resume(args.resume_gid)
        return True

    # Handle resume all
    if args.resume_all:
        handle_resume_all()
        return True

    # Handle clear completed
    if args.clear_completed:
        handle_clear_completed()
        return True

    if config_set:
        return True
    # No CLI mode specified, continue to TUI
    return False
