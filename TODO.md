# aria2tui

> [!IMPORTANT] Features
> - [x] allow options when adding uris; perhaps use the same structure as the aria2c input file
>    - [x] implemented in principle
>    - [x] Allow all possible options to be specified
> - [ ] Implement argstrings to modify group-add URIs.
> - [ ] improve menu navigation
>    - [x] when downloads are selected and we go back they should still be selected
> - [x] add global stats bar,
>   - [x] Total DL speed, # active, 
> - [ ] monitor log file
> - [ ] setup https connection
> - [ ] add source column, showing site from which it is being downloaded
> - [ ] Create passive notification
>   - [ ]  use infobox?
> - [ ] Add notifications to the following:
>    - adding downloads (# succeeeded or failed)
> - [ ] implement changeOption for downloads
> - [ ] add key to open download location using 'o'
> - [ ] (!!!) make operations upon downloads work only with certain download types:
>    - [x] make remove work with all
>    - [ ] queue operations only on those in the queue
>    - [ ] retry only on errored
> - [ ] add column to show download type (e.g., torrent)
> - [x] add support for multiple aria servers
>   - [x] Config file can be specified.
>   - [ ] Change on the fly
> - [ ] add more flags to filtering/searching
>    - [ ] invert
>    - [ ] case-sensitivity
> - [x] Implement change option functionality to allow download options to be changed
>   - [x] Allow batch options changing
>     - Change dir for batch of downloads
> - [ ] Integrate bulk downloaders
> - [x] Add watch download speed graph
>   - [ ] Integrate the graphs into the main list_picker so that they can be watched as a pane while list_picker runs.
> - [x] Make data requests asynchronous so that the data is still refreshed with a spotty connection.
>   - [x] Use threading.
>   - [ ] Will Asyncio improve performance at all? 
>     - [ ] Test with very large data set


> [!Important] Improvements
> - [ ] Redo colours
>   - completed: green
>   - active: blue
>   - paused: ??? gray?
> - [ ] (!!!) make operations on multiple downloads into a batch request to reduce token-validation delay
> - [x] examine parsing of toml (why are the arguments set outside of the main function?)
> - [ ] add to config
>    - [x] url
>    - [x] port
>    - [x] startupcmds
>    - [x] theme
>    - [x] paging vs scrolling
>    - [ ] highlights off
>    - [ ] color off
>     - Search highlights should show inverse of b/w
> - [ ] live setting changes
>    - [x] show/hide columns
>    - [x] centre in cols & centre in terminals
>    - [ ] theme
> - [?] Allow name to be specified with magnet link
>    - [?] I don't think this is possible to change in aria2c
> - [x] open files 
>    - [x] open files of the same type in one instance
> - [x] make remove work with errored download
>    - [x] remove all errored/completed downloads works
> - [ ] fix operation loop to ensure that specific if/else can be removed; e.g., changePosition
> - [ ] redo handle_visual_selection()
> - [ ] redo cursor_up, cursor_down
> - [ ] Filter and search use the same tokenize and apply_filter function. Put them in utils.
> - [ ] Add option to change options and readd download. 
>   - [ ] Note that changing options for errored downloads doesn't work
> - [ ] Add retry and puase option
> - [ ] Finish implementation of batch changeOptions (!!!)
>    - [ ] Fix changing out dir
> - [x] Restructure repo directory.
> - [ ] If the token is incorrect then we are asked if we want to start aria2c...
> - [ ] Add tooltips to certain menu options
> - [x] add an editariaconfig path to the config 
> - [x] Redo main app launcher file
>   - [x] Put the menu options data into a separate file
>     - [x] Make a class for the option with the name, function, args, etc.
>   - [x] Add an Aria2TUi class
> - [x] Add default file manager option in config; or make yazi optional
> - [ ] Ensure that add torrent returns the gids.
> - [ ] Fix the startup notification when downloads are added.
> - [ ] Add an editor command to the config so that the preferred editor can be changed.
> - [ ] Implement "undo" for edits
> - [ ] Add row-wise highlighting
>   - [ ] E.g., Edited rows highlighted red
> - [ ] pass Option object to applytodownloads rather than individual variables.
> - [ ] Add picker_view variable to Option object.
> - [ ] Add --dump-config flag
> - [ ] Unify remove download  operations (paused and errored)
>   - [ ] We will have to check the status of downloads and make sure we send the right operation over IPC. If they are:
>     - [ ] Errored: removeDownloadResult
>     - [ ] Completed: removeDownloadResult
>     - [ ] Paused: remove
>     - [ ] Active: pause and then remove

> [!error] Errors
> - [ ] fix adding uris with filename. Data is the same but it is corrupted somehow. This is a problem with aria itself. **
> ```
> works vs doesn't work:
>   https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg
>   https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLBVWNXUrlGnx3VtnPULUE6v0EteQg
>```
> - [ ] When downloads are updating quickly and I try to operate upon them it sometimes says that the indices are not in the list...
> - [ ] Add an "Are you sure you want to exit?" option.


> [!Bug] Bugs
> - [ ] Fix order upon refresh
>   - [ ] when the item order refreshes (e.g. new downloads added) the selected items change. need to associate the selected items with gids and then create new selected items which will be passed back
> - [ ] (!!!) Fix cursor position upon refresh
>   - [ ] takes us back to the top when it refreshes in a different mode (I think due to filter)
>   - [ ] add pin_cursor option to pqrevent the cursor from going down when refreshing
>   - [ ] might have to do with filtering; 
>   - [ ] when original sort order there is no jumping
>   - [ ] lots of jumping when sorting by size
> - [ ] Filter/search problems
>   - [ ] ^[^\s] matches all rows in help but only highlights the first col
>     - [ ] seems to match the expression in any col but then only show highlights based on the row_str so misses matches in the second col
>  - [ ] restrict refresh so that it doesn't exit on the menu
>  - [x] infobox causes flickering
>   - [x] Caused by stdscr.clear() which we called when creating the new Picker(). We need to use stdscr.erase().
> - [ ] Overspill of selected header column by one character
> - [ ] Prevent input field from overwriting footer values.
>   - [x] Fixed after input has finished.
> - [x] Fix display of size for torrent with multiple files
>    - [x] Torrent size shows size of first file in torrent if there are multiple files...
> - [x] Exiting from change options still changes options
>   - [x] Check if selected_indices is empty first.
> - [ ] Slow navigation when we have a search query and many downloads with 1 second refresh rate




> [!Tip] Done
> - [x] If a download is paused and it is paused again it throws an error when it should just skip it.
> - [x] implement addTorrent
> - [x] Return a list of files and % completed for each file in a torrent.
> - [x] check if remove completed/errored is working
> - [x] show all downloads (not just 500)
>   - set max=5000 which should be fine
>   - had to set the max in the aria config file as well
> - [x] Add a getAllInfo option for downloads
> - [x] open location
> - [x] figure out how to keep the row constant when going back and forth between menus
> - [x] make fetching active, queue, and stopped downloads into a batch request
> - [x] (!!!) high CPU usage
>   - when val in `stdscr.timeout(val)` is low the cpu usage is high
> - [x] colour problems:
>   - aria2tui > view downloads > 'q' > 'z' 
>   - [x] fixed by arbitarily setting 0-50 for application colours, 50-100 for help colours and 100-150 for notification colours
> - [x] have to open watch active twice; first time exits immediately...
> - [x] add preview of selected downloads when selecting options
>   - [x] implemented infobox
> - [x] artifacts after opening download location in terminal; have to refresh before and after?
>   - [x] stdscr.clear() after yazi closes
> - [x] add a lambda function for add_download so that url and port don't have to be specifed
> - [x] some sudden exits from the watch all menu
>   - [x] caused by get_new_data not being in the function data
> - [x] add empty values for inapplicable cols
> - [x] get all function
> - [x] fix not resizing properly
> - [x] watch active only refreshes upon a keypress
> - [x] (!!!) add retry download function by getting download data, remove it and readd it
> - [x] info is wrong for torrents. The size, % completed, etc. Might need to rework the the data scraped from the json response.
> - [x] after nvim is opened (e.g., show all dl info) the display needs to be redrawn
> - [x] (!!!) there is a problem with the path when readding downloads sometimes. It is correct in the download info but is displayed wrong???
>   - [x] was caused by discordant order of getting download options and the main download information
> - [x] fix dir; it should be obtained from getInfo; 
> - [x] Add a view all tasks option
> - [x] When I change a download to position 4, the user_option 4 will remain in the options going forward
>   - [x] reset user_opts after option select
> - [x] fix filenames; also check torrents
> - [x] add highlights for % complete
> - [x] make percentage bar look nicer
> - [x] add url to test_connection
> - [x] add default sort method for columns
> - [x] remove old watch loop; pass refresh function to watch, no refresh function to view
> - [x] remove completed not working
> - [x] Add hidden columns to function so that they remain hidden on refresh
> - [x] Add color to highlight errored and completed tasks
> - [x] implement proper retrydownload function 
> - [x] create watch all
> - [x] make fetching active, queue, and stopped downloads into a batch request (all)


>- [!IMPORTANT] Done
>- [x] Make escape work with : (as it does with | and f)
>- [x] make filter work with regular expressions
>- [x] adjust page after resize
> - [x] fix not resizing properly
> - [x] fix header columns not being aligned (fixed by replacing tabs with spaces so char count clipped properly)
> - [x] rows not aligned with chinese characters (need to trim display rows based on wcswidth)
> - [x] fix problems with empty lists both [] and [[],[]] 
> - [x] fix issue where item when filtering the cursor goes to a nonexistent item
> - [x] add unselectable_indices support for filtered rows and visual selection
> - [x] allow a keyword match for colours in columns (error, completed)
> - [x] fix time sort
> - [x] add colour highlighting for search and filter
> - [x] fix highlights when columns are shortened
> - [x] highlights wrap on bottom row
> - [x] Search
>    - [x] add search count
>    - [x] add option to continue search rather than finding all matches every time
>    - [x] problem when filter is applied
> - [x] Visual selection
>    - [x] (!!!) Fix visual selection in the entries are sorted differently.
>    - [x] when filtered it selects entries outside of those visible and throws an error
> - [x] add config file
> - [x] Highlights
>    - [x] add highlight colour differentiation for selected and under cursor
>    - [x] remain on same row when sorting (23-5-25)
>    - [x] add option to stay on item when sorting
> - [x] fix highlighting when cols are hidden
> - [x] Add hidden columns to function so that they remain hidden on refresh
> - [x] Fix the position of a filter and options when terminal resizes
> - [x] fix the filtering so that it works with more than one arg
> - [x] fix error when filtering to non-existing rows
> - [x] implement settings:
>      - [x] !11 show/hide 11th column
>      - [x] ???
> - [x] Allow state to be restored
>    - [x] allow search/filter to be passed to list_picker so that search can resume
>    - [x] cursor postion (x)
>    - [x] page number
>    - [x] sort
>    - [x] filter state
>    - [x] search
>    - [x] show/hide cols
> - [x] implement scroll as well as page view
> - [x] why the delay when pressing escape to cancel selection, remove filter, search, etc.
>    - [x] the problem is that ESCDELAY has to be set
> - [x] (!!!) high CPU usage
>    - [x] when val in `stdscr.timeout(val)` is low the cpu usage is high
> - [x] (!!!) When the input_field is too long the application crashes
> - [x] crash when selecting column from empty list
> - [x] sendReq()...
> - [x] add tabs for quick switching
> - [x] add header for title
> - [x] add header tabs
> - [x] add colour for active setting; e.g., when filter is being entered the bg should be blue
> - [x] check if mode filter in query when updating the query and if not change the mode
> - [x] when sorting on empty data it throws an error
> - [x] hiding a column doesn't hide the corresponding header cell
> - [x] add colour for selected column
> - [x] highlighting doesn't disappear when columns are hidden
> - [x] add scroll bar
> - [x] (!!!) fix crash when terminal is too small
> - [x] add option to start with X rows already selected (for watch active selection)
> - [x] prevent overspill on last row
> - [x] redo help
>    - [x] help screen doesn't adjust when terminal resized
>    - [x] add search/filter on help page
>    - [x] use list_picker to implement help
> - [x] +/- don't work when using scroll (rather than paginate)
> - [x] flickering when "watching"
>   - [x] stdscr.clear() vs stdscr.erase()
> - [x] change the cursor tracker from current_row, current_page to current_pos
> - [x] add flag to require options for a given entry
> - [x] option to number columns or not
> - [x] make sure `separator` works with header
> - [x] add cursor when inputing filter, opts, etc.
> - [x] remain on same row when resizing with +/-

># [!WARNING] Add docstrings
> - [x] aria2_detailing
> - [x] aria2c_utils
> - [x] aria2c_wrapper
> - [x] aria2tui
> - [x] aria_adduri
> - [x] clipboard_operations
> - [x] filtering
> - [x] help_screen
> - [x] input_field
> - [x] keys
> - [x] list_picker
> - [x] list_picker_colours
> - [x] searching
> - [x] sorting
> - [x] table_to_list_of_lists
> - [x] utils
