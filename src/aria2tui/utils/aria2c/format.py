#!/bin/python
# -*- coding: utf-8 -*-
"""
format.py - Data formatting and conversion utilities

Contains pure functions for formatting data for display, converting
between formats, and transforming download data for UI presentation.

Author: GrimAndGreedy
License: MIT
"""

from typing import Tuple

# Import from listpick for helper functions (format_size, convert_percentage_to_ascii_bar, convert_seconds)
try:
    from listpick.listpick_app import format_size, convert_percentage_to_ascii_bar, convert_seconds
except ImportError:
    # Fallback if listpick doesn't export these
    def format_size(size):
        """Fallback format_size if not available from listpick"""
        return bytes_to_human_readable(size)

    def convert_seconds(seconds:int, long_format:bool=False) -> str:
        """ Convert seconds to human readable format. E.g., 60*60*24*3+62=772262 -> 3d2m2s """
        if isinstance(seconds, str):
            seconds = int(seconds)

        # Calculate years, days, hours, minutes, and seconds
        years = seconds // (365 * 24 * 3600)
        days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
        hours = (seconds % (24 * 3600)) // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60

        # Long format = years, days, hours, minutes, seconds
        if long_format:
            human_readable = []
            if years > 0:
                human_readable.append(f"{years} year{'s' if years > 1 else ''}")
            if days > 0:
                human_readable.append(f"{days} day{'s' if days > 1 else ''}")
            if hours > 0:
                human_readable.append(f"{hours} hour{'s' if hours > 1 else ''}")
            if minutes > 0:
                human_readable.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
            if remaining_seconds > 0 or not human_readable:
                human_readable.append(f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}")
            return ', '.join(human_readable)
        else:
            # Compact format = y, d, h, m, s
            compact_parts = []
            if years > 0:
                compact_parts.append(f"{years}y")
            if days > 0:
                compact_parts.append(f"{days}d")
            if hours > 0:
                compact_parts.append(f"{hours}h")
            if minutes > 0:
                compact_parts.append(f"{minutes}m")
            if remaining_seconds > 0 or not compact_parts:
                compact_parts.append(f"{remaining_seconds}s")
            return ''.join(compact_parts)

def convert_percentage_to_ascii_bar(p: int, chars: int = 6) -> str:
    """ Convert percentage to an ascii status bar of length chars. """
    # Clamp percentage between 0 and 100
    p = max(0, min(100, p))
    
    # Calculate exact progress
    exact_progress = p / 100 * chars
    filled = int(exact_progress)
    remainder = exact_progress - filled
    
    # Determine if we need a partial character
    if remainder > 0 and filled < chars:
        partial = '▌'  # Half-filled block
        empty = chars - filled - 1
    else:
        partial = ''
        empty = chars - filled
    
    # Create the bar
    bar = '█' * filled + partial + ' ' * empty
    
    return f"[{bar}]"




def get_selected_indices(selections: dict[int, bool]) -> list[int]:
    """ Return a list of indices which are True in the selections dictionary. """

    # selected_indices = [items[i] for i, selected in selections.values() if selected]
    selected_indices = [i for i, selected in selections.items() if selected]
    return selected_indices

def bytes_to_human_readable(size: float, sep =" ", round_at=1) -> str:
    """
    Convert a number of bytes to a human readable string.

    size (int): the number of bytes
    sep (str): the string that should separate the size from the units.
                A single space by default.
    round_at (int): the unit below which the figure should be rounded
            round_at=0:  0.0B, 23.1KB, 2.3MB
            round_at=1:  0B, 23.1KB, 2.3MB
            round_at=2:  0B, 23KB, 2.3MB

    Examples:
    1024000 -> 1 MB
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    if isinstance(size, str):
        size=float(size)
    i = 0
    while size >= 1024 and i < len(suffixes)-1:
        size /= 1024.0
        i += 1
    if i < round_at:
        size_str = f"{int(size)}"
    else:
        size_str = f"{size:.1f}"
    return f"{size_str}{sep}{suffixes[i]}"


def flatten_data(y, delim="."):
    out = {}

    def flatten(x, name='', delim="."):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + delim)
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + delim)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y, delim=delim)
    return out


def unflatten_data(y, delim="."):
    out = {}

    def unflatten(x, parent_key='', delim="."):
        if type(x) is dict:
            for k, v in x.items():
                new_key = f"{parent_key}{delim}{k}" if parent_key else k
                unflatten(v, new_key, delim)
        else:
            keys = parent_key.split(delim)
            current_dict = out
            for key in keys[:-1]:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]
            current_dict[keys[-1]] = x

    unflatten(y)
    return out


def dataToPickerRows(dls, options_batch, files_info_batch, show_pc_bar: bool = True):
    """ Take list of dl dicts and return list of desired attributes along with a header. """
    items = []
    for i, dl in enumerate(dls):
        try:
            options = options_batch[i]
            files_info = files_info_batch[i]
            gid = dl['gid']
            pth = options["result"]["dir"]
            if "out" in options["result"]:
                fname = options["result"]["out"]
            else:
                orig_path = dl['files'][0]['path']
                fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            dltype = "direct"
            try:
                if "bittorrent" in dl:
                    dltype = "torrent"
                    fname = dl["bittorrent"]["info"]["name"]
            except: pass
            status = dl['status']

            size = 0
            for file in files_info['result']:
                if 'length' in file:
                    if 'selected' in file and file['selected'] == "true":
                        size += int(file['length'])
            # size = int(dl['files'][0]['length'])
            completed = 0
            for file in files_info['result']:
                if 'completedLength' in file:
                    if 'selected' in file and file['selected'] == "true":
                        completed += int(file['completedLength'])
            # completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left: time_left_s = convert_seconds(time_left)
            else: time_left_s = ""

            try:
                uri = files_info["result"][0]["uris"][0]["uri"]
            except:
                uri = ""

            row = [str(i), status, fname, format_size(size), format_size(completed), f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left_s, pth, dltype, uri, gid]
            if show_pc_bar: row.insert(5, pc_bar)
            items.append(row)
        except:
            pass

    header = ["", "Status", "Name", "Size", "Done", "%", "Speed", "Time", "DIR", "Type", "URI", "GID"]
    if show_pc_bar: header.insert(5, "%")
    return items, header


def process_dl_dict(dls):
    if "result" in dls:
        dls = dls["result"]
    for dl in dls:
        for key in dl:
            if key in ["length", "completedLength"]:
                dl[key] = bytes_to_human_readable(dl[key])
    return dls
