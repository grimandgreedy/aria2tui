# aria2tui

Aria2TUI is a download management tool. It acts as a TUI client for the aria2c download utility, facilitating bulk downloading, torrenting, queue control, the fine-tuning of download options (e.g., piece length, user-agent, max speed, etc.), downloading via proxy, and much more. 

Aria2tui communicates with an aria2c daemon over RPC. The UI is provided by my TUI picker [listpick](https://github.com/grimandgreedy/listpick).

<!-- https://github.com/user-attachments/assets/07ab1f63-3a5e-42dd-bddb-56c948ecd620 -->

https://github.com/user-attachments/assets/7c77a13f-90c7-4e67-9946-7b7009c835ad


Note: Make sure that you have [aria2c installed and configured](https://github.com/grimandgreedy/aria2tui/wiki/aria2c-setup) with RPC enabled.

## Quickstart


Install aria2tui using pip:
```bash
python -m pip install aria2tui
```

When you run `aria2tui` for the first time it will bring up a config creation form with the defaults pre-set. This creates a config file in `~/.config/aria2tui/config.toml` when you click save. Just enter your `url`, `port`, and `token` into the form and you are good to go.

```bash
aria2tui
```

See the [wiki](https://github.com/grimandgreedy/aria2tui/wiki) for more information on how to use aria2tui and for more configuration options.

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
