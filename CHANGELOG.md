# CHANGELOG.md

## [0.1.12.1] ?
- Created first-time startup form that generates default config if missing
- Added ability to edit aria2tui config through a form interface
- Updated form to store and return exit status
- Improved progress bar display
- Added "Change Global Options (Session)" (for aria2c) to main menu
- Fixed scrolling in form views with page up/down key support
- Redirected stderr messages at app launch to prevent TUI distortion
- Added new structured data viewer
  - Used to display download info
  - Used to display global info
- Fix bitstring to download pieces display in right pane.
- Added new forms in aria2tui
  - Add download form
  - Form to enter config details if first time starting aria2tui
  - Change download options form

## [0.1.12.0] 2026-01-04
 - Download operation menu options now auto-filter based on download selections.
  - So, e.g., "Modify torrent files" will not appear in the menu when direct downloads are selected.
 - Improvement: Retry Download now ensures that all aria2c download options from target download are preserved in new download.
 - Fix change filename menu option
 - Improve help descriptions and ordering
 - Disable modification checks for change options menu and also for change torrent filenames menu.
 - Disable listpick keys that should not work with aria2tui
    - Add col/row keys from aria2tui_keys
    - Remove left_pane keys (toggle and cycle)
    - Disable paste functionality
 - Add pytest skeleton and outline future tests

## [0.1.11.13-14] 2025-12-24
 - Fixed "Change Position in Queue" download operation
 - Added change filename download operation option
 - Reordered download operations

## [0.1.11.12] 2025-11-10
 - Streamlined download options menu
  - Reordered menu in a more intuitive way.
  - Created "DL Info" submenu--reducing the sie of the main options menu.
 - Fixed invalid escape strings warning in nvim commands.
 - Added macro ('O' key) to open file location of hovered download.

## [0.1.11.10-11] 2025-11-04
 - Updated listpick version fixing major bug OSX.
    - Fixed instacrashes due to tmpfile paths being too long when multiprocessing.manager was created.

## [0.1.11.9] 2025-10-26
 - Changed inherited from listpick:
   - Fixed problems when there are no downloads
     - Bug accessing settings when there are no downloads
     - Bug displaying footer when there are no downloads
 - Improved file-opening.
   - Groups files and attempts to open them in a single instance of the default application.
   - Now detects system type in use and attempts to use the appropriate opener
     - linux: xdg-open
     - macos: open
     - android: termux-open
 - File opening now works on MacOS without needing to set the appropriate opener in config.
 - Added macro ('o' key) to open files from the main menu.

## [0.1.11.8] 2025-10-14
 - Updated listpick version requirement. 

## [0.1.11.7] 2025-10-14
 - Ensured that the terminal settings are reset after opening yazi or neovim.
 - Improved graph size function for full-screen graphs.
 - Ensured that multiple cells can be edited in neovim by pressing "E" in a Picker with editable columns--e.g., when changing options or modifying torrent files.
 - Ensured that when editing options in nvim the commentstring is set to #\ %s

## [0.1.11.6] 2025-10-03
 - Added a timeout when testing the connection to the aria daemon to ensure that if aria2c crashes (but is still running) the pplication does not simply hang.
 - Improved the Operation class so that it accounts for all of the relevant menu options without requiring special cases in the logic of the applyToDownloads() function.
 - Cleaned up the applyToDownloads() function
 - Improved documentation for a few key functions (applyToDownloads, main app loop)
 - Enabled colours for up/download graphs in the full-screen graphs.
 - Made the full-screen graphs the same style as the pane graphs.

## [0.1.11.5] 2025-09-23
 - Improved data display for DL Info: Files.

## [0.1.11.4] 2025-09-22
 - Ensured that changing options using nvim uses the same key=value format as the input files. Previously a structured json was used.

## [0.1.11.3] 2025-09-21
 - Fixed display notifications when adding download tasks.
 - Ensured compatibility with listpick changes to pane size parameter.


## [0.1.11.1] 2025-09-17

 - Multifile torrents can now be managed a lot better.
   - Files can be skipped
   - Filenames can be edited
   - See the wiki

## [0.1.11.0] 2025-09-16
 - We can now select which files (from a torrent) that we want to download and which to skip.
 - File info pane now shows which files are being downloaded ([*]) and which are to be skipped ([ ]).
 - Updated size in columns to reflect only the total size of the target files--i.e., excluding skipped files.
 - Added colour to the speed and progress graphs--by converting ansi to a colours dict.
 - Graph ticks are now rounded for small units (B/s and KB/s).

## [0.1.10.16] 2025-09-15
 - Added unified "Add Download Tasks" menu option--URIs and torrents no longer have to be added separately.
 - Fixed "View Downloads" still auto-refreshing.
 - Added --add_download_bg flag which uses a gui popup if aria is not running.
 - Added placeholder footer string to ensure that the footer doesn't resize after loading the footer string.

## [0.1.10.11] 2025-09-12
 - --add_download flag added so that aria2tui can be used as the default magnet link opener.
 - Fixed graph ticks.


## [0.1.10.10] 2025-09-01
 - Fixed notification display after adding DLs.

## [0.1.10.9] 2025-09-01
 - Added file picker option when adding torrents.

## [0.1.10.8] 2025-08-31
 - Fixed bug in right pane of the download options picker.

## [0.1.10.6] 2025-08-31
 - Fixed bug which caused crash due to config key error.
 - Aria2TUI connection now uses a picker spash screen.
   - This fixes pink flash when colours dict changed to the other picker.
 - Improved DL info display.

## [0.1.10.5] 2025-08-29
 - Added to config options: default pane.

## [0.1.10.5] 2025-08-29
 - Added right panes: DL progress, DL Files, DL pieces.

## [0.1.10.0] 2025-08-27
- Feature added: display speed graph of selected download in right pane
- Display selected downloads in right pane when selecting an operation to perform.
  - This was previously done using an infobox but this caused flickering.

## [0.1.9.0] - [0.1.9.21] 2025-08-22
- Fixed error when adding torrent path with ~.
- Fixed crash when adding a non-existent torrent path.
- Fixed cursor displaying after dropping to nvim to add uris/torrents.
- Waiting downloads are now displayed before paused downloads on the "All" mode.
- Ensured compatibility with latest version(s) of listpick:
  - The sort_column is now separate from the select column so we set the selected column in the setOptions picker.
  - The colour theme has to be set for each picker; it does not stay constant after being defined in the first picker.
- Ensured that the display messages are consistent when adding URIs and/or torrents. Previously when URIs were addded it would return the list of GIDs; this has been replaced with a proper message showing how many were added.
- Split batch requests into clumps of 2000 downloads to prevent aria2c throwing an error.

## [0.1.9] 2025-08-08
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
