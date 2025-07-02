#!/bin/python
# -*- coding: utf-8 -*-
"""
aria_adduri.py

Author: GrimAndGreedy
License: MIT
"""

import argparse
import json
import requests
import tempfile
import subprocess
import re

from typing import Callable, Optional, Tuple

def addDownloadFull(
        uri: str,
        # out:str = "",
        token: str = "",
        url: str = "http://localhost",
        port: int = 6800,
        queue_position: Optional[int] = 0,
        cookies_file: str = "",
        # dir: str = "",
        # on_download_start: str = "",
        # on_download_complete: str = "",
        # proxy: str = "",
        prompt: bool = False,
        download_options_dict={},

    ) -> Tuple[bool, str]:
    """
    Send download to aria2c server at $url:$port. 
    If prompt is true then we open a new kitty window with a neovim buffer to enter any uris.
    """

    url = f'{url}:{port}/jsonrpc'
   
    # if prompt:
    #     argdict, out, uri = kitty_prompt(out, uri)
    #     if type(uri) == type([]):
    #         uri = uri[0]

    # Add params to json request
    params = [f"token:{token}", [uri]] if token not in ["", None] else [[uri]]
    
    # Include optional parameters if provided
    # options = {}
    # if on_download_start:
    #     options['on-download-start'] = on_download_start
    # if on_download_complete:
    #     options['on-download-complete'] = on_download_complete
    if cookies_file:
        # Assuming cookies_file contains cookies in a format accepted by aria2
        with open(cookies_file, 'r') as file:
            download_options_dict['header'] = [f'Cookie: {line.strip()}' for line in file]

    # Add optional parameters to params
    if download_options_dict:
        params = params + [download_options_dict]

    # JSON-RPC request data
    request_data = {
        "jsonrpc": "2.0",
        "method": "aria2.addUri",
        "id": "some_unique_id",
        "params": params
    }

    # Send request
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(request_data))
    
    # Handle response
    response_json = response.json()
    if response_json.get("error"):
        # print(f"Error: {response_json['error']['message']}")
        return False, response_json['error']['message']
    else:
        # print(f"Success! Download ID: {response_json['result']}")
        return True, response_json['result']

def parse_string_to_list(s: str) -> list[int]:
    """ Turn a string containing a list of integers ("5,3,1,3,222") or a slice (e.g., "4:199") into a python list. """
    # Use regular expressions to find all lists and slices
    pattern = r'\[([^]]*)\]'
    matches = re.findall(pattern, s)
    
    result = []
    for match in matches:
        if ':' in match:
            # Handle slice notation
            start, end = map(int, match.split(':'))
            result.extend(range(start, end + 1))
        else:
            # Handle list notation
            elements = list(map(int, match.split(',')))
            result.extend(elements)
    
    return result

def argstring_to_argdict(argstring: str) -> dict:
    r"""
    desc: takes an argstring (see below for examples) as input and returns a dictionary for each arg.

    the argstring can be used to pass key-value pairs.

    argstring: r'\w([(\d+,)*(\d+)?]|(\d+:\d+))*'
    examples:
        s = "a[4,4];v[3:9][1];c"
        {
            a: [4, 4]
            v: [3, 4, 5, 6, 7, 8, 9, 1]
            c: []
        }
    """
    argdict = {}
    if len(argstring) == 0: return argdict
    args = argstring.split(";")
    for arg in args:
        c = arg[0]
        l = parse_string_to_list(arg[1:])

        # print(c + ": " + str(l))
        argdict[c] = l
    return argdict

def kitty_prompt(name: str, url: str) -> Tuple[dict, str, list[str]]:
    """ Open a nvim buffer and return the lines of the saved buffer. """
    s = f"!!\n{name}\n{url}"
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile.write(s)
        tmpfile_path = tmpfile.name
    
    # Open the temporary file in nvim within a new kitty window
    cmd = f"kitty --class=reader-class nvim -i NONE {tmpfile_path}"
    ps = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    with open(tmpfile_path, "r") as f:
        lines = f.readlines()
    # print(lines)

    argdict = {}
    argstring = lines[0].strip()
    if argstring.count("!") == 1: exit()
    if argstring[0] == "!":
        # We have, e.g., "!i[3,2];v[1][6:10]!johnsnow.mp4"
        # We extract '!argstring!' and get the range from lists and slices
        #   then remove the argstring to get the filename

        argstring = argstring[1:argstring[1:].find("!")+1]
        argdict = argstring_to_argdict(argstring)

        # Remove argstring from fname (e.g. !i! for no images)
        name = argstring[argstring[1:].find("!")+2:].strip()
        if len(name) == 0:
            lines.pop(0)
            name = lines[0].strip()
    else:
        name = lines[0].strip()


    return argdict, name, [line.strip() for line in lines[1:]]
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a download to a running aria2c server")
    parser.add_argument("uri", help="The URI of the file to download")
    parser.add_argument("-o", "--output", help="Optional filename for the downloaded file")
    parser.add_argument("-p", "--proxy", help="Optional filename for the downloaded file")
    parser.add_argument('--kitty-prompt', action='store_true', help='Confirm with kitty prompt.')
    parser.add_argument("-t", "--token", default="", help="Token for authentication")
    parser.add_argument("-q", "--queue", type=int, help="Optional queue position")
    parser.add_argument("-c", "--cookies", help="Optional cookies file")
    parser.add_argument("-d", "--directory", help="Optional directory to save the file")

    args = parser.parse_args()

    download_options_dict = {
        "out": args.output,
        "dir": args.directory,
    }
    addDownloadFull(
        uri=args.uri,
        # out=args.output,
        token=args.token,
        queue_position=args.queue,
        cookies_file=args.cookies,
        # dir=args.directory,
        proxy=args.proxy,
        prompt=args.kitty_prompt
    )

