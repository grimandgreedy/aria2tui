#!/bin/python
from subprocess import run
from urllib import request as rq
import urllib
import copy
import json

from sqlalchemy.engine import cursor
from list_picker import *
from list_picker_colours import get_colours
from table_to_list_of_lists import *
import time
import multiprocessing
import queue
import os
from time import sleep
import curses
from aria2c_wrapper import *
from aria_adduri import add_download
import tempfile
import tomllib

"""
todo 

 - refresh menu with a timer
 - add retry download function by getting download data, remove it and readd it
 - info is wrong for torrents. The size, % completed, etc. Might need to rework the the data scraped from the json response.
 - remove completed not working
 - fix adding uris with filename. Data is the same but it is corrupted somehow.
    - works:        https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg
    - doesn't work: https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLBVWNXUrlGnx3VtnPULUE6v0EteQg
 - fix crash when terminal is too small
 - get all function
 - merge columns
 - add empty values for inapplicable cols
 - allow index
 - add a config file (~/.config/ariatui.conf) which contains the rpc url, port, secret, etc.
 - fix not resizing properly
 - Add hidden columns to function so that they remain hidden on refresh
 - Add a view all tasks option
 - Add color to highlight errored and completed tasks
 - implement proper retrydownload function 
 - allow options when adding uris; perhaps use the same structure as the aria2c input file
 - improve menu navigation
    - when downloads are selected and we go back they should still be selected
 - redo menu order
 - fix dir; it should be obtained from getInfo; 
    - E.g., 4chan downloads don't show filename or dir as dir is based on filename
 - should the colours be:
    - completed: green
    - active: blue
    - paused: ??? gray?
 - after nvim is opened (e.g., show all dl info) the display needs to be redrawn
 - fix filenames; also check torrents
 - add highlights for % complete
 - create watch all
 - make operations on downloads into a batch request
 - examine parsing of toml (why are the arguments set outside of the main function?)
 - make fetching active, queue, and stopped downloads into a batch request (all)
 - add to config
    - highlights off
    - color off
 - live setting changes
    - theme
 - make percentage bar look nicer
 - watch active only refreshes upon a keypress
 - when the item order refreshes (e.g. new downloads added) the selected items change. need to associate the selected items with gids and then create new selected items which will be passed back
 - takes us back to the top when it refreshes in a different mode (I think due to filter)
 - add pin_cursor option to prevent the cursor from going down when refreshing
 - add url to test_connection
 - specifying name doesn't work with magnet links
 - add global stats bar
 - monitor log file
 - setup https connection

DONE
 - If a download is paused and it is paused again it throws an error when it should just skip it.
 - implement addTorrent
 - Return a list of files and % completed for each file in a torrent.
 - check if remove completed/errored is working
 - show all downloads (not just 500)
    - set max=5000 which should be fine
 - Add a getAllInfo option for downloads
 - open location
 - figure out how to keep the row constant when going back and forth between menus
 - make fetching active, queue, and stopped downloads into a batch request
 - (!!!) high CPU usage
    - when val in `stdscr.timeout(val)` is low the cpu usage is high


"""
# TODO:  <14-11-24, noah> Run only one ncurses wrapper so that it doesn't flash the terminal screen when switching between menus#


# def send_req(jsonreq, port=6800):
#     with rq.urlopen(f'http://localhost:{port}/jsonrpc', jsonreq) as c:
#         response = c.read()
#
#     js_rs = json.loads(response)
#     return response


def test_connection(port=6800):
    url = f'http://localhost:{port}/jsonrpc'
    try:
        # with rq.urlopen(url, getGlobalStat()) as c:
        print(getVersion())
        with rq.urlopen(url, getVersion()) as c:
            response = c.read()
        return True
    except urllib.error.URLError:
        return False

def convert_seconds(seconds, long_format=False):
    # Ensure the input is an integer
    if isinstance(seconds, str):
        seconds = int(seconds)

    # Calculate years, days, hours, minutes, and seconds
    years = seconds // (365 * 24 * 3600)
    days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    # Build the human-readable format
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
        # Compact format: using abbreviated units
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

def convert_percentage_to_ascii_bar(p, chars=8):
    # Convert percentage to an ascii status bar

    done = "█"
    notdone = "▒"
    return done * int(p / 100 * chars) + (chars-(int(p / 100 * chars)))*notdone
    return "[" + "=" * int(p / 100 * chars) + ">" + " " * (chars - int(p / 100 * chars) - 1) + "]"

def __getQueue():
    js_rs = send_req(tellWaiting())

    items = []

    # print(f"{' Waiting ':*^50}")
    # print("*"*50)
    # for i in range(len(js_rs["result"])):

    options_batch = []
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = send_req(json.dumps(options_batch).encode('utf-8'))

    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        # print(f"{'Queue Position':<{colsize}}: {i}")
        try:
            # gid = dl['gid']
            # pth = dl['files'][0]['path']
            # fname = pth[pth.rfind("/")+1:]
            gid = dl['gid']
            options = options_batch[i]
            pth = options["result"]["dir"]
            orig_path = dl['files'][0]['path']
            fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            # options = send_req(getOption(gid))
            # pth = options["result"]["dir"]
            # fname = options["result"]["out"]
            try:
                if "bittorrent" in dl:
                    tmp = dl["bittorrent"]["info"]["name"]
                    fname = tmp
            except: pass

            status = dl['status']
            # print(f"{'Path':<{colsize}}: {pth[:70]}")
            # print(f"{'Filename':<{colsize}}: {fname}")
            # print(f"{'Status':<{colsize}}: {dl['status']}")
            # print(f"{'GID':<{colsize}}: {dl['gid']}")
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            # print(f"{'Size':<{colsize}}: {size/1024**2:.02f}MB")
            # print(f"{'Completed':<{colsize}}: {completed/1024**2:.02f}MB")
            # print(f"{'% Completed':<{colsize}}: {100*pc_complete:.02f}%")
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = "INF"
        
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB")
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB")
            # entries.append({"path":pth,"fname":fname,"gid":dl['gid'],})

            # row = [i, status, fname, format_size(size), format_size(completed), f"{pc_complete*100:.2f}", format_size(dl_speed)+"/s", time_left, pth, gid]
            row = [i, status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left, pth, gid]
            items.append(row)
        except:
            print("ERR")
            # print(dl)
        # print("*"*50)
    # header = ["", "status", "fname", "size", "completed", "%", "dl_speed", "time_left", "dir", "gid"]
    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
    # print(response)
    return items, header

