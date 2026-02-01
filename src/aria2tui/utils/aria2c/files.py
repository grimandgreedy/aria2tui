#!/bin/python
# -*- coding: utf-8 -*-
"""
files.py - File operations and UI macros

Functions for opening download locations, opening completed files,
and UI macros for file interactions.

Author: GrimAndGreedy
License: MIT
"""

import os
import sys
import json
import subprocess
import shlex
import mimetypes
from collections import defaultdict

from aria2tui.utils.logging_utils import get_logger
from listpick import *
from listpick.listpick_app import *
from listpick.ui.keys import *
from .core import get_config, config_manager

logger = get_logger()


def openDownloadLocation(gid: str, new_window: bool = True) -> None:
    """Opens the download location for a given download."""
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getFiles, sendReq, getOption

    try:
        os.system("cls" if os.name == "nt" else "clear")
        req = getFiles(str(gid))
        response = sendReq(req)
        val = json.loads(json.dumps(response))
        files = val["result"]
        if len(files) == 0:
            return None
        loc = files[0]["path"]
        if "/" not in loc:
            req = getOption(str(gid))
            response = sendReq(req)
            val = json.loads(json.dumps(response))
            loc = val["result"]["dir"]

        config = get_config()
        terminal_file_manager = config["general"]["terminal_file_manager"]
        gui_file_manager = config["general"]["gui_file_manager"]
        if new_window:
            cmd = f"{gui_file_manager} {repr(loc)}"
            subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        else:
            cmd = f"{terminal_file_manager} {repr(loc)}"
            subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    except:
        pass


def openGidFiles(gids: list[str]) -> None:
    """
    Open download files. We best guess the file opener based on platform.
    """
    # Import here to avoid circular dependency during module initialization
    from aria2tui.utils.aria2c import getFiles, sendReq, getOption

    if isinstance(gids, str):
        gids = [gids]
    files_list = []

    for gid in gids:
        try:
            req = getFiles(str(gid))
            response = sendReq(req)
            val = json.loads(json.dumps(response))
            files = val["result"]
            if len(files) == 0:
                continue
            loc = files[0]["path"]
            if "/" not in loc:
                req = getOption(str(gid))
                response = sendReq(req)
                val = json.loads(json.dumps(response))
                loc = val["dir"]

            files_list.append(loc)
        except:
            pass
    openFiles(files_list)


def openFiles(files: list[str]) -> None:
    """
    Opens multiple files using their associated applications.

    Platforms:
      • macOS — uses `open`, groups by bundle id when possible.
      • Linux/BSD — uses `gio launch` or falls back to `xdg-open`.
      • Android (Termux) — uses `termux-open`, else `am start`.

    Files sharing the same default app are opened together where possible.

    Args:
        files (list[str]): A list of file paths.
    """

    def command_exists(cmd: str) -> bool:
        """Return True if command exists in PATH."""
        return (
            subprocess.call(f"type {shlex.quote(cmd)} > /dev/null 2>&1", shell=True)
            == 0
        )

    def is_android() -> bool:
        """Rudimentary Android/Termux detection."""
        return (
            os.path.exists("/system/bin/am")
            or "com.termux" in os.environ.get("PREFIX", "")
            or "ANDROID_ROOT" in os.environ
        )

    # pick main open command
    if sys.platform == "darwin":
        open_cmd = "open"
    elif is_android():
        open_cmd = "termux-open" if command_exists("termux-open") else "am start"
    elif command_exists("gio"):
        open_cmd = "gio open"
    elif command_exists("xdg-open"):
        open_cmd = "xdg-open"
    else:
        raise EnvironmentError(
            "No open command found (termux-open, am, gio, or xdg-open)"
        )

    def get_mime_types(file_list: list[str]) -> dict[str, list[str]]:
        """Map MIME types to lists of files."""
        types = defaultdict(list)
        for f in file_list:
            mime = None
            if command_exists("xdg-mime"):
                try:
                    out = (
                        subprocess.run(
                            f"xdg-mime query filetype {shlex.quote(f)}",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                        )
                        .stdout.decode()
                        .strip()
                    )
                    if out:
                        mime = out
                except Exception:
                    pass
            if not mime:
                mime, _ = mimetypes.guess_type(f)
                if not mime:
                    mime = "application/octet-stream"
            types[mime].append(f)
        return types

    def get_default_app(mime: str) -> str:
        """Return default app id or command for a MIME type."""
        if sys.platform == "darwin":
            return None
        if is_android():
            return open_cmd
        if command_exists("xdg-mime"):
            out = (
                subprocess.run(
                    f"xdg-mime query default {shlex.quote(mime)}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                .stdout.decode()
                .strip()
            )
            return out or open_cmd
        return open_cmd

    types_map = get_mime_types(files)
    apps_files = defaultdict(list)

    # group files by app
    if sys.platform == "darwin":
        for f in files:
            try:
                out = (
                    subprocess.run(
                        f"mdls -name kMDItemCFBundleIdentifier -raw {shlex.quote(f)}",
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                    )
                    .stdout.decode()
                    .strip()
                )
                bundle = (
                    out
                    if out and out != "(null)"
                    else os.path.splitext(f)[1] or "unknown"
                )
            except Exception:
                bundle = os.path.splitext(f)[1] or "unknown"
            apps_files[bundle].append(f)
    else:
        for mime, flist in types_map.items():
            app = get_default_app(mime)
            apps_files[app].extend(flist)

    # launch groups
    for app, flist in apps_files.items():
        # Ensure all file paths are absolute
        abs_flist = [os.path.abspath(os.path.expanduser(f)) for f in flist]

        if is_android() and open_cmd == "termux-open" and command_exists("termux-open"):
            for f in abs_flist:
                subprocess.Popen(f"termux-open {shlex.quote(f)}", shell=True)
            continue

        quoted = " ".join(shlex.quote(f) for f in abs_flist)

        if sys.platform == "darwin":
            if app and app.startswith("com."):
                subprocess.Popen(f"open -b {shlex.quote(app)} {quoted}", shell=True)
            else:
                subprocess.Popen(f"open {quoted}", shell=True)

        elif is_android():
            for f in abs_flist:
                uri = f"file://{f}"
                subprocess.Popen(
                    f"am start -a android.intent.action.VIEW -d {shlex.quote(uri)}",
                    shell=True,
                )

        elif (
            isinstance(app, str) and app.endswith(".desktop") and command_exists("gio")
        ):
            app_path = None
            for base in (
                "/usr/share/applications",
                os.path.expanduser("~/.local/share/applications"),
            ):
                path = os.path.join(base, app)
                if os.path.exists(path):
                    app_path = path
                    break
            if app_path:
                subprocess.Popen(
                    f"gio launch {shlex.quote(app_path)} {quoted}", shell=True
                )
            else:
                subprocess.Popen(f"xdg-open {quoted}", shell=True)

        elif "xdg-open" in open_cmd:
            subprocess.Popen(f"xdg-open {quoted}", shell=True)
        else:
            subprocess.Popen(f"{open_cmd} {quoted}", shell=True)


# Import macros from the macros module
from .macros import aria2tui_macros
