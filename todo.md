# aria2tui

> [!error] Errors
> - [ ] fix adding uris with filename. Data is the same but it is corrupted somehow. This is a problem with aria itself. **
> ```
> works vs doesn't work:
>   https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg
>   https://i.ytimg.com/vi/TaUlBYqGuiE/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLBVWNXUrlGnx3VtnPULUE6v0EteQg
>```
> - [ ] When downloads are updating quickly and I try to operate upon them it sometimes says that the indices are not in the list...


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
>  - [ ] infobox causes flickering


> [!IMPORTANT] Features
> - [ ] allow options when adding uris; perhaps use the same structure as the aria2c input file
>    - [x] implemented in principle
>    - [ ] Allow all possible options to be specified
> - [ ] improve menu navigation
>    - [x] when downloads are selected and we go back they should still be selected
> - [ ] add global stats bar
> - [ ] monitor log file
> - [ ] setup https connection
> - [ ] add source column, showing site from which it is being downloaded
> - [ ] Create passive notification
> - [ ] Add notifications to the following:
>    - adding downloads (# succeeeded or failed)
> - [ ] implement changeOption for downloads
> - [ ] add key to open download location using 'o'
> - [ ] (!!!) make operations upon downloads work only with certain download types:
>    - [x] make remove work with all
>    - [ ] queue operations only on those in the queue
>    - [ ] retry only on errored
> - [ ] add column to show download type (e.g., torrent)
> - [ ] add support for multiple aria servers
> - [ ] add more flags to filtering/searching
>    - [ ] invert
>    - [ ] case-sensitivity


> [!Important] Improvements
> - [ ] Redo colours
>   - completed: green
>   - active: blue
>   - paused: ??? gray?
> - [ ] (!!!) make operations on downloads into a batch request
> - [ ] examine parsing of toml (why are the arguments set outside of the main function?)
> - [ ] add to config
>    - [x] url
>    - [x] port
>    - [x] startupcmds
>    - [x] theme
>    - [x] paging vs scrolling
>    - [ ] highlights off
>    - [ ] color off
> - [ ] live setting changes
>    - [x] show/hide columns
>    - [x] centre in cols & centre in terminals
>    - [ ] theme
> - [?] Allow name to be specified with magnet link
>    - [?] I don't think this is possible to change in aria2c
> - [x] open files 
>    - [ ] open files of the same type in one instance
> - [x] make remove work with errored download
>    - [x] remove all errored/completed downloads works
> - [ ] fix operation loop to ensure that specific if/else can be removed; e.g., changePosition
> - [ ] redo handle_visual_selection()
> - [ ] redo cursor_up, cursor_down
> - [ ] Filter and search use the same tokenize and apply_filter function. Put them in utils.


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


# list_picker.py

> [!error] Errors
>- [ ] place cursor on last row and hold +.
>- [ ] why does curses crash when writing to the final char on the final line?
>   - [ ] is there a way to colour it?
>- [ ] errors thrown when length(header) != length(items[0])
>- [ ] Error handling needed
>   - [ ] apply_settings("sjjj") 
>- [ ] Error when drawing highlights. Have to put them in a try-except block
>- [ ] Add error-checking for:
>   - [ ] display of modes... 



> [!Bug] Bugs
> - [ ] sometimes the cursor shows, sometimes it doesn't
>    - cursor shows after opening nvim and returning to listpicker
> - [ ] fix resizing when input field active
> - [ ] Visual selection
>   - [ ] when visually selecting sometimes single rows above are highlighted (though not selected)
> - [ ] weird alignment problem when following characters are in cells:
>       - ： 
> - [ ] moving columns:
>   - ruins highlighting
>   - is not preserved in function_data
>   - implement indexed_columns
>   - will have to put header in function_data to track location of fields
> - [ ] regexp and field entry errors
>   - [ ] filter
>   - [ ] "--1 error .*" doesn't work but ".* --1" error does
>   - [ ] search
>   - [ ] highlights
>   - [ ] when +,* is added to the filter it errors out
>   - [ ] some capture groups don't work [^0]
>   - [ ] should general search be cell-wise?
>   - [ ] option to search visible columns only


> [!Important] Improvements
>- [ ] (!!!) Need to remove nonlocal args and pass all variables as arguments
>- [ ] change hidden_columns from set() to list()
>- [ ] make unselectable_indices work with filtering
>- [ ] look at adjustment for cursor position and hidden unselectable indices
>- [ ] each time we pass options it will resort and refilter; add an option to simply load the items that are passed
>- [ ] require_option should skip the prompt if an option has already been given
>- [ ] force option type; show notification to user if option not appropriate
>- [ ] add the ability to disable options for:
>   - [x] show footer
>   - [x] auto-refresh
>   - [x] edit cell
>   - [ ] sort
>   - [ ] visual selection
>   - [ ] disable visual selection when # is greater than max_selected
>   - [ ] NOTIFICATIONS
>   - [ ] OPTIONS
>- [ ] Colours
>   - [ ] Redo colours
>   - [ ] pass colours to list_picker in a more intuitive way
>   - [ ] complete get_colours loop
>   - [?] we have arbitrarily set application colours to be 0-50, notification 50-100 and help 100-150
> - [ ] make infobox variable in size and position 
> - [ ] break draw_screen() into functions
> - [ ] input_field
>      - [ ] implement readline keybinds
>          - [x] ctrl-f, ctrl-b
>      - [ ] add variable max display length
>- [ ] Highlights
>   - [ ] (!!!) there is a difference between search matches and highlights because the highlights operate on what is displayed
>      - [?] allow visual matches with searches?
>      - [?] hide highlights across fields?
>      - [?] e.g., mkv$ shows no highlights but does match
>   - [ ]  - e.g., wmv$ shows no matches but --3 wmv$ shows matches
>- [ ] Pipe
>   - [ ] if no items are selected pipe cursor to command
>- [ ] Redo keybinds
>   - [ ]  n/N search next/prev
>   - [ ] (!!!) allow key remappings; have a dictionary to remap
>      - [ ] escape should close option selections and notifications
>   - [ ] Add keybind to focus on next (visible) column
>- [?] adjust default column width based on current page?


> [!IMPORTANT] Features
>- [x] Create notification system
>    - [ ] add transient non-blocking notifications
>- [x] add different selection styles
>   - [x] row highlighted   
>   - [x] selection indicator (selection char at end of line)
>- [ ] add key-chain support. Can use the timeout to clear the key.
>   - [ ] gg
>   - [ ] count
>- [ ] add return value; e.g., refreshing
>- [ ] add indexed columns
>   - [ ] will fix highlighting when column order is switched
>- [ ] Copy
>   - [ ] Add copy selection box with options
>- [ ] Modes
>   - [x] Allow filtering in mode
>   - [x] Display modes
>   - [ ] Search
>   - [ ] ...
>- [ ] adjust width of particular columns
>- [ ] merge columns
>- [ ] show/hide col based on name; have tab auto complete
>- [ ] add option for padding/border
>   - [ ] stdscr.box??
>- [ ] add option to go to next dissimilar value in column
>   - [ ] e.g., select column 2 (download: complete), and pressing tab will go to the next entry that is not complete 
>- [ ] when column is selected try best guess search method


--------------

>[!warning] COPY:
>   copy IDs of selected rows (currently 'y')
>   copy selected rows, visible values of visible cols (currently 'Y')
>   copy selected rows, full values of visible cols (currently 'c') (NEW 'y')
>   copy full python table (currently/NEW 'C')
>   copy selected rows, full values of all cols (NEW 'Y')
>   copy selected rows as python table
>   copy selected rows as python table without hidden cols (NEW 'c')
>   m + c: copies all visible rows
>   Y = toggle_cols() + y
>   C = toggle_cols() + c
>   hidden cols, selected rows, 
>       selections = [False] * len(items)
>       selections = {i: False for i in range(len(items))}
--------------

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