def __getFromQueue(pos=[]):
    if type(pos) ==  type(1): pos = [pos]

    jsonreq = tellWaiting()

    # with rq.urlopen('http://localhost:6800/jsonrpc', jsonreq) as c:
    #     js_rs = c.read()
    #
    # js_rs = json.loads(response)
    js_rs = send_req(jsonreq)
    # js_rs = json.loads(response)

    # print(json.dumps(js_rs, indent=4))
    entries = []


    # print(f"{' Waiting ':*^50}")
    # print("*"*50)
    # for i in range(len(js_rs["result"])):
    for i in range(len(js_rs["result"])-1, -1, -1):
        if i not in pos: continue
        dl = js_rs["result"][i]
        colsize = 14
        # print(f"{'Queue Position':<{colsize}}: {i}")
        try:
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            # print(f"{'Path':<{colsize}}: {pth[:70]}")
            # print(f"{'Filename':<{colsize}}: {fname}")
            # print(f"{'Status':<{colsize}}: {dl['status']}")
            # print(f"{'GID':<{colsize}}: {dl['gid']}")
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            # print(f"{'Size':<{colsize}}: {size/1024**2:.02f}MB")
            # print(f"{'Completed':<{colsize}}: {completed/1024**2:.02f}MB")
            # print(f"{'% Completed':<{colsize}}: {100*pc_complete:.02f}%")
        
            dl_speed = int(dl['downloadSpeed'])
        
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB")
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB")
            # entries.append({"path":pth,"fname":fname,"gid":dl['gid'],})
        except:
            print("ERR")
        #     print(dl)
        # print("*"*50)

def __getQueueCompact():
    jsonreq = tellWaiting()

    # with rq.urlopen('http://localhost:6800/jsonrpc', jsonreq) as c:
    #     response = c.read()
    #
    # js_rs = json.loads(response)
    js_rs = send_req(jsonreq)
    # js_rs = json.loads(response)

    # print(json.dumps(js_rs, indent=4))
    entries = []

    # print(f"{' Waiting ':*^50}")
    # print("*"*50)
    # for i in range(len(js_rs["result"])):
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        # print(f"{'Queue Position':<{colsize}}: {i}")
        try:
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            status = dl['status'].strip()
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            status_char = status_chars[status]
            
            fn_width = 65
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])

            # line = f"{i:0>{len(str(len(js_rs["result"])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%  {dl_speed}"
            line = f"{i:0>{len(str(len(js_rs['result'])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%"
            # print(line)
        
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB")
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB")
            # entries.append({"path":pth,"fname":fname,"gid":dl['gid'],})
        except:
            print("ERR")
            print(dl)

def __getStopped():
    jsonreq = tellStopped()

    # with rq.urlopen('http://localhost:6800/jsonrpc', jsonreq) as c:
    #     response = c.read()

    js_rs = send_req(tellStopped())
    # js_rs = json.loads(response)

    # print(json.dumps(js_rs, indent=4))
    entries = []
    items = []

    # print(f"{' Stopped ':*^50}")
    # print("*"*50)
    # for i in range(len(js_rs["result"])):
    options_batch = []
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = send_req(json.dumps(options_batch).encode('utf-8'))


    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        # print(f"{'Queue Position':<{colsize}}: {i}")
        try:
            gid = dl['gid']
            # options = send_req(getOption(gid))
            options = options_batch[i]
            pth = options["result"]["dir"]
            orig_path = dl['files'][0]['path']
            fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            # fname = options["result"]["out"]
            status = dl['status']
            # print(f"{'Path':<{colsize}}: {pth[:70]}")
            # print(f"{'Filename':<{colsize}}: {fname}")
            # print(f"{'Status':<{colsize}}: {dl['status']}")
            # print(f"{'GID':<{colsize}}: {dl['gid']}")
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            # print(f"{'Size':<{colsize}}: {size/1024**2:.02f}MB")
            # print(f"{'Completed':<{colsize}}: {completed/1024**2:.02f}MB")
            # print(f"{'% Completed':<{colsize}}: {100*pc_complete:.02f}%")
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = "INF"
        
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB")
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB")
            # entries.append({"path":pth,"fname":fname,"gid":dl['gid'],})
            # row = [fname, status, format_size(size), format_size(completed), f"{ pc_complete*100 :.1f}", format_size(dl_speed)+"/s", time_left, pth, gid]
            row = ["NA", status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left, pth, gid]
            items.append(row)
        except:
            print("ERR")
            print(dl)
        # print("*"*50)
    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
    return items, header

def __getStoppedCompact():
    jsonreq = tellStopped()

    # with rq.urlopen('http://localhost:6800/jsonrpc', jsonreq) as c:
    #     response = c.read()
    #
    # js_rs = json.loads(response)
    js_rs = send_req(jsonreq)
    # js_rs = json.loads(response)

    # print(json.dumps(js_rs, indent=4))
    entries = []

    # print(f"{' Stopped ':*^50}")
    # print("*"*50)
    # for i in range(len(js_rs["result"])):
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        colsize = 14
        # print(f"{'Queue Position':<{colsize}}: {i}")
        try:
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            status = dl['status'].strip()
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            # print("1")
            status_char = status_chars[status]
            
            # print("2")
            fn_width = 65
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            # print("3")
        
            dl_speed = int(dl['downloadSpeed'])
            # print("4")

            # line = f"{i:0>{len(str(len(js_rs["result"])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%  {dl_speed}"
            line = f"{i:0>{len(str(len(js_rs['result'])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%"
            print(line)
        
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB")
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB")
            # entries.append({"path":pth,"fname":fname,"gid":dl['gid'],})
        except:
            print("ERR")
            print(dl)

