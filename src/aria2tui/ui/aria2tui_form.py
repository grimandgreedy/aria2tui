#!/usr/bin/env python3
"""
Curses-based form filling application.
Supports navigation, editing, scrolling, and keyboard shortcuts.
"""

import curses
from typing import Dict, List, Tuple


class FormField:
    """Represents a single form field."""

    def __init__(self, section: str, label: str, value: str):
        self.section = section
        self.label = label
        self.value = value


class FormApp:
    """Main form application using curses."""

    def __init__(self, stdscr, form_dict: Dict[str, Dict[str, str]]):
        self.stdscr = stdscr
        self.form_dict = form_dict
        self.fields: List[FormField] = []
        self.current_field = 0
        self.scroll_offset = 0
        self.editing = False
        self.cursor_pos = 0
        self.original_values = {}  # Store original values for discard

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
            for label, value in fields.items():
                self.fields.append(FormField(section, label, value))

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
            yes_attr = curses.color_pair(4) | curses.A_BOLD if selected == 0 else curses.A_NORMAL
            try:
                dialog_win.addstr(4, yes_x, yes_text, yes_attr)
            except curses.error:
                pass

            # Draw No button
            no_attr = curses.color_pair(5) | curses.A_BOLD if selected == 1 else curses.A_NORMAL
            try:
                dialog_win.addstr(4, no_x, no_text, no_attr)
            except curses.error:
                pass

            dialog_win.refresh()

            # Handle input
            key = dialog_win.getch()

            if key in (curses.KEY_LEFT, curses.KEY_RIGHT, 9, curses.KEY_BTAB):
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

        # Draw header
        header = " Form Editor - Tab: Next | Enter: Edit/Activate | g/G: Top/Bottom | q: Quit "
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

                    # Draw field label
                    label_text = f"  {field.label}:"
                    label_width = 30

                    if is_current and not self.editing:
                        self.stdscr.addstr(y, 2, label_text[:label_width].ljust(label_width), curses.color_pair(1))
                    else:
                        self.stdscr.addstr(y, 2, label_text[:label_width].ljust(label_width))

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
                        display_value = field.value if field.value else "<empty>"
                        attr = curses.color_pair(1) if is_current else curses.A_DIM if not field.value else curses.A_NORMAL
                        self.stdscr.addstr(y, value_x, display_value[:value_width], attr)

                    y += 1

            except curses.error:
                pass

        # Draw scrollbar
        self._draw_scrollbar(max_y, max_x)

        # Draw footer with buttons
        if self.editing:
            footer = f" EDITING - Field {self.current_field + 1}/{len(self.fields)} | Esc: Cancel | Enter: Save "
            try:
                self.stdscr.addstr(max_y - 1, 0, footer[:max_x-1], curses.A_REVERSE)
            except curses.error:
                pass
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
                    save_attr = curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE
                else:
                    # Not selected - just green
                    save_attr = curses.color_pair(4)
                self.stdscr.addstr(max_y - 1, save_x, save_text, save_attr)

                # Draw Discard button
                if self._is_on_discard_button():
                    # Selected - bright red with bold and reverse
                    discard_attr = curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE
                else:
                    # Not selected - just red
                    discard_attr = curses.color_pair(5)
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
        else:
            # Not in edit mode - hide cursor
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

    def _handle_navigation_mode(self, key: int) -> bool:
        """
        Handle keyboard input in navigation mode.
        Returns True if app should exit, False otherwise.
        """
        if key == 9:  # Tab - move to next item (field or button)
            self.current_field = (self.current_field + 1) % self._total_items()
            if self._is_on_field():
                self.cursor_pos = len(self.fields[self.current_field].value)

        elif key in [curses.KEY_BTAB, ord('k')]:  # Shift+Tab - move to previous item
            self.current_field = (self.current_field - 1) % self._total_items()
            if self._is_on_field():
                self.cursor_pos = len(self.fields[self.current_field].value)

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
                # Start editing the field
                self.editing = True
                self.cursor_pos = len(self.fields[self.current_field].value)

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


def run_form(form_dict: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Run the form application with the given form dictionary.

    Args:
        form_dict: Dictionary of sections containing field-value pairs

    Returns:
        Updated form dictionary with user input
    """
    def _curses_main(stdscr):
        app = FormApp(stdscr, form_dict)
        return app.run()

    return curses.wrapper(_curses_main)


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
