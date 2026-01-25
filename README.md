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

# Aria2TUI supports multiple simultaneous connections;
#   each can be specified as an element of the instances array.

[[instances]]
name = "Default"
url = "http://localhost"
port = 6800
token = "1234"

# Used for starting and restarting. Creating service files for each instance is recommended
startup_commands = ["aria2c"]
restart_commands = ["pkill aria2c && sleep 1 && aria2c"]
# startup_commands = ["systemctl --user start aria2d.service"]
# restart_commands = ["systemctl --user restart aria2d.service"]

# Used when the "Edit Config" option is chosen in the main menu
aria2_config_path = "~/.config/aria2/aria2.conf"

# [[instances]]
# name = "Home Server"
# url = ...
# port = ...

[general]
# File managers 
## terminal_file_manager will open in the same terminal as Aria2TUI in a blocking fashion;
## gui_file_manager will fork a new process and open a new application.
terminal_file_manager = "yazi"
gui_file_manager = "kitty yazi"


# Data refresh time (in seconds) for the global stats and for the download data.
global_stats_timer = 1
refresh_timer = 2

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
 - If you have problems starting aria2c, check that you have an aria2c config file at `~/.config/aria2/aria2.conf`

### Keybinds
 - Press `?` in aria2tui to see the help page which will list the available keybinds.
 - `Ctrl-l` will redraw the screen; useful if there are stray artifacts after dropping to the shell
 - Switch between open aria2tui instances with `{` and `}`
 - Toggle the right-pane with `'` and cycle between right-pane views with `"`.
### Cursor Tracking and Auto-Refrsh

#### Cursor Tracking Modes

By default, the cursor follows the selected download task. If you're viewing an active download that completes and moves to the bottom of the list, the cursor moves with it.

For scenarios where you want the cursor to stay at a fixed position (e.g., watching active downloads at the top), you can enable **pin cursor mode**:

- Press `` ` `` and type `pc` to toggle pin cursor mode
- Alternatively, press `~` to open settings and select the pin cursor option
- A pin symbol (📌) in the footer indicates which tracking mode is active

#### Auto-Refresh Control

When performing bulk operations on rapidly changing downloads (e.g., hundreds of images transitioning from active/waiting to completed), it's recommended to **disable auto-refresh** to maintain data integrity during selection. To toggle auto-refresh:
- Press `~` and toggle the auto-refresh option

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