# CHANGELOG.md

## [0.1.9] 2025-07-08
 - Added download type column.
 - Added uri column.
 - Added header when viewing 'DL Info...'
 - Buxfixes
   - Fixed display of torrent size so that it shows the total size of all files in the torrent.
   - Refresh timer remains the set value after exiting to the menu and returning to the watch downloads Picker.
   - Fixed crash when trying to edit options.
 - Highlight downloads with 'removed' status red.

## [0.1.8] 2025-07-04
 - Added asynchronous data refresh requests using threading--inherited from listpick==0.1.9.
 - Added left-right scrolling using h/l--inherited from listpick==0.1.8.
 - Scroll to home/end with H/L--inherited from listpick==0.1.8.

## [0.1.7] 2025-07-02
 - Added MIT license information.

## [0.1.6] 2025-06-28
 - Restructured project and added it to pypi so that it can be intalled with pip. 
 - Changed default toml location to ~/.config/aria2tui/config.toml

## [0.1.5] 2025-06-27
 - terminal_file_manager option added to config so that the terminal file manager can be modified.
 - gui_file_manager option added to config so that the file manager that is opened in a new window can be modified.
 - launch_command option added to config so that the default file-launcher command can be specified.
 - View data (global or download) options are now passed to a Picker object.
 - Fixed issue with opening location of files that have 0% progress.
 
## [0.1.4] 2025-06-27
 - Ensured that the refresh rate can be set from the config.
 - Change options now uses Picker rather than editing the json from nvim.

## [0.1.3] 2025-06-20
 - Made Aria2TUI class which is called to run the appliction.

## [0.1.2] 2025-06-19
 - *New Feature*: Monitor global and particular download/upload speeds on a graph.
 - Fixed flickering when infobox is shown


## [0.1.1] 2025-06-18
 - Added a global stats string to show the total upload/download speed and the number of active, waiting, and stopped downloads.

## [0.1.0] 2025-06-17
 - CHANGELOG started.
 - Made Aria2TUI compliant with the new class-based Picker.