def __getActive(print_output=False):

    js_rs = send_req(tellActive())
    items = []

    if print_output:
        print(f"{' Active ':*^50}")
        print("*"*50)

    options_batch = []
    for i in range(len(js_rs["result"])-1, -1, -1):
        dl = js_rs["result"][i]
        gid = dl['gid']
        options = json.loads(getOption(gid))
        options_batch.append(options)
        
    options_batch = send_req(json.dumps(options_batch).encode('utf-8'))

    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            colsize = 14
            gid = dl['gid']
            options = options_batch[i]
            pth = options["result"]["dir"]
            if "out" in options["result"]:
                fname = options["result"]["out"]
            else:
                orig_path = dl['files'][0]['path']
                fname = orig_path[orig_path.rfind("/")+1:]
            if fname == "":   # get from url
                url = dl['files'][0]['uris'][0]["uri"]
                fname = url[url.rfind("/")+1:]
            # fname = js_rs2["result"]["out"]
            # pth = dl['files'][0]['path']
            # fname = pth[pth.rfind("/")+1:]
            try:
                if "bittorrent" in dl:
                    tmp = dl["bittorrent"]["info"]["name"]
                    fname = tmp
            except: pass
            status = dl['status']
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left: time_left_s = convert_seconds(time_left)
            else: time_left_s = "INF"
            # time_left_s = f"{time_left//60**2%60}h" + f"{time_left//60%60}m" + f"{time_left%60}s" if time_left else "INF"

            if print_output:
                print(f"{'Path':<{colsize}}: {pth[:70]}")
                print(f"{'Filename':<{colsize}}: {fname}")
                print(f"{'Status':<{colsize}}: {dl['status']}")
                print(f"{'GID':<{colsize}}: {dl['gid']}")
                print(f"{'Size':<{colsize}}: {size/1024**2:.02f}MB")
                print(f"{'Completed':<{colsize}}: {completed/1024**2:.02f}MB")
                print(f"{'% Completed':<{colsize}}: {100*pc_complete:.02f}%")
                print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB/s")
                print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB/s")
                print(f"{'Time Left':<{colsize}}: {time_left_s}")

            # row = [fname, status, format_size(size), format_size(completed), f"{pc_complete*100:.2f}", format_size(dl_speed)+"/s", time_left_s, pth, gid]
            row = ["NA", status, fname, format_size(size), format_size(completed), pc_bar, f"{pc_complete*100:.1f}%", format_size(dl_speed)+"/s", time_left_s, pth, gid]
            items.append(row)
        except:
            print("ERR")
            print(dl)

        if print_output:
            print("*"*50)
    header = ["", "status", "fname", "size", "completed", "%", "%", "dl_speed", "time_left", "dir", "gid"]
    return items, header

def __getActiveCompact():
    jsonreq = tellActive()

    # with rq.urlopen('http://localhost:6800/jsonrpc', jsonreq) as c:
    #     response = c.read()
    #
    # js_rs = json.loads(response)
    js_rs = send_req(jsonreq)
    # js_rs = json.loads(response)

    # print(json.dumps(js_rs, indent=4))

    # print(f"{' Active ':*^50}")
    # print("*"*50)

    fn_width = 65
    header = f"{'Q'} {'S'}  {'File Name':{fn_width}}  {'Size':8}  {'%done'}  {'DL speed'}  {'Time Left'}"
    print(header)
    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        try:
            colsize = 14
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left:
                time_left_s = ""
                time_left_s += f"{time_left//60**2%60}h" if time_left//60**2 > 1 else ""
                time_left_s += f"{time_left//60%60}m" if time_left//60 > 1 else ""
                time_left_s += f"{time_left%60}s"
            else: time_left_s = "INF"
            # time_left_s = f"{time_left//60**2%60}h" + f"{time_left//60%60}m" + f"{time_left%60}s" if time_left else "INF"
            
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            status = dl['status'].strip()
            status_chars = {
                    'waiting':'w',
                    'paused':'p',
                    'active':'a', 
                    'error': 'e',
                    'complete':'c'
                    }
            status_char = status_chars[status]
            
            fn_width = 65
            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
        
            dl_speed = int(dl['downloadSpeed'])

            # line = f"{i:0>{len(str(len(js_rs["result"])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size}  {pc_complete}%  {dl_speed}"
            line = f"{i:0>{len(str(len(js_rs['result'])-1))}} {status_char}  {fname[:fn_width]:{fn_width}}  {size/1024**2:.02f}MB  {pc_complete*100:.01f}%  {dl_speed/1024:.02f}KB/s  {time_left_s}s"
            print(line)


        except:
            print("ERR")
            print(dl)

def __getPaused():
    jsonreq = tellWaiting()

    # with rq.urlopen('http://localhost:6800/jsonrpc', jsonreq) as c:
    #     response = c.read()
    #
    # js_rs = json.loads(response)
    js_rs = send_req(jsonreq)
    # js_rs = json.loads(response)

    # print(json.dumps(js_rs, indent=4))

    # print(f"{' Paused ':*^50}")
    # print("*"*50)
    gids=[]

    for i in range(len(js_rs["result"])):
        dl = js_rs["result"][i]
        if "paused" not in dl['status']: continue
        try:
            colsize = 14
            pth = dl['files'][0]['path']
            fname = pth[pth.rfind("/")+1:]
            # print(f"{'Path':<{colsize}}: {pth[:70]}")
            # print(f"{'Filename':<{colsize}}: {fname}")
            # print(f"{'Status':<{colsize}}: {dl['status']}")
            # print(f"{'GID':<{colsize}}: {dl['gid']}")

            size = int(dl['files'][0]['length'])
            completed = int(dl['files'][0]['completedLength'])
            pc_complete = completed/size if size > 0 else 0
            pc_bar = convert_percentage_to_ascii_bar(pc_complete*100)
            # print(f"{'Completed':<{colsize}}: {completed/1024**2:.02f}MB")
            # print(f"{'% Completed':<{colsize}}: {100*pc_complete:.02f}%")
        
            dl_speed = int(dl['downloadSpeed'])
            time_left = int((size-completed)/dl_speed) if dl_speed > 0 else None
            if time_left:
                time_left_s = ""
                time_left_s += f"{time_left//60**2%60}h" if time_left//60**2 > 1 else ""
                time_left_s += f"{time_left//60%60}m" if time_left//60 > 1 else ""
                time_left_s += f"{time_left%60}s"
            else: time_left_s = "INF"
            # time_left_s = f"{time_left//60**2%60}h" + f"{time_left//60%60}m" + f"{time_left%60}s" if time_left else "INF"
            
        
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024:.02f}kB/s")
            # print(f"{'D/l speed':<{colsize}}: {dl_speed/1024**2:.02f}MB/s")
            # print(f"{'Time Left':<{colsize}}: {time_left_s}")

            gids.append(dl['gid'])

        except:
            print("ERR")
            print(dl)
    #     print("*"*50)
    # print(f"gids = {gids}")


