# CHANGELOG.md

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
