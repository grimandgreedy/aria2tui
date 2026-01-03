# aria2tui

Aria2TUI is a download management tool. It acts as a TUI client for the aria2c download utility, facilitating bulk downloading, torrenting, queue control, the fine-tuning of download options (e.g., piece length, user-agent, max speed, etc.), downloading via proxy, and much more. 

Aria2tui communicates with an aria2c daemon over RPC. The UI is provided by my TUI picker [listpick](https://github.com/grimandgreedy/listpick).

<!-- https://github.com/user-attachments/assets/07ab1f63-3a5e-42dd-bddb-56c948ecd620 -->

https://github.com/user-attachments/assets/7c77a13f-90c7-4e67-9946-7b7009c835ad

## Quickstart

See the [wiki](https://github.com/grimandgreedy/aria2tui/wiki).

Install aria2tui using pip:
```bash
python -m pip install aria2tui
```

Create a `config.toml` file and place it in `~/.config/aria2tui/`. Here is the default config:

```toml
####################################################
##        Default config for Aria2TUI
##   Some common config options have been provided
##      and commented for your convenience
####################################################

[general]

port = 6800
token = "1234"
url = "http://localhost"

# Used for starting and restarting.
startup_commands = ["aria2c"]
restart_commands = ["pkill aria2c && sleep 1 && aria2c"]
# startup_commands = ["systemctl --user start aria2d.service"]
# restart_commands = ["systemctl --user restart aria2d.service", "notify-send 'Aria2c has been restarted.'"]

# Used when "Edit Config" option is chosen in the main menu
aria2_config_path = "~/.config/aria2/aria2.conf"

# File managers 
## terminal_file_manager will open in the same terminal as Aria2TUI in a blocking fashion;
## gui_file_manager will fork a new process and open a new application.
terminal_file_manager = "yazi"
gui_file_manager = "kitty yazi"


# Data refresh time (in seconds) for the global stats and for the download data.
global_stats_timer = 1
refresh_timer = 2

# Scrolls by default
paginate = false

[appearance]
theme = 3

# Whether the right pane (DL Info, DL graphs) should be displayed by default when opening aria2tui
show_right_pane_default = false

# Which pane should be displayed first when the sidebar is opened.
# [0=DL Files (info), 1=speed graph, 2=progress graph, 3=download pieces]
right_pane_default_index = 0
```

**Note**: If you have not used aria2c before then download [this file](https://gist.github.com/qzm/a54559726896d5e6bf21adf2363ad334) and put it in ~/.config/aria2/. In any case, since we are using RPC to communicate with aria2c, make sure that you have the following set in your config: `enable-rpc` `rpc-listen-all` `rpc-allow-origin-all`.

After creating ~/.config/aria2tui/config.toml and ensuring that your url, port, and secret token are correct, you are all set to go:

```bash
aria2tui
```


## Tips

 - See [the wiki](https://github.com/grimandgreedy/aria2tui/wiki), which covers basic usage.
 - Press '?' in aria2tui to see the help page which will list the available keybinds.
 - If you have problems starting aria2c, check that you have an aria2c config file at ~/.config/aria2/aria2.conf
 - `Ctrl-l` will redraw the screen; useful if there are stray artifacts after dropping to the shell
 - Toggle the right-pane with `'` and cycle between right-pane views with `"`.
 - By default the cursor in aria2tui will track the highlighted download task--that is, if you are hovering over an active download which finishes and moves to the bottom of the list, then the cursor will remain on that task. This is usually what you want. However, sometimes you want to stay at a particular place in the download list--perhaps you want to remain at the top and watch the currently active downloads. To do this you can activate 'pin cursor' mode which will pin the cursor to an index rather than to a particular row.
    - Press ` and type pc. This will toggle pin cursor mode.
    - You can also press ~ to open the settings and then select the pin cursor option.
      - Note: The pin symbol  will be shown in the footer to indicate the cursor tracking mode.
 - If you are performing bulk operations and the downloads are changing state rapidly--e.g., hundreds of images are changing from active/waiting to completed--it is recommended to **toggle the auto-refresh** option to ensure data integrity while selecting which downloads to operate upon.
    - This can be done by either:
      - exiting to the main menu ('q') and going to "View Downloads"; or
      - Pressing ~ and toggling auto-refresh.
    - Note: The refresh symbol  at the top right indicates that you are in auto-refresh mode.

## Important

 - Aria2TUI was made to work on UNIX systems.
 - Changing download options for a task that is in progress--whether active or paused--will most likely restart the download (!!).

## Aria2TUI makes use of...

 - `yazi` for selecting torrent files.
 - `nvim` for viewing/editing download options as well as adding URIs, magnet links and torrent files
 - `curses` for controlling the terminal display
 - [listpick](https://github.com/grimandgreedy/listpick) for the terminal user-interface
 - [plotille](https://github.com/tammoippen/plotille) for graphs
 - [pyperclip](https://github.com/asweigart/pyperclip) for clipboard access

## Similar Projects

- [Ariang](https://github.com/mayswind/AriaNg) A web client for aria2c

## Support and Feedback

Feel free to request features. Please report any errors you encounter with appropriate context.