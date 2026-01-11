#!/usr/bin/env python3
"""
Curses-based form filling application.
Supports navigation, editing, scrolling, and keyboard shortcuts.
"""

import curses
import subprocess
import tempfile
import os
from typing import Dict, List, Tuple, Union, Optional


class FormField:
    """Represents a single form field."""

    def __init__(self, section: str, label: str, value: str,
                 field_type: str = "text", options: Optional[List[str]] = None):
        self.section = section
        self.label = label
        self.value = value
        self.field_type = field_type  # "text", "cycle", "file"
        self.options = options or []  # For cycle: list of valid values


class FormApp:
    """Main form application using curses."""

    def __init__(self, stdscr, form_dict: Dict[str, Dict[str, Union[str, Tuple]]]):
        self.stdscr = stdscr
        self.form_dict = form_dict
        self.fields: List[FormField] = []
        self.current_field = 0
        self.scroll_offset = 0
        self.editing = False
        self.cursor_pos = 0
        self.original_values = {}  # Store original values for discard
        self.yazi_path = "yazi"  # Path to yazi executable

        # Search state
        self.search_query: Optional[str] = None
        self.search_matches: List[int] = []  # indices into self.fields
        self.search_input_mode: bool = False
        self.search_input: str = ""

        # Initialize curses settings
        curses.curs_set(1)
        # Color pairs are assumed to be already initialized by the parent application
        # Pair 1: Highlighted (black on white)
        # Pair 2: Section titles (cyan on black)
        # Pair 3: Editing (black on yellow)
        # Pair 4: Save button (black on green)
        # Pair 5: Discard button (black on red)

        # Build field list from form_dict
        self._build_fields()

        # Store original values for discard functionality
        for field in self.fields:
            self.original_values[id(field)] = field.value

    def _build_fields(self):
        """Build flat list of fields from nested dictionary."""
        for section, fields in self.form_dict.items():
            for label, field_data in fields.items():
                # Support both old format (string) and new format (tuple)
                if isinstance(field_data, str):
                    # Old format: just a string value
                    self.fields.append(FormField(section, label, field_data))
                elif isinstance(field_data, tuple):
                    # New format: (value, field_type, options?)
                    value = field_data[0]
                    field_type = field_data[1] if len(field_data) > 1 else "text"
                    options = field_data[2] if len(field_data) > 2 else None
                    self.fields.append(FormField(section, label, value, field_type, options))
                else:
                    # Fallback: treat as string
                    self.fields.append(FormField(section, label, str(field_data)))

    def _is_on_save_button(self) -> bool:
        """Check if current selection is on Save button."""
        return self.current_field == len(self.fields)

    def _is_on_discard_button(self) -> bool:
        """Check if current selection is on Discard button."""
        return self.current_field == len(self.fields) + 1

    def _is_on_field(self) -> bool:
        """Check if current selection is on a field."""
        return self.current_field < len(self.fields)

    def _total_items(self) -> int:
        """Total number of items in the navigation cycle (fields + buttons)."""
        return len(self.fields) + 2

    def _has_unsaved_changes(self) -> bool:
        """Check if any fields have been modified from their original values."""
        for field in self.fields:
            if field.value != self.original_values[id(field)]:
                return True
        return False

    def _launch_file_picker(self, current_path: str) -> Optional[str]:
        """
        Launch yazi file picker and return the selected path.
        Returns None if cancelled or no selection made.
        """
        # Create a temporary file to store the selected path
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Reset curses before launching yazi
            curses.endwin()

            # Launch yazi with the current path as starting directory
            start_dir = current_path if current_path and os.path.isdir(current_path) else os.getcwd()

            # Run yazi with output file
            result = subprocess.run(
                [self.yazi_path, start_dir, "--chooser-file", tmp_path],
                check=False
            )

            # Reinitialize curses
            self.stdscr.clear()
            self.stdscr.refresh()

            # Read the selected path from the temporary file
            if result.returncode == 0 and os.path.exists(tmp_path):
                with open(tmp_path, 'r') as f:
                    selected = f.read().strip()
                    if selected:
                        return selected

            return None

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _show_confirmation_dialog(self, message: str) -> bool:
        """
        Show a confirmation dialog with Yes/No options.
        Returns True if user selects Yes, False if No.
        """
        max_y, max_x = self.stdscr.getmaxyx()

        # Dialog dimensions
        dialog_width = min(60, max_x - 4)
        dialog_height = 7
        dialog_y = (max_y - dialog_height) // 2
        dialog_x = (max_x - dialog_width) // 2

        # Create dialog window
        dialog_win = curses.newwin(dialog_height, dialog_width, dialog_y, dialog_x)
        dialog_win.keypad(True)

        selected = 1  # 0 = Yes, 1 = No (default to No)

        while True:
            dialog_win.clear()
            dialog_win.border()

            # Draw message
            try:
                dialog_win.addstr(2, 2, message[:dialog_width-4], curses.A_BOLD)
            except curses.error:
                pass

            # Calculate button positions
            yes_text = "[ Yes ]"
            no_text = "[ No ]"
            button_spacing = 4
            total_button_width = len(yes_text) + button_spacing + len(no_text)
            button_start_x = (dialog_width - total_button_width) // 2

            yes_x = button_start_x
            no_x = button_start_x + len(yes_text) + button_spacing

            # Draw Yes button
            yes_attr = curses.color_pair(8) | curses.A_BOLD if selected == 0 else curses.A_NORMAL
            try:
                dialog_win.addstr(4, yes_x, yes_text, yes_attr)
            except curses.error:
                pass

            # Draw No button
            no_attr = curses.color_pair(7) | curses.A_BOLD if selected == 1 else curses.A_NORMAL
            try:
                dialog_win.addstr(4, no_x, no_text, no_attr)
            except curses.error:
                pass

            dialog_win.refresh()

            # Handle input
            key = dialog_win.getch()

            if key in (curses.KEY_LEFT, curses.KEY_RIGHT, 9, curses.KEY_BTAB, ord('j'), ord('k')):
                # Toggle between Yes and No
                selected = 1 - selected
            elif key in (curses.KEY_ENTER, 10, 13):
                # Confirm selection
                del dialog_win
                self.stdscr.touchwin()
                self.stdscr.refresh()
                return selected == 0  # True if Yes, False if No
            elif key == 27:  # Esc - treat as No
                del dialog_win
                self.stdscr.touchwin()
                self.stdscr.refresh()
                return False

    def _get_display_rows(self) -> List[Tuple[str, str, int]]:
        """
        Get list of display rows with their types.
        Returns: List of (type, content, field_index) tuples
        Type can be: 'section', 'field', 'blank'
        """
        rows = []
        current_section = None

        for idx, field in enumerate(self.fields):
            # Add section header if new section
            if field.section != current_section:
                if current_section is not None:
                    rows.append(('blank', '', -1))
                rows.append(('section', field.section, -1))
                rows.append(('blank', '', -1))
                current_section = field.section

            # Add field row
            rows.append(('field', field, idx))

        return rows

    def _calculate_scroll(self, max_y: int) -> None:
        """Calculate scroll offset to keep current field visible."""
        # Don't scroll if we're on a button
        if not self._is_on_field():
            return

        # If on the first field, always scroll to the top to show section headers
        if self.current_field == 0:
            self.scroll_offset = 0
            return

        rows = self._get_display_rows()

        # Find the row index of current field
        current_row = None
        for row_idx, (row_type, content, field_idx) in enumerate(rows):
            if row_type == 'field' and field_idx == self.current_field:
                current_row = row_idx
                break

        if current_row is None:
            return

        # Available space for content (reserve lines for header and footer)
        visible_height = max_y - 3

        # Adjust scroll to keep current field visible
        if current_row < self.scroll_offset:
            self.scroll_offset = current_row
        elif current_row >= self.scroll_offset + visible_height:
            self.scroll_offset = current_row - visible_height + 1

        # Ensure scroll offset doesn't go negative or too far
        self.scroll_offset = max(0, self.scroll_offset)
        max_scroll = max(0, len(rows) - visible_height)
        self.scroll_offset = min(self.scroll_offset, max_scroll)

    def _draw_scrollbar(self, max_y: int, max_x: int) -> None:
        """Draw scrollbar on the right side if needed."""
        rows = self._get_display_rows()
        visible_height = max_y - 3
        total_rows = len(rows)

        if total_rows <= visible_height:
            return  # No scrollbar needed

        scrollbar_x = max_x - 1
        scrollbar_height = visible_height

        # Calculate scrollbar thumb position and size
        thumb_size = max(1, int(scrollbar_height * visible_height / total_rows))
        thumb_pos = int(scrollbar_height * self.scroll_offset / total_rows)

        # Draw scrollbar track and thumb
        for y in range(2, 2 + scrollbar_height):
            try:
                if 2 + thumb_pos <= y < 2 + thumb_pos + thumb_size:
                    self.stdscr.addch(y, scrollbar_x, '█')
                else:
                    self.stdscr.addch(y, scrollbar_x, '│')
            except curses.error:
                pass

    def _draw(self) -> None:
        """Draw the form interface."""
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()

        # Calculate scroll
        self._calculate_scroll(max_y)

        # Track cursor position for edit mode
        edit_cursor_y = None
        edit_cursor_x = None
        # Track cursor position for search input mode
        search_cursor_y = None
        search_cursor_x = None

        # Draw header - show different messages based on current field type
        if self._is_on_field():
            field = self.fields[self.current_field]
            if field.field_type == "cycle":
                header = " Tab: Next Section | j/k: Navigate | Enter/Space: Cycle | g/G: Top/Bottom | /: Search | n/N: Next/Prev | q: Quit "
            elif field.field_type == "file":
                header = " Tab: Next Section | j/k: Navigate | Enter: File Picker | e: Edit | /: Search | n/N: Next/Prev | q: Quit "
            else:
                header = " Tab: Next Section | j/k: Navigate | Enter: Edit | g/G: Top/Bottom | /: Search | n/N: Next/Prev | q: Quit "
        else:
            header = " Tab: Next Section | j/k: Navigate | Enter: Activate | /: Search | n/N: Next/Prev | q: Quit "
        try:
            self.stdscr.addstr(0, 0, header[:max_x-1], curses.A_REVERSE)
        except curses.error:
            pass

        # Get display rows
        rows = self._get_display_rows()
        visible_height = max_y - 3

        # Draw visible rows
        y = 2
        for row_idx in range(self.scroll_offset, min(len(rows), self.scroll_offset + visible_height)):
            if y >= max_y - 1:
                break

            row_type, content, field_idx = rows[row_idx]

            try:
                if row_type == 'blank':
                    y += 1
                    continue

                elif row_type == 'section':
                    section_text = f"[ {content} ]"
                    self.stdscr.addstr(y, 2, section_text[:max_x-4], curses.color_pair(2) | curses.A_BOLD)
                    y += 1

                elif row_type == 'field':
                    field = content
                    is_current = (field_idx == self.current_field)
                    is_search_match = field_idx in self.search_matches if self.search_matches else False

                    # Draw field label
                    label_text = f"  {field.label}:"
                    label_width = 30

                    label_attr = curses.A_NORMAL
                    if is_current and not self.editing:
                        label_attr = curses.color_pair(9)
                    if is_search_match and not self.editing:
                        label_attr |= curses.A_BOLD
                    self.stdscr.addstr(y, 2, label_text[:label_width].ljust(label_width), label_attr)

                    # Draw field value
                    value_x = 2 + label_width + 2
                    value_width = max_x - value_x - 3  # Reserve space for scrollbar

                    if is_current and self.editing:
                        # Show input box with highlighted background in edit mode
                        display_value = field.value
                        # Fill the entire input width with background color
                        padded_value = display_value.ljust(value_width)

                        # Draw the field value with background
                        for i, char in enumerate(padded_value[:value_width]):
                            try:
                                if i == self.cursor_pos:
                                    # Draw cursor position with inverse video for maximum visibility
                                    self.stdscr.addstr(y, value_x + i, char, curses.color_pair(3) | curses.A_REVERSE)
                                else:
                                    self.stdscr.addstr(y, value_x + i, char, curses.color_pair(3))
                            except curses.error:
                                pass

                        # Store cursor position to set later
                        edit_cursor_y = y
                        edit_cursor_x = value_x + min(self.cursor_pos, value_width - 1)
                    else:
                        # Add field type indicator
                        indicator = ""
                        if field.field_type == "cycle":
                            indicator = " ↻"
                        elif field.field_type == "file":
                            indicator = " 📁"

                        display_value = field.value if field.value else "<empty>"
                        display_value_with_indicator = display_value + indicator

                        attr = curses.color_pair(9) if is_current else curses.A_DIM if not field.value else curses.A_NORMAL
                        if is_search_match:
                            attr |= curses.A_BOLD
                        self.stdscr.addstr(y, value_x, display_value_with_indicator[:value_width], attr)

                    y += 1

            except curses.error:
                pass

        # Draw scrollbar
        self._draw_scrollbar(max_y, max_x)

        # Draw footer with buttons or search prompt
        if self.editing:
            footer = f" EDITING - Field {self.current_field + 1}/{len(self.fields)} | Esc: Cancel | Enter: Save "
            try:
                self.stdscr.addstr(max_y - 1, 0, footer[:max_x-1], curses.A_REVERSE)
            except curses.error:
                pass
        elif self.search_input_mode:
            # Draw search prompt
            prompt = f"/{self.search_input}"
            helper = "  (Enter: search, Esc: cancel)"
            footer_text = (prompt + helper)[:max_x-1]
            try:
                self.stdscr.addstr(max_y - 1, 0, " " * (max_x - 1), curses.A_REVERSE)
                self.stdscr.addstr(max_y - 1, 0, footer_text, curses.A_REVERSE)
            except curses.error:
                pass
            search_cursor_y = max_y - 1
            search_cursor_x = min(len(prompt), max_x - 2)
        else:
            # Draw button bar
            try:
                # Clear the footer line
                self.stdscr.addstr(max_y - 1, 0, " " * (max_x - 1), curses.A_NORMAL)

                # Calculate button positions
                save_text = "[ Save ]"
                discard_text = "[ Discard Changes ]"
                button_spacing = 4

                # Center the buttons
                total_width = len(save_text) + button_spacing + len(discard_text)
                start_x = (max_x - total_width) // 2

                save_x = start_x
                discard_x = start_x + len(save_text) + button_spacing

                # Draw Save button
                if self._is_on_save_button():
                    # Selected - bright green with bold and reverse
                    save_attr = curses.color_pair(8) | curses.A_BOLD | curses.A_REVERSE
                else:
                    # Not selected - just green
                    save_attr = curses.color_pair(8)
                self.stdscr.addstr(max_y - 1, save_x, save_text, save_attr)

                # Draw Discard button
                if self._is_on_discard_button():
                    # Selected - bright red with bold and reverse
                    discard_attr = curses.color_pair(7) | curses.A_BOLD | curses.A_REVERSE
                else:
                    # Not selected - just red
                    discard_attr = curses.color_pair(7)
                self.stdscr.addstr(max_y - 1, discard_x, discard_text, discard_attr)

            except curses.error:
                pass

        # Set cursor visibility and position after all drawing is complete
        if self.editing and edit_cursor_y is not None and edit_cursor_x is not None:
            # In edit mode - show cursor at the edit position
            try:
                curses.curs_set(2)  # Very visible block cursor
                self.stdscr.move(edit_cursor_y, edit_cursor_x)
            except curses.error:
                pass
        elif self.search_input_mode and search_cursor_y is not None and search_cursor_x is not None:
            # In search input mode - show cursor at end of prompt
            try:
                curses.curs_set(2)
                self.stdscr.move(search_cursor_y, search_cursor_x)
            except curses.error:
                pass
        else:
            # Not in edit or search mode - hide cursor
            try:
                curses.curs_set(0)
            except curses.error:
                pass

        self.stdscr.refresh()


    def _handle_edit_mode(self, key: int) -> None:
        """Handle keyboard input in edit mode."""
        current_field = self.fields[self.current_field]

        if key == 27:  # Esc - cancel editing
            self.editing = False
            self.cursor_pos = len(current_field.value)

        elif key in (curses.KEY_ENTER, 10, 13):  # Enter - save and exit edit mode
            self.editing = False
            self.cursor_pos = len(current_field.value)

        # Readline keybinds
        elif key == 1:  # Ctrl+A - go to beginning of line
            self.cursor_pos = 0

        elif key == 5:  # Ctrl+E - go to end of line
            self.cursor_pos = len(current_field.value)

        elif key == 11:  # Ctrl+K - kill to end of line
            current_field.value = current_field.value[:self.cursor_pos]

        elif key == 21:  # Ctrl+U - kill to beginning of line
            current_field.value = current_field.value[self.cursor_pos:]
            self.cursor_pos = 0

        elif key == 23:  # Ctrl+W - delete word backwards
            if self.cursor_pos > 0:
                # Find the start of the word
                pos = self.cursor_pos - 1
                # Skip trailing whitespace
                while pos > 0 and current_field.value[pos].isspace():
                    pos -= 1
                # Delete the word
                while pos > 0 and not current_field.value[pos - 1].isspace():
                    pos -= 1
                current_field.value = (
                    current_field.value[:pos] +
                    current_field.value[self.cursor_pos:]
                )
                self.cursor_pos = pos

        elif key == curses.KEY_BACKSPACE or key == 127:
            if self.cursor_pos > 0:
                current_field.value = (
                    current_field.value[:self.cursor_pos-1] +
                    current_field.value[self.cursor_pos:]
                )
                self.cursor_pos -= 1

        elif key == curses.KEY_DC:  # Delete key
            if self.cursor_pos < len(current_field.value):
                current_field.value = (
                    current_field.value[:self.cursor_pos] +
                    current_field.value[self.cursor_pos+1:]
                )

        elif key == curses.KEY_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)

        elif key == curses.KEY_RIGHT:
            self.cursor_pos = min(len(current_field.value), self.cursor_pos + 1)

        elif key == curses.KEY_HOME:
            self.cursor_pos = 0

        elif key == curses.KEY_END:
            self.cursor_pos = len(current_field.value)

        elif 32 <= key <= 126:  # Printable characters
            char = chr(key)
            current_field.value = (
                current_field.value[:self.cursor_pos] +
                char +
                current_field.value[self.cursor_pos:]
            )
            self.cursor_pos += 1

    def _get_section_boundaries(self) -> List[Tuple[str, int, int]]:
        """
        Get list of sections with their start and end field indices.
        Returns: List of (section_name, start_idx, end_idx) tuples
        """
        boundaries = []
        current_section = None
        start_idx = 0

        for idx, field in enumerate(self.fields):
            if field.section != current_section:
                if current_section is not None:
                    boundaries.append((current_section, start_idx, idx - 1))
                current_section = field.section
                start_idx = idx

        # Add the last section
        if current_section is not None:
            boundaries.append((current_section, start_idx, len(self.fields) - 1))

        return boundaries

    def _jump_to_next_section(self):
        """Jump to the first field of the next section or to buttons."""
        if self._is_on_save_button():
            # From Save button, go to Discard button
            self.current_field = len(self.fields) + 1
        elif self._is_on_discard_button():
            # From Discard button, wrap to first field
            self.current_field = 0
            self.cursor_pos = len(self.fields[0].value) if self.fields else 0
        elif self._is_on_field():
            current_section = self.fields[self.current_field].section
            boundaries = self._get_section_boundaries()

            # Find current section
            current_section_idx = None
            for idx, (section, start, end) in enumerate(boundaries):
                if section == current_section:
                    current_section_idx = idx
                    break

            if current_section_idx is not None:
                if current_section_idx < len(boundaries) - 1:
                    # Jump to next section's first field
                    next_start = boundaries[current_section_idx + 1][1]
                    self.current_field = next_start
                    self.cursor_pos = len(self.fields[next_start].value)
                else:
                    # Jump to Save button
                    self.current_field = len(self.fields)

    def _jump_to_prev_section(self):
        """Jump to the first field of the previous section or to buttons."""
        if self._is_on_discard_button():
            # From Discard button, go to Save button
            self.current_field = len(self.fields)
        elif self._is_on_save_button():
            # From Save button, go to last section
            if self.fields:
                self.current_field = len(self.fields) - 1
                self.cursor_pos = len(self.fields[self.current_field].value)
        elif self._is_on_field():
            current_section = self.fields[self.current_field].section
            boundaries = self._get_section_boundaries()

            # Find current section
            current_section_idx = None
            for idx, (section, start, end) in enumerate(boundaries):
                if section == current_section:
                    current_section_idx = idx
                    break

            if current_section_idx is not None:
                if current_section_idx > 0:
                    # Jump to previous section's first field
                    prev_start = boundaries[current_section_idx - 1][1]
                    self.current_field = prev_start
                    self.cursor_pos = len(self.fields[prev_start].value)
                else:
                    # Jump to Discard button (wrap around)
                    self.current_field = len(self.fields) + 1

    def _start_search_input(self) -> None:
        """Enter search input mode for finding settings."""
        self.search_input_mode = True
        # Start with empty search text each time
        self.search_input = ""

    def _perform_search(self, query: str) -> None:
        """Perform a case-insensitive search over field labels and sections."""
        normalized = query.lower()
        matches: List[int] = []
        for idx, field in enumerate(self.fields):
            haystack = f"{field.section} {field.label}".lower()
            if normalized in haystack:
                matches.append(idx)

        self.search_query = query
        self.search_matches = matches

        if matches:
            # Jump to the first match
            self.current_field = matches[0]
            self.cursor_pos = len(self.fields[self.current_field].value)
        else:
            # No matches found; leave current selection unchanged
            try:
                curses.flash()
            except curses.error:
                pass

    def _handle_search_input(self, key: int) -> None:
        """Handle keyboard input while in search prompt mode."""
        if key == 27:  # Esc - cancel search
            self.search_input_mode = False
            self.search_input = ""
            return

        if key in (curses.KEY_ENTER, 10, 13):  # Enter - run search
            query = self.search_input.strip()
            self.search_input_mode = False
            if query:
                self._perform_search(query)
            else:
                # Empty query clears current search
                self.search_query = None
                self.search_matches = []
            return

        if key in (curses.KEY_BACKSPACE, 127, curses.KEY_DC):
            if self.search_input:
                self.search_input = self.search_input[:-1]
            return

        if 32 <= key <= 126:  # Printable characters
            self.search_input += chr(key)

    def _handle_navigation_mode(self, key: int) -> bool:
        """Handle keyboard input in navigation mode.
        Returns True if app should exit, False otherwise.
        """
        if key == ord('/'):
            # Enter search input mode
            self._start_search_input()

        elif key in (ord('n'), ord('N')):
            # Jump between search results if a search is active
            if self.search_query and self.search_matches:
                matches = self.search_matches
                try:
                    current_index = matches.index(self.current_field)
                except ValueError:
                    current_index = -1

                if key == ord('n'):
                    next_index = (current_index + 1) % len(matches)
                else:  # 'N' - previous match
                    next_index = (current_index - 1) % len(matches)

                self.current_field = matches[next_index]
                self.cursor_pos = len(self.fields[self.current_field].value)

        elif key == 9:  # Tab - jump to next section
            self._jump_to_next_section()

        elif key == curses.KEY_BTAB:  # Shift+Tab - jump to previous section
            self._jump_to_prev_section()

        elif key in (curses.KEY_ENTER, 10, 13):  # Enter - edit field or activate button

            if self._is_on_save_button():
                return True  # Exit and save
            elif self._is_on_discard_button():
                # Check if there are unsaved changes
                if self._has_unsaved_changes():
                    # Show confirmation dialog
                    if self._show_confirmation_dialog("Are you sure you want to exit without saving?"):
                        # User confirmed - discard changes and exit
                        for field in self.fields:
                            field.value = self.original_values[id(field)]
                        return True
                    # User cancelled - don't exit
                else:
                    # No changes, just exit
                    return True
            elif self._is_on_field():
                field = self.fields[self.current_field]

                if field.field_type == "text":
                    # Start editing the text field
                    self.editing = True
                    self.cursor_pos = len(field.value)

                elif field.field_type == "cycle":
                    # Cycle to next value
                    if field.options and field.value in field.options:
                        current_idx = field.options.index(field.value)
                        field.value = field.options[(current_idx + 1) % len(field.options)]
                    elif field.options:
                        # Value not in options, set to first option
                        field.value = field.options[0]

                elif field.field_type == "file":
                    # Launch file picker
                    selected_path = self._launch_file_picker(field.value)
                    if selected_path:
                        field.value = selected_path

        elif key == ord(' '):  # Space bar - cycle fields only
            if self._is_on_field():
                field = self.fields[self.current_field]
                if field.field_type == "cycle":
                    # Cycle to next value
                    if field.options and field.value in field.options:
                        current_idx = field.options.index(field.value)
                        field.value = field.options[(current_idx + 1) % len(field.options)]
                    elif field.options:
                        # Value not in options, set to first option
                        field.value = field.options[0]

        elif key == ord('e'):  # 'e' key - edit file path as text
            if self._is_on_field():
                field = self.fields[self.current_field]
                if field.field_type == "file":
                    # Start editing the file path as text
                    self.editing = True
                    self.cursor_pos = len(field.value)

        elif key == ord('q') or key == ord('Q'):  # Quit
            # Check if there are unsaved changes
            if self._has_unsaved_changes():
                # Show confirmation dialog
                if self._show_confirmation_dialog("Are you sure you want to exit without saving?"):
                    # User confirmed - discard changes and exit
                    for field in self.fields:
                        field.value = self.original_values[id(field)]
                    return True
                # User cancelled - don't exit
            else:
                # No changes, just exit
                return True

        elif key == ord('g'):  # Go to top (first field)
            self.current_field = 0
            self.cursor_pos = len(self.fields[self.current_field].value)

        elif key == ord('G'):  # Go to bottom (last field)
            self.current_field = len(self.fields) - 1
            self.cursor_pos = len(self.fields[self.current_field].value)

        elif key in [curses.KEY_UP, ord('k')]:
            if self.current_field > 0:
                self.current_field -= 1
                if self._is_on_field():
                    self.cursor_pos = len(self.fields[self.current_field].value)

        elif key in [curses.KEY_DOWN, ord('j')]:
            if self.current_field < self._total_items() - 1:
                self.current_field += 1
                if self._is_on_field():
                    self.cursor_pos = len(self.fields[self.current_field].value)

        return False

    def run(self) -> Dict[str, Dict[str, str]]:
        """Run the form application main loop."""
        should_exit = False

        while not should_exit:
            self._draw()

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                should_exit = True
                continue

            if self.editing:
                self._handle_edit_mode(key)
            elif self.search_input_mode:
                # Handle search prompt input
                self._handle_search_input(key)
            else:
                # Handle navigation, which returns True if we should exit
                should_exit = self._handle_navigation_mode(key)

        # Reconstruct form_dict from fields
        result = {}
        for field in self.fields:
            if field.section not in result:
                result[field.section] = {}
            result[field.section][field.label] = field.value

        return result