def run_with_timeout(function, args, kwargs, timeout):
    result_queue = multiprocessing.Queue()

    # Create a wrapper function to pass both positional and keyword arguments, and a result queue
    def wrapper():
        function(*args, result_queue=result_queue, **kwargs)

    p = multiprocessing.Process(target=wrapper)
    p.start()
    p.join(timeout)  # Wait for `timeout` seconds or until process finishes

    if p.is_alive():
        p.terminate()  # Terminate the process if still alive after timeout
        p.join()  # Ensure process has terminated
        result = None
        print("Curses application terminated due to timeout")
    else:
        print("Curses application completed successfully")
        try:
            result = result_queue.get_nowait()
        except queue.Empty:
            result = None

    return result

def watch_active(stdscr):
    stdscr.clear()
    REFRESH_INTERVAL = 1
    COL_SIZE = 3
    while True:
        items, header = __getActive()
        # Get col sizes
        colsizes = [len(str(item)) for item in header]
        for row in items:
            for i, col in enumerate(row):
                if len(str(col)) > colsizes[i]:
                    colsizes[i] = len(str(col))
        # Clear the screen
        stdscr.clear()
        
        # Print the header
        header_str = " | ".join([f"{item:<{colsizes[i]}}" for i, item in enumerate(header)])
        stdscr.addstr(0, 0, header_str)

        # Print the rows
        for i, row in enumerate(items):
            row_str = " | ".join([f"{item:<{colsizes[i]}}" for i, item in enumerate(row)])
            stdscr.addstr(i+1, 0, row_str)

        # Refresh the screen
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            break
        sleep(REFRESH_INTERVAL)

def restartAria():
    cmd = f"systemctl --user restart aria2d.service"
    subprocess.run(cmd, shell=True)

def editConfig():
    cmd = f"NVIM_APPNAME=nvim-nvchad nvim ~/.config/aria2/aria2.conf"
    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def addUrisFull(url="http://localhost", port=6800, token=None):
    s = "!!\n"
    s +=  "# URI,out\n\n"

    ## Create tmpfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
    # process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls = []
    argstrs = []
    for line in lines:
        if line[0] == "!" and line.count("!") == 2:
            argstrs.append(line)
        elif line[0] in ["#", "!"] or line.strip() == "":
            pass
        else:
            sp = line.find(",")
            if sp == -1:
                # os.system(f"notify-send '{len(dls)} downloads added'")
                dls.append({"uri": line.strip()})
            else:
                dls.append({"uri": line[:sp].strip(), "filename": line[sp+1:].strip()})

    for dl in dls:
        add_download(**dl, url=url, port=port, token=token)
        # jsonreq = pyperclip.copy(addUri(**dl))
        # send_req(jsonreq)

    os.system(f"notify-send '{len(dls)} downloads added'")

def addTorrentsFull(url="http://localhost", port=6800, token=None):
    s = "!!\n"
    s +=  "# path\n\n"

    ## Create tmpfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    cmd = f"nvim -i NONE -c 'norm G' {tmpfile_path}"
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()

    dls = []
    uris = []
    argstrs = []
    for line in lines:
        if line[0] == "!" and line.count("!") == 2:
            argstrs.append(line)
        elif line[0] in ["#", "!"] or line.strip() == "":
            pass
        elif len(line) > len("magnet:") and line[:len("magnet:")] == "magnet:":
            uris.append({"uri": line.strip()})
        else:
            dls.append({"path": line.strip()})
            # sp = line.find(",")
            # if sp == -1:
            #     # os.system(f"notify-send '{len(dls)} downloads added'")
            #     dls.append({"path": line.strip()})
            # else:
            #     dls.append({"path": line[:sp].strip(), "filename": line[sp+1:].strip()})

    for dl in dls:
        # with open(dl["path"], "rb") as f:
        #     torrent_data = f.read()
        jsonreq = addTorrent(dl["path"])

        # jsonreq = pyperclip.copy(addUri(**dl))
        send_req(jsonreq)

    for uri in uris:
        add_download(**uri, url=url, port=port, token=token)

    os.system(f"notify-send '{len(dls)} torrent files added'")
    os.system(f"notify-send '{len(uris)} magnet links added'")

def getAllInfo(gid):
    responses = []
    for op in [getFiles, getServers, getPeers, getUris, getOption, tellStatus]:
        try:
            response = send_req(op(gid))
            info = { "function" : op.__name__ }
            response = {**info, **response}
            responses.append(response)
        except:
            responses.append(json.loads(f'{{"function": "{op.__name__}", "response": "NONE"}}'))
    return responses
    file_info = send_req(getFiles(gid))
    server_info = send_req(getServers(gid)) 

    vals = [file_info]
    return file_info
    return [val if val else json.loads("{}") for val in vals]

def __getAll():
    active, aheader = __getActive()
    stopped, sheader = __getStopped()
    waiting, wheader = __getQueue()

    # active = [["NA"] + row for row in active]
    # stopped = [["NA"] + row for row in stopped]
    return active + waiting + stopped, wheader

