# aria2tui

Aria2tui is a TUI download management tool. It acts as a front-end for the aria2c download utility, facilitating bulk downloading, torrenting, queue control, pausing and resuming downloads, fine-tuning download options (e.g., piece length, user-agent, max speed, etc.), downloading via proxy, and much more. 

Aria2tui communicates with the aria2c daemon over RPC. The UI is provided by my TUI picker [listpick](https://github.com/grimandgreedy/listpick).

https://github.com/user-attachments/assets/07ab1f63-3a5e-42dd-bddb-56c948ecd620

## Quickstart

Install aria2tui using pip and add the config.toml file from ./src/aria2tui/data/ to your config directory.

```
python -m pip install aria2tui &&
mkdir ~/.config/aria2tui/ &&
wget https://raw.githubusercontent.com/grimandgreedy/aria2tui/refs/heads/master/src/aria2tui/data/config.toml -O ~/.config/aria2tui/config.toml
```

**Note**: If you have not used aria2c before then download [this file](https://gist.github.com/qzm/a54559726896d5e6bf21adf2363ad334) and put it in ~/.config/aria2/. I would recommend going through and configuring it but this one will get you up and running for now.

After editing ~/.config/aria2tui/config.toml and ensuring that your url, port, and secret token are correct, you are all set to go:

```
aria2tui
```

If you have multiple daemons you can specify another config file:

```
ARIA2TUI_CONFIG_PATH=/path/to/config/aria2c_torrents.toml aria2tui
ARIA2TUI_CONFIG_PATH=/path/to/config/aria_on_home_server_config.toml aria2tui
```

If you wish to use it regularly, then it may be useful to add aliases to your ~/.bashrc.
```
alias a2="python /path/to/aria2tui/aria2tui.py"
alias a2t="ARIA2TUI_CONFIG_PATH=/path/to/config/aria2c_torrents.toml aria2tui"
alias a2n="ARIA2TUI_CONFIG_PATH=/path/to/config/aria_on_home_server_config.toml aria2tui"
```

in addition to those requirements the application uses:
 - `nvim` for viewing/editing download options as well as adding URIs, magnet links and torrent files
 - `xdg-open` and `gio` for opening files.

## Other installation options

### Git repo

Clone rep
```bash
git clone https://github.com/grimandgreedy/Aria2TUI
```

Copy config and edit it accordingly:
```bash
mkdir ~/.config/aria2tui &&
cp Aria2TUI/src/aria2tui/data/config.toml ~/.config/aria2tui
```
Now you can start Aria2TUI:
```bash
cd ./Aria2TUI/src
python -m aria2tui.aria2tui_app
```

```bash
alias a2="cd /path/to/Aria2TUI/src && python -m aria2tui.aria2tui_app"
```

## Tips

 - Press '?' to see the help page which will list the available keys.
 - If you have problems starting aria2c, check that you have an aria2c config file at ~/.config/aria2/aria2.conf

## Features

 - Dynamic display of downloads
     - View active, queue, errored, stopped
 - Sort/filter/search using regular expressions
 - Add downloads with options
   - Simply dump a list of links;
     - or specify options:
       - proxy
       - User agent
       - ... Many more!
          - See [this section of the aria2c manual](https://aria2.github.io/manual/en/html/aria2c.html#input-file) for all available options all of which are supported
 - Add magnet links and torrent files
 - Operations on downloads:
   - Pause/unpause
   - Remove
   - Change position in queue
   - Open downloaded files
   - Open download location (with yazi)
   - Change download options by value of keys in nvim

     - Select download(s) you wish to change the value
     - Change save directory
     - Specify proxy, proxy user, and proxy password
     - Specify user-agent
     - Specify download piece length
     - ... Many more!
         - See [this section of the aria2c manual](https://aria2.github.io/manual/en/html/aria2c.html#input-file) for all available options all of which are supported.

<!-- <div align="center"> <img src="assets/change_options.gif" alt="change_options" width="70%"> </div> -->
<div align="center"> <img src="https://raw.githubusercontent.com/grimandgreedy/aria2tui/refs/heads/master/assets/change_options.gif" alt="change_options" width="70%"> </div>

   - View current options of download
   - Retry download
 - Interact with aria2 daemon
   - Edit config
   - Pause all
   - Restart aria
 - Global and particular download transfer speed *graphs*.

  <!-- <div align="center"> <img src="assets/transfer_speed_graph.png" alt="speed_graph" width="70%"> </div> -->
  <div align="center"> <img src="https://raw.githubusercontent.com/grimandgreedy/aria2tui/refs/heads/master/assets/transfer_speed_graph.png" alt="speed_graph" width="70%"> </div>

 - Visual options
   - Modify theme
     - '~' to view settings and then select theme

<!-- <div align="center"> <img src="assets/themes.png" alt="themes" width="70%"> </div> -->
<div align="center"> <img src="https://github.com/grimandgreedy/aria2tui/blob/master/assets/themes.png?raw=true" alt="themes" width="70%"> </div>

   - Show/hide columns
     - Press Shift+Column_number to toggle or press '~' to view settings and find the column you wish to toggle.
   - Quick-toggle footer: press '_'


## Important

While I use Aria2TUI every day, it is still in development and there are many things that still need to be cleaned up.

Some things that should be mentioned:

 - Realistically, Aria2TUI will only work in a UNIX (linux, macos) environment. If you register your interest I might be able to look into what I would need to change to get it to work on windows.
 - If you are performing bulk operations and the downloads are changing state rapidly--e.g., hundreds of images are changing from active/waiting to completed--it is recommended to stop the auto-refresh and operate on a static list.
    - This can be done by either:
      - exiting to the main menu ('q') and going to "View Downloads"; or
      - Pressing ~ and toggling the auto-refresh in the default "Watch Downloads" viewer.
    - You know that auto-refresh is active because there is a refresh symbol in the top right.
 - Note: This was created for personal use and so some of the code is quite ugly and/or buggy and simply needs to be re-written.

## Similar Projects

- [Ariang](https://github.com/mayswind/AriaNg) A web client for aria2c.

## Support and Feedback

Feel free to request features. Please report any errors you encounter with appropriate context.