def run_form(form_dict: Dict[str, Dict[str, Union[str, Tuple]]]) -> Dict[str, Dict[str, str]]:
    """
    Run the form application with the given form dictionary.

    Args:
        form_dict: Dictionary of sections containing field-value pairs.
                   Values can be:
                   - str: Simple text field
                   - Tuple: (value, field_type, options)
                     - field_type: "text", "cycle", or "file"
                     - options: List of values for "cycle" type

    Returns:
        Updated form dictionary with user input (values only, no type info)

    Examples:
        # Simple text fields (backward compatible)
        form_dict = {
            "Section": {
                "Name": "default_value"
            }
        }

        # With field types
        form_dict = {
            "Section": {
                "Name": ("John", "text"),
                "Enabled": ("true", "cycle", ["true", "false"]),
                "Path": ("/home", "file")
            }
        }
    """
    def _curses_main(stdscr):
        app = FormApp(stdscr, form_dict)
        return app.run()

    return curses.wrapper(_curses_main)


class FormViewerApp:
    """Read-only viewer for structured form data.

    This uses the same flattened field structure and navigation
    as FormApp, but does not allow editing or saving.
    """

    def __init__(self, stdscr, form_dict: Dict[str, Dict[str, Union[str, Tuple]]]):
        self.stdscr = stdscr
        self.form_dict = form_dict
        self.fields: List[FormField] = []
        self.current_field = 0
        self.scroll_offset = 0

        # Search state
        self.search_query: Optional[str] = None
        self.search_matches: List[int] = []  # indices into self.fields
        self.search_input_mode: bool = False
        self.search_input: str = ""

        # Build field list from form_dict
        self._build_fields()

        # Viewer is purely read-only; hide cursor by default
        try:
            curses.curs_set(0)
        except curses.error:
            pass

    def _build_fields(self) -> None:
        """Build flat list of fields from nested dictionary."""
        for section, fields in self.form_dict.items():
            for label, field_data in fields.items():
                if isinstance(field_data, str):
                    self.fields.append(FormField(section, label, field_data))
                elif isinstance(field_data, tuple):
                    value = field_data[0]
                    field_type = field_data[1] if len(field_data) > 1 else "text"
                    options = field_data[2] if len(field_data) > 2 else None
                    self.fields.append(FormField(section, label, value, field_type, options))
                else:
                    self.fields.append(FormField(section, label, str(field_data)))

    def _get_display_rows(self) -> List[Tuple[str, str, int]]:
        """Return display rows as (type, content, field_index).

        Type can be: 'section', 'field', 'blank'.
        """
        rows: List[Tuple[str, str, int]] = []
        current_section: Optional[str] = None

        for idx, field in enumerate(self.fields):
            if field.section != current_section:
                if current_section is not None:
                    rows.append(("blank", "", -1))
                rows.append(("section", field.section, -1))
                rows.append(("blank", "", -1))
                current_section = field.section

            rows.append(("field", field, idx))

        return rows

    def _calculate_scroll(self, max_y: int) -> None:
        """Calculate scroll offset to keep current field visible."""
        if not self.fields:
            self.scroll_offset = 0
            return

        # Always show section headers when near the top
        if self.current_field == 0:
            self.scroll_offset = 0
            return

        rows = self._get_display_rows()

        # Find the row index of current field
        current_row: Optional[int] = None
        for row_idx, (row_type, _content, field_idx) in enumerate(rows):
            if row_type == "field" and field_idx == self.current_field:
                current_row = row_idx
                break

        if current_row is None:
            return

        # Available space for content (reserve lines for header and footer)
        visible_height = max_y - 3

        if current_row < self.scroll_offset:
            self.scroll_offset = current_row
        elif current_row >= self.scroll_offset + visible_height:
            self.scroll_offset = current_row - visible_height + 1

        self.scroll_offset = max(0, self.scroll_offset)
        max_scroll = max(0, len(rows) - visible_height)
        self.scroll_offset = min(self.scroll_offset, max_scroll)

    def _draw_scrollbar(self, max_y: int, max_x: int) -> None:
        """Draw scrollbar on the right side if needed."""
        rows = self._get_display_rows()
        visible_height = max_y - 3
        total_rows = len(rows)

        if total_rows <= visible_height:
            return

        scrollbar_x = max_x - 1
        scrollbar_height = visible_height

        thumb_size = max(1, int(scrollbar_height * visible_height / total_rows))
        thumb_pos = int(scrollbar_height * self.scroll_offset / total_rows)

        for y in range(2, 2 + scrollbar_height):
            try:
                if 2 + thumb_pos <= y < 2 + thumb_pos + thumb_size:
                    self.stdscr.addch(y, scrollbar_x, "█")
                else:
                    self.stdscr.addch(y, scrollbar_x, "│")
            except curses.error:
                pass

    def _get_section_boundaries(self) -> List[Tuple[str, int, int]]:
        """Return (section_name, start_idx, end_idx) tuples."""
        boundaries: List[Tuple[str, int, int]] = []
        current_section: Optional[str] = None
        start_idx = 0

        for idx, field in enumerate(self.fields):
            if field.section != current_section:
                if current_section is not None:
                    boundaries.append((current_section, start_idx, idx - 1))
                current_section = field.section
                start_idx = idx

        if current_section is not None:
            boundaries.append((current_section, start_idx, len(self.fields) - 1))

        return boundaries

    def _jump_to_next_section(self) -> None:
        """Jump to the first field of the next section (wrap around)."""
        if not self.fields:
            return

        current_section = self.fields[self.current_field].section
        boundaries = self._get_section_boundaries()

        current_section_idx: Optional[int] = None
        for idx, (section, _start, _end) in enumerate(boundaries):
            if section == current_section:
                current_section_idx = idx
                break

        if current_section_idx is None:
            return

        if current_section_idx < len(boundaries) - 1:
            next_start = boundaries[current_section_idx + 1][1]
            self.current_field = next_start
        else:
            # Wrap to first section
            self.current_field = boundaries[0][1]

    def _jump_to_prev_section(self) -> None:
        """Jump to the first field of the previous section (wrap around)."""
        if not self.fields:
            return

        current_section = self.fields[self.current_field].section
        boundaries = self._get_section_boundaries()

        current_section_idx: Optional[int] = None
        for idx, (section, _start, _end) in enumerate(boundaries):
            if section == current_section:
                current_section_idx = idx
                break

        if current_section_idx is None:
            return

        if current_section_idx > 0:
            prev_start = boundaries[current_section_idx - 1][1]
            self.current_field = prev_start
        else:
            # Wrap to last section
            self.current_field = boundaries[-1][1]

    def _start_search_input(self) -> None:
        """Enter search input mode for finding fields."""
        self.search_input_mode = True
        self.search_input = ""

    def _perform_search(self, query: str) -> None:
        """Search over section names and field labels."""
        normalized = query.lower()
        matches: List[int] = []
        for idx, field in enumerate(self.fields):
            haystack = f"{field.section} {field.label}".lower()
            if normalized in haystack:
                matches.append(idx)

        self.search_query = query
        self.search_matches = matches

        if matches:
            self.current_field = matches[0]
        else:
            try:
                curses.flash()
            except curses.error:
                pass

    def _handle_search_input(self, key: int) -> None:
        """Handle keyboard input in search prompt mode."""
        if key == 27:  # Esc
            self.search_input_mode = False
            self.search_input = ""
            return

        if key in (curses.KEY_ENTER, 10, 13):
            query = self.search_input.strip()
            self.search_input_mode = False
            if query:
                self._perform_search(query)
            else:
                self.search_query = None
                self.search_matches = []
            return

        if key in (curses.KEY_BACKSPACE, 127, curses.KEY_DC):
            if self.search_input:
                self.search_input = self.search_input[:-1]
            return

        if 32 <= key <= 126:
            self.search_input += chr(key)

    def _handle_navigation_mode(self, key: int) -> bool:
        """Handle navigation keys. Return True to exit."""
        if key == ord('/'):
            self._start_search_input()

        elif key in (ord('n'), ord('N')):
            if self.search_query and self.search_matches:
                matches = self.search_matches
                try:
                    current_index = matches.index(self.current_field)
                except ValueError:
                    current_index = -1

                if key == ord('n'):
                    next_index = (current_index + 1) % len(matches)
                else:
                    next_index = (current_index - 1) % len(matches)

                self.current_field = matches[next_index]

        elif key == 9:  # Tab
            self._jump_to_next_section()

        elif key == curses.KEY_BTAB:  # Shift+Tab
            self._jump_to_prev_section()

        elif key in (ord('q'), ord('Q'), 27):  # q/Q/Esc
            return True

        elif key == ord('g') and self.fields:  # Go to top
            self.current_field = 0

        elif key == ord('G') and self.fields:  # Go to bottom
            self.current_field = len(self.fields) - 1

        elif key in (curses.KEY_UP, ord('k')):
            if self.current_field > 0:
                self.current_field -= 1

        elif key in (curses.KEY_DOWN, ord('j')):
            if self.current_field < len(self.fields) - 1:
                self.current_field += 1

        return False

    def _draw(self) -> None:
        """Draw the read-only viewer interface."""
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()

        self._calculate_scroll(max_y)

        # Track cursor position for search input mode
        search_cursor_y: Optional[int] = None
        search_cursor_x: Optional[int] = None

        header = " VIEW MODE | j/k: Navigate | g/G: Top/Bottom | /: Search | n/N: Next/Prev | q: Close "
        try:
            self.stdscr.addstr(0, 0, header[: max_x - 1], curses.A_REVERSE)
        except curses.error:
            pass

        rows = self._get_display_rows()
        visible_height = max_y - 3

        y = 2
        for row_idx in range(self.scroll_offset, min(len(rows), self.scroll_offset + visible_height)):
            if y >= max_y - 1:
                break

            row_type, content, field_idx = rows[row_idx]

            try:
                if row_type == "blank":
                    y += 1
                    continue

                if row_type == "section":
                    section_text = f"[ {content} ]"
                    self.stdscr.addstr(y, 2, section_text[: max_x - 4], curses.color_pair(2) | curses.A_BOLD)
                    y += 1
                    continue

                if row_type == "field":
                    field = content
                    is_current = field_idx == self.current_field
                    is_search_match = field_idx in self.search_matches if self.search_matches else False

                    label_text = f"  {field.label}:"
                    label_width = 30

                    label_attr = curses.A_NORMAL
                    if is_current:
                        label_attr = curses.color_pair(9)
                    if is_search_match:
                        label_attr |= curses.A_BOLD
                    self.stdscr.addstr(y, 2, label_text[:label_width].ljust(label_width), label_attr)

                    value_x = 2 + label_width + 2
                    value_width = max_x - value_x - 3

                    indicator = ""
                    if field.field_type == "cycle":
                        indicator = " ↻"
                    elif field.field_type == "file":
                        indicator = " 📁"

                    display_value = field.value if field.value else "<empty>"
                    display_value_with_indicator = display_value + indicator

                    attr = curses.color_pair(9) if is_current else curses.A_DIM if not field.value else curses.A_NORMAL
                    if is_search_match:
                        attr |= curses.A_BOLD
                    self.stdscr.addstr(y, value_x, display_value_with_indicator[:value_width], attr)

                    y += 1

            except curses.error:
                pass

        self._draw_scrollbar(max_y, max_x)

        if self.search_input_mode:
            prompt = f"/{self.search_input}"
            helper = "  (Enter: search, Esc: cancel)"
            footer_text = (prompt + helper)[: max_x - 1]
            try:
                self.stdscr.addstr(max_y - 1, 0, " " * (max_x - 1), curses.A_REVERSE)
                self.stdscr.addstr(max_y - 1, 0, footer_text, curses.A_REVERSE)
            except curses.error:
                pass
            search_cursor_y = max_y - 1
            search_cursor_x = min(len(prompt), max_x - 2)
        else:
            footer = " q: Close "
            try:
                self.stdscr.addstr(max_y - 1, 0, " " * (max_x - 1), curses.A_REVERSE)
                self.stdscr.addstr(max_y - 1, 0, footer[: max_x - 1], curses.A_REVERSE)
            except curses.error:
                pass

        # Cursor handling
        if self.search_input_mode and search_cursor_y is not None and search_cursor_x is not None:
            try:
                curses.curs_set(2)
                self.stdscr.move(search_cursor_y, search_cursor_x)
            except curses.error:
                pass
        else:
            try:
                curses.curs_set(0)
            except curses.error:
                pass

        self.stdscr.refresh()

    def run(self) -> None:
        """Run the viewer main loop until the user exits."""
        should_exit = False

        while not should_exit:
            self._draw()

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if self.search_input_mode:
                self._handle_search_input(key)
            else:
                should_exit = self._handle_navigation_mode(key)


def run_viewer(form_dict: Dict[str, Dict[str, Union[str, Tuple]]]) -> None:
    """Run the read-only structured data viewer.

    The input structure matches run_form: a mapping of sections to
    label/value pairs. Tuple values are interpreted the same way as
    in run_form, but are displayed read-only.
    """

    def _curses_main(stdscr):
        app = FormViewerApp(stdscr, form_dict)
        app.run()

    curses.wrapper(_curses_main)


if __name__ == "__main__":
    curses.set_escdelay(25)
    # Example usage
    form_dict = {
        "Basic Details": {
            "First Name": "",
            "Surname": ""
        },
        "Emergency Contact": {
            "First Name": "",
            "Surname": "",
            "Contact Number": ""
        },
        "Notes": {
            "Additional Notes": ""
        }
    }

    result = run_form(form_dict)

    # Print results
    print("\n=== Form Results ===")
    for section, fields in result.items():
        print(f"\n{section}:")
        for label, value in fields.items():
            print(f"  {label}: {value}")