def openDownloadLocation(gid):
    """

    """
    try:
        req = getFiles(str(gid))
        response = send_req(req)
        val = json.loads(json.dumps(response))
        files = val["result"]
        if len(files) == 0: return None
        loc = files[0]["path"]
        if "/" not in loc:
            req = getOption(str(gid))
            response = send_req(req)
            val = json.loads(json.dumps(response))
            loc = val["dir"]

        # val = json.loads(response.encode('utf-8'))
        cmd = f"kitty yazi '{loc}'"
        # subprocess.run(cmd, shell=True)
        subprocess.Popen(cmd, shell=True)
        os.system(f"notify-send '{type(val)}'")
        os.system(f"notify-send '{loc}'")
        # os.system(f'kitty yazi "{loc}"')

    except:
        pass


def begin(config):
    active_loop = lambda x: x
    waiting_loop = lambda x: x
    stopped_loop = lambda x: x
    options = [
            [
                "View All", 
                {
                    "function": active_loop,
                    "get_data": __getAll,
                    "operations": [
                        ["pause", pause],
                        ["unpause", unpause],
                        ["changePosition", changePosition],
                        ["sendToFrontOfQueue", changePosition, {"pos":0} ],
                        ["sendToBackOfQueue", changePosition, {"pos":10000} ],
                        ["remove", remove],
                        ["retryDownload", retryDownload, {}],
                        ["forceRemove", forceRemove],
                        ["getFiles", getFiles, {}, {"view":True}],
                        ["getServers", getServers, {}, {"view":True}],
                        ["getPeers", getPeers, {}, {"view":True}],
                        ["getUris", getUris, {}, {"view":True}],
                        ["tellStatus", tellStatus, {}, {"view":True}],
                        ["getOption", getOption, {}, {"view":True}],
                        ["getAllInfo", getAllInfo, {}, {"view":True}],
                        # ["changeOption", changeOption, {}, {"view":True}],
                        ["openDownloadLocation", openDownloadLocation, {}, {}],
                    ],
                }
            ],
            # [
            #     "View Active", 
            #     {
            #         "function": active_loop,
            #         "get_data": __getActive,
            #         "operations": [
            #             ["pause", pause],
            #             ["changePosition", changePosition],
            #             ["sendToFrontOfQueue", changePosition, {"pos":0} ],
            #             ["sendToBackOfQueue", changePosition, {"pos":10000} ],
            #             ["remove", remove],
            #             ["forceRemove", forceRemove],
            #             ["getFiles", getFiles, {}, {"view":True}],
            #             ["getServers", getServers, {}, {"view":True}],
            #             ["getPeers", getPeers, {}, {"view":True}],
            #             ["getUris", getUris, {}, {"view":True}],
            #             ["tellStatus", tellStatus, {}, {"view":True}],
            #             ["getOption", getOption, {}, {"view":True}],
            #             ["getAllInfo", getAllInfo, {}, {"view":True}],
            #             # ["changeOption", changeOption, {}, {"view":True}],
            #         ],
            #     }
            # ],
            # [
            #     "View Waiting", 
            #     {
            #         "function": waiting_loop,
            #         "get_data": __getQueue,
            #         "operations": [
            #             ["pause", pause],
            #             ["unpause", unpause],
            #             ["changePosition", changePosition],
            #             ["sendToFrontOfQueue", changePosition, {"pos":0} ],
            #             ["sendToBackOfQueue", changePosition, {"pos":10000} ],
            #             ["remove", remove],
            #             ["forceRemove", forceRemove],
            #             ["getFiles", getFiles, {}, {"view":True}],
            #             ["getServers", getServers, {}, {"view":True}],
            #             ["getPeers", getPeers, {}, {"view":True}],
            #             ["getUris", getUris, {}, {"view":True}],
            #             ["tellStatus", tellStatus, {}, {"view":True}],
            #             ["getOption", getOption, {}, {"view":True}],
            #             ["getAllInfo", getAllInfo, {}, {"view":True}],
            #             # ["changeOption", changeOption, {}, {"view":True}],
            #         ]
            #     }
            # ],
            # [
            #     "View Stopped", 
            #     {
            #         "function": stopped_loop,
            #         "get_data": __getStopped,
            #         "operations": [
            #             ["unpause", unpause, {}],
            #             ["remove", removeStopped],
            #             ["forceRemove", removeStopped],
            #             ["retryDownload", retryDownload, {}],
            #             ["getFiles", getFiles, {}, {"view":True}],
            #             ["getServers", getServers, {}, {"view":True}],
            #             ["getPeers", getPeers, {}, {"view":True}],
            #             ["getUris", getUris, {}, {"view":True}],
            #             ["tellStatus", tellStatus, {}, {"view":True}],
            #             ["getOption", getOption, {}, {"view":True}],
            #             ["getAllInfo", getAllInfo, {}, {"view":True}],
            #             # ["changeOption", changeOption, {}, {"view":True}],
            #         ]
            #     },
            # ],
            # [
            #     "Watch Active",
            #     {
            #         "get_data": __getActive,
            #         "args": (),
            #         "kwargs": {},
            #         "refresh": True,
            #     },
            # ],
            [
                "Watch All",
                {
                    "get_data": __getAll,
                    "args": (),
                    "kwargs": {},
                    "refresh": True,
                    "operations": [
                        ["pause", pause],
                        ["unpause", unpause],
                        ["changePosition", changePosition],
                        ["sendToFrontOfQueue", changePosition, {"pos":0} ],
                        ["sendToBackOfQueue", changePosition, {"pos":10000} ],
                        ["remove", remove],
                        ["retryDownload", retryDownload, {}],
                        ["forceRemove", forceRemove],
                        ["getFiles", getFiles, {}, {"view":True}],
                        ["getServers", getServers, {}, {"view":True}],
                        ["getPeers", getPeers, {}, {"view":True}],
                        ["getUris", getUris, {}, {"view":True}],
                        ["tellStatus", tellStatus, {}, {"view":True}],
                        ["getOption", getOption, {}, {"view":True}],
                        ["getAllInfo", getAllInfo, {}, {"view":True}],
                        # ["changeOption", changeOption, {}, {"view":True}],
                        ["openDownloadLocation", openDownloadLocation, {}, {}],
                    ],
                },
            ],
            # [
            #     "Watch Active (non-interactive)",
            #     {
            #         "get_data": __getActive,
            #         "args": (),
            #         "kwargs": {},
            #         "refresh": True,
            #     },
            # ],
            [
                "AddURIs",
                {
                    "function": addUris,
                },
            ],
            [
                "Add Torrents",
                {
                    "function": addTorrents,
                },
            ],
            [
                "pauseAll",
                {
                    "function": pauseAll,
                }
            ],
            [
                "Remove completed/errored downloads",
                {
                    "function": removeCompleted,
                },
            ],
            [
                "Get Global Options",
                {
                    "function": getGlobalOption,
                }

            ],
            [
                "Get Global Stat",
                {
                    "function": getGlobalStat,
                }
            ],
            [
                "Get Session Info",
                {
                    "function": getSessionInfo,
                }
            ],
            [
                "Get Version",
                {
                    "function": getVersion,
                }
            ],
            [
                "Edit Config",
                {
                    "function": editConfig,
                }
            ],
            [
                "Restart Aria",
                {
                    "function": restartAria,
                }

            ],
        ]
    highlights = [
        {
            "match": "complete",
            "field": 1,
            "color": 8,
        },
        {
            "match": "error",
            "field": 1,
            "color": 7,
        },
        {
            "match": "active",
            "field": 1,
            "color": 9,
        },
        {
            "match": "waiting",
            "field": 1,
            "color": 11,
        },
        {
            "match": "paused",
            "field": 1,
            "color": 12,
        },
        { ## 0-20
            "match": r'^(0\d?(\.\d*)?\b|\b\d(\.\d*)?)\b%?',
            "field": 6,
            "color": 7,
        },
        {
            "match": r'^(2\d(\.\d*)?|3\d(\.\d*)?|40(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 20 to 40
            "field": 6,
            "color": 11,
        },
        {
            "match": r'^(4\d(\.\d*)?|5\d(\.\d*)?|60(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 40 to 60
            "field": 6,
            "color": 9,
        },
        {
            "match": r'^(6\d(\.\d*)?|7\d(\.\d*)?|80(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 60 to 80
            "field": 6,
            "color": 9,
        },
        {
            "match": r'^(8\d(\.\d*)?|9\d(\.\d*)?|100(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 80 to 100
            "field": 6,
            "color": 8,
        },
    ]
    menu_highlights = [
        {
            "match": "complete",
            "field": 0,
            "color": 8,
        },
        {
            "match": "error",
            "field": 0,
            "color": 7,
        },
        {
            "match": "active",
            "field": 0,
            "color": 9,
        },
        {
            "match": "waiting",
            "field": 0,
            "color": 11,
        },
    ]
    modes = [
        {
            'filter': '',
            'sort': 0,
            'name': 'All',
        },
        {
            'filter': '--1 active',
            'name': 'Active',
        },
        {
            'filter': '--1 waiting',
            'name': 'Queue',
        },
        {
            'filter': '--1 paused',
            'name': 'Paused',
        },
        {
            'filter': '--1 complete',
            'name': 'Completed',
        },
        {
            'filter': '--1 error',
            'name': 'Error',
        },
    ]

    app_name = "Aria2TUI"
    menu_persistent = False
    dl_type_list = [3]
    cursor_pos = 0
    cursor_pos_levels = [(0,0) for i in range(4)]
    function_data = {
        "current_row":  cursor_pos_levels[1][0],
        "current_page": cursor_pos_levels[1][1],
        "highlights": highlights,
        "paginate": paginate,
        "title": app_name,
        "colors": custom_colors,

    }
    menu_data = {
        "top_gap": 0,
        "current_row":  cursor_pos_levels[1][0],
        "current_page": cursor_pos_levels[1][1],
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colors": custom_colors,

    }
    view_loop_data = {
        "top_gap": 0,
        "current_row":  cursor_pos_levels[1][0],
        "current_page": cursor_pos_levels[1][1],
        "highlights": highlights,
        "paginate": paginate,
        "modes": modes,
        "title": app_name,
        "colors": custom_colors,
        "display_modes": True,

    }
    watch_loop_data = {
        "top_gap": 0,
        "current_row":  cursor_pos_levels[1][0],
        "current_page": cursor_pos_levels[1][1],
        "highlights": highlights,
        "paginate": paginate,
        "modes": modes,
        "title": app_name,
        "colors": custom_colors,
        "display_modes": True,

    }
    dl_option_data = {
        "top_gap": 0,
        "current_row":  cursor_pos_levels[1][0],
        "current_page": cursor_pos_levels[1][1],
        "highlights": menu_highlights,
        "paginate": paginate,
        "title": app_name,
        "colors": custom_colors,
        "require_option": [False if x[0] != "changePosition" else True for x in options[0][1]["operations"]],
    }
    while True:
        ## Select menu option
        if not menu_persistent:
            menu_data = {key: val for key, val in menu_data.items() if key not in ["items", "indexed_items"]}
            dl_type_list, opts, menu_data = list_picker(
                stdscr,
                items=[[func[0]] for func in options],
                # current_row=cursor_pos_levels[0][0],
                # current_page=cursor_pos_levels[0][1],
                # colors=custom_colors,
                max_selected=1,
                **menu_data,
            )
            cursor_pos_levels[0] = (function_data["current_row"], function_data["current_page"])
        if not dl_type_list: break
        dl_type = dl_type_list[0]


        if options[dl_type][0] == "Watch Active (non-interactive)":
            curses.wrapper(watch_active)
            continue
        elif options[dl_type][0] in ["Watch Active", "Watch All"]:
            # os.system("notify-send 'refreshing'")
            menu_persistent = True
            items, header = options[dl_type][1]["get_data"]()
            # if len(items) == 0:
            #     header = ["items"]
            #     items = [[]]

            ## Ensure that the cursor stays on the same download (as ID'd by the gid)
            if "indexed_items" in watch_loop_data and len(watch_loop_data["indexed_items"]) != 0 and "cursor_pos" in watch_loop_data:
                curs = watch_loop_data["cursor_pos"]
                indexed_items = watch_loop_data["indexed_items"]
                gid_col = header.index("gid")
                current_index_gid = indexed_items[curs][1][gid_col]
                if current_index_gid in [item[gid_col] for item in items]:
                    new_index = [item[gid_col] for item in items].index(current_index_gid)
                    watch_loop_data["cursor_pos"] = new_index

            ## Remove old data from dict
            watch_loop_data = {key: val for key, val in watch_loop_data.items() if key not in ["items", "indexed_items"]}
            selected_downloads, opts, watch_loop_data = list_picker(
                stdscr,
                items,
                # current_row=cursor_pos_levels[1][0],
                # current_page=cursor_pos_levels[1][1],
                header=header,
                timer=3,
                get_new_data=True,
                refresh_function=options[dl_type][1]["get_data"],
                # highlights=highlights,
                **watch_loop_data,
            )

            cursor_pos_levels[1] = (watch_loop_data["current_row"], watch_loop_data["current_page"])
            # selected_downloads, opts = list_picker(stdscr, items, custom_colors, header=header, timer=2, get_new_data=True, refresh_function=options[dl_type][1]["get_data"])
            # terminate_code = run_with_timeout(list_picker, args, kwargs, timeout=2)
            if not selected_downloads and opts == 'refresh':
                continue
            elif not selected_downloads:
                menu_persistent = False
                continue

        elif options[dl_type][0] in ["AddURIs", "Edit Config", "Restart Aria", "Add Torrents"]:
            # Run function
            options[dl_type][1]["function"]()
            continue
        # elif options[dl_type][0] == "Edit Config":
        #     # process = subprocess.Popen(usrtxt, shell=True, stdin=subprocess.PIPE)
        #     # process.communicate(input='\n'.join(full_values).encode('utf-8'))
        #     # cmd = f"kitty --class=reader-class nvim -i NONE {tmpfile_path}"
        #     # cmd = f"nvim ~/.config/aria2/aria2.conf"
        #     cmd = f"NVIM_APPNAME=nvim-nvchad nvim ~/.config/aria2/aria2.conf"
        #     subprocess.run(cmd, shell=True)
        #     continue
        # elif options[dl_type][0] == "Restart Aria":
        #     cmd = f"systemctl --user restart aria2d.service"
        #     subprocess.run(cmd, shell=True)
        #     continue
        ## Global
        elif options[dl_type][0] in ["Get Global Options", "Get Global Stat", "Get Session Info", "Get Version"]:
            data = send_req(options[dl_type][1]["function"]())
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                tmpfile.write(json.dumps(data, indent=4))
                # tmpfile.write(data)
                tmpfile_path = tmpfile.name
            # cmd = f"kitty --class=reader-class nvim -i NONE {tmpfile_path}"
            cmd = f"nvim -i NONE {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
            continue

        elif options[dl_type][0] in ["pauseAll", "Remove completed/errored downloads"]:
            data = send_req(options[dl_type][1]["function"]())
            continue


        else:
            cursor_pos_levels[2] = (0,0)
            ## select downloads to operate upon
            items, header = options[dl_type][1]["get_data"]()
            if len(items) == 0:
                header = ["items"]
                items = [[]]
            ## Ensure that the cursor stays on the same download (as ID'd by the gid)
            if "indexed_items" in view_loop_data and len(view_loop_data["indexed_items"]) != 0 and "cursor_pos" in watch_loop_data:
                curs = view_loop_data["cursor_pos"]
                indexed_items = view_loop_data["indexed_items"]
                gid_col = header.index("gid")
                current_index_gid = indexed_items[curs][1][gid_col]
                if current_index_gid in [item[gid_col] for item in items]:
                    new_index = [item[gid_col] for item in items].index(current_index_gid)
                    view_loop_data["cursor_pos"] = new_index
            view_loop_data = {key: val for key, val in view_loop_data.items() if key not in ["items", "indexed_items"]}
            selected_downloads, opts, view_loop_data = list_picker(
                stdscr,
                items,
                # current_row=cursor_pos_levels[2][0],
                # current_page=cursor_pos_levels[2][1],
                # colors=custom_colors,
                header=header,
                # highlights=highlights,
                **view_loop_data,

            )
            cursor_pos_levels[2] = (function_data["current_row"], function_data["current_page"])
            if not selected_downloads or items == [[]]: continue
        # os.system(f"notify-send {repr(selected_downloads)}")
        gid_index = header.index("gid")
        gids = [item[gid_index] for i, item in enumerate(items) if i in selected_downloads]
        
        ## select action to perform on downloads
        operations = [operation_list[0] for operation_list in options[dl_type][1]["operations"]]
        items, header = operations, [f"Operation to perform on {selected_downloads}"]
        dl_option_data = {key: val for key, val in dl_option_data.items() if key not in ["items", "indexed_items"]}
        operation_n, opts, dl_option_data = list_picker(
            stdscr,
            items,
            # colors=custom_colors,
            header=header,
            **dl_option_data,
        )
        cursor_pos_levels[3] = (function_data["current_row"], function_data["current_page"])
        if not operation_n: 
            continue
        operation = operation_n[0]
        operation_f = options[dl_type][1]["operations"][operation][1]
        operation_list = options[dl_type][1]["operations"][operation]
        operation_function = operation_list[1]
        if len(operation_list) > 2:
            operation_kwargs = operation_list[2]

        # print(f"We want to {operations[operation]}")
        # print(f"    on {gids}")
        # print(f"    from list {dl_type_list}")

        responses = []
        batch = []
        for gid in gids:
            try:
                # jsonreq = changePosition(gid,0)
                if operations[operation] == "changePosition":
                    position = int(opts) if opts.strip().isdigit() else 0
                    jsonreq = operation_f(str(gid), position)
                elif operations[operation] == "getAllInfo":
                    js_rs = getAllInfo(str(gid))
                    responses.append(js_rs)
                    continue

                elif len(operation_list) > 2:
                    jsonreq = operation_f(str(gid), **operation_kwargs)
                else:
                    jsonreq = operation_f(str(gid))
            
                js_rs = send_req(jsonreq)
                responses.append(js_rs)
            except:
                responses.append({})
                pass
        if len(operation_list) > 2 and "view" in operation_list[-1].keys() and operation_list[-1]:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
                # tmpfile.write(json.dumps(data, indent=4))
                for i, response in enumerate(responses):
                    tmpfile.write(f'{"*"*50}\n{str(i)+": "+gids[i]:^50}\n{"*"*50}\n')
                    tmpfile.write(json.dumps(response, indent=4))
                # tmpfile.write(operation_f(str(gids[0])))
                # tmpfile.writelines([json.dumps(response, indent=4) for response in responses])
                # tmpfile.write(data)
                tmpfile_path = tmpfile.name
            # cmd = f"kitty --class=reader-class nvim -i NONE {tmpfile_path}"
            # cmd = r"nvim -i NONE -c '/^\s*\d'" + f" {tmpfile_path}"
            cmd = r"nvim -i NONE -c '/^\s*\"function\"'" + f" {tmpfile_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
            



