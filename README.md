# Aria2TUI

Aria2TUI is a TUI frontend for the Aria2 download utility.

<div align="center">
  <video src="assets/demo.mp4" alt="aria2tui demo" width="70%">
</div>

## Quickstart

Aria2TUI fetches the download data from the aria2c daemon over RPC and displays it using list_picker. As both Aria2TUI and list_picker are in active development you will need to clone both repositories.

```
git clone https://github.com/grimandgreedy/aria2tui

cd aria2tui && python -m pip install -r requirements

cd ..

git clone https://github.com/grimandgreedy/list_picker

cd list_picker && python -m pip install -r requirements
```

Edit the config.toml in the aria2tui repo and make sure your url, port, and secret token are correct.

 - Note that starting/restarting the aria2 daemon is done using systemd. There is a sample service file that you can put in ~/.config/systemd/user/ if you want to utilise this functionality.

Navigate to the aria2tui repo and run aria2tui.py

```
python aria2tui.py
```

or if you have multiple daemons you can specify another config file:

```
ARIA2TUI_CONFIG_PATH=/path/to/config/aria_on_home_server_config.toml python aria2tui.py
```

in addition to those requirements the application uses:
 - `yazi` for opening download locations
 - `nvim` for viewing/editing download options as well as adding URIs, magnet links and torrent files
 - `xdg-open` and `gio` for opening files.

## Features

 - Dynamic display of downloads
     - View active, queue, errored, stopped
 - Sort/filter/search using regular expressions
 - Add downloads 
 - Add magnet links and torrent files
 - Operations on downloads:
   - Pause/unpause
   - Remove
   - Change position in queue
   - View current options of download
   - Change download options
     - Change save directory
     - Specify proxy, proxy user, and proxy password
     - Specify user-agent
     - Specify download piece length
     - ...
   - Retry download
   - Open download location (yazi)
   - Open downloaded file
 - Interact with aria2 daemon
   - Edit config
   - Pause all
   - Restart aria (uses aria2d.service file)
 - Global and particular download transfer speed *graphs*.


## Important

While I use Aria2TUI every day, it is still in development and there are many things that still need to be cleaned up.

Some things that should be mentioned:

 - Realistically Aria2TUI will currently only work in a UNIX (linux, macos) environment.
 - If you are performing bulk operations and the downloads are changing state rapidly--e.g., hundreds of images are changing from active/waiting to completed--it is recommended to stop the auto-refresh and operate on a static list.
    - This can be done by either:
      - exiting to the main menu ('q') and going to "View Downloads"; or
      - Pressing ~ and toggling the auto-refresh in the default "Watch Downloads" viewer.
 - Note: This was created for personal use and so some of the code is quite ugly and/or buggy and simply needs to be re-written.

## Support and Feedback

Feel free to request features. Please report any errors you encounter with appropriate context.