def format_size(size_bytes):
    if size_bytes == 0:
        return "0.0 MB"
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_mb / 1024
    if size_gb >= 1:
        return f"{size_gb:.1f} GB"
    return f"{size_mb:.1f} MB"


def main():
    while True:
        connection_up = test_connection()
        if connection_up: break
        header, choices = ["Aria2c Connection down."], ["Yes", "No"]
        choice, opts, function_data = list_picker(
            stdscr,
            choices,
            colors=custom_colors,
            header=header,
            max_selected=1
        )

        if choice == [1] or choice == []: exit()

        subprocess.Popen(f"systemctl --user restart aria2d.service", shell=True, stderr=subprocess.PIPE)
        subprocess.Popen(f"systemctl --user restart ariang.service", shell=True, stderr=subprocess.PIPE)
        time.sleep(2)

    begin(config)




if __name__ == "__main__":
    ## Run curses
    global send_req, jsonmodelreq, token
    os.environ.setdefault('ESCDELAY', '25')
    try:
        stdscr = curses.initscr()
        stdscr.keypad(True)
        curses.start_color()
        curses.noecho()  # Turn off automatic echoing of keys to the screen
        curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)

        # Check if config exists. If not then load default
        CONFIGPATH = "~/scripts/utils/aria2tui/aria2tui.toml"
        with open(os.path.expanduser(CONFIGPATH), "rb") as f:
            config = tomllib.load(f)

        url = config["general"]["url"]
        port = config["general"]["port"]
        token = config["general"]["token"]
        paginate = config["general"]["paginate"]

        send_req = lambda req: sendReqFull(req, url=url, port=port)
        addUri = lambda uri, out="", dir=None, queue_pos=10000:  addUriFull(uri, out=out, dir=dir, queue_pos=queue_pos, token=token)
        addTorrent = lambda path, out="", dir=None, queue_pos=10000:  addTorrentFull(path, out=out, dir=dir, queue_pos=queue_pos, token=token)
        getOption = lambda gid:  getOptionFull(gid, token=token)
        getServers = lambda gid:  getServersFull(gid, token=token)
        getPeers = lambda gid:  getPeersFull(gid, token=token)
        getUris = lambda gid:  getUrisFull(gid, token=token)
        getGlobalOption = lambda : getGlobalOptionFull(token=token)
        getSessionInfo = lambda : getSessionInfoFull(token=token)
        getVersion = lambda : getVersionFull(token=token)
        getGlobalStat = lambda : getGlobalStatFull(token=token)
        pause = lambda gid:  pauseFull(gid, token=token)
        retryDownload = lambda gid:  retryDownloadFull(gid, token=token)
        retryDownload2 = lambda gid:  retryDownload2Full(gid, token=token)
        pauseAll = lambda : pauseAllFull(token=token)
        unpause = lambda gid:  unpauseFull(gid, token=token)
        remove = lambda gid:  removeFull(gid, token=token)
        forceRemove = lambda gid:  forceRemoveFull(gid, token=token)
        removeStopped = lambda gid:  removeStoppedFull(gid, token=token)
        getFiles = lambda gid:  getFilesFull(gid, token=token)
        removeCompleted = lambda : removeCompletedFull(token=token)
        changePosition = lambda gid, pos, how="POS_SET":  changePositionFull(gid, pos, how=how, token=token)
        changeOption = lambda gid, key, val:  changeOptionFull(gid, key, val, token=token)
        tellActive = lambda offset=0, max=5000:  tellActiveFull(offset=0, max=max, token=token)
        tellWaiting = lambda offset=0, max=5000:  tellWaitingFull(offset=0, max=max, token=token)
        tellStopped = lambda offset=0, max=5000:  tellStoppedFull(offset=0, max=max, token=token)
        tellStatus = lambda gid:  tellStatusFull(gid, token=token)
        sendReq = lambda jsonreq, url="http://localhost", port=6800: sendReqFull(jsonreq, url=url, port=port)
        addTorrents = lambda url="http://localhost", port=6800, token=token: addTorrentsFull(url=url, port=port, token=token)
        addUris = lambda url="http://localhost", port=6800, token=token: addUrisFull(url=url, port=port, token=token)
        custom_colors = get_colours(config["appearance"]["theme"])
        
        ## start connection
        while True:
            connection_up = test_connection()
            if connection_up: break
            header, choices = ["Aria2c Connection down."], ["Yes", "No"]
            choice, opts, function_data = list_picker(
                stdscr,
                choices,
                colors=custom_colors,
                header=header,
                max_selected=1
            )

            if choice == [1] or choice == []: exit()
            for cmd in config["general"]["startupcmds"]:
                subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

            # subprocess.run(f"systemctl --user restart aria2d.service", shell=True)
            # subprocess.run(f"systemctl --user restart ariang.service", shell=True)
            time.sleep(2)

        begin(config=config)
        # Clean up
        stdscr.clear()
        stdscr.refresh()
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        os.system('cls' if os.name == 'nt' else 'clear')
    except:

        # Clean up
        stdscr.clear()
        stdscr.refresh()
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        os.system('cls' if os.name == 'nt' else 'clear')
        raise
