import pyperclip
from utils import get_selected_indices, get_selected_values, format_row, format_row_full

# Function to copy selected indices to clipboard
def copy_indices(indexed_items, selections):
    indices = get_selected_indices(indexed_items, selections)
    pyperclip.copy(', '.join(map(str, indices)))

# Function to copy selected values to clipboard
def copy_values(indexed_items, selections, hidden_columns, column_widths, separator="  "):
    formatted_values = [format_row(item[1], hidden_columns, column_widths, separator) for item in indexed_items if item[0] in get_selected_indices(indexed_items, selections)]
    pyperclip.copy('\n'.join(formatted_values))

# Function to copy full values of selected entries to clipboard
def copy_full_values(indexed_items, selections, hidden_columns=[]):
    selected_indices = get_selected_indices(indexed_items, selections)
    full_values = [format_row_full(indexed_items[i][1], hidden_columns) for i in selected_indices]  # Use format_row_full for full data
    pyperclip.copy('\n'.join(full_values))

def copy_all_to_clipboard(items, hidden_columns):
    formatted_items = [[x for i, x in enumerate(item) if i not in hidden_columns] for item in items]
    pyperclip.copy(repr(formatted_items))
    # stdscr.addstr(h - 2, 50, f"{len(formatted_items)}R,{len(formatted_items[0])}C list copied to clipboard", curses.color_pair(6))

def copy_selected_rows_to_clipboard(items, selections):
    formatted_items = [[x for i, x in enumerate(item)] for j, item in enumerate(items) if selections[j]]  # Convert to Python list representation

    pyperclip.copy(repr(formatted_items))
    # stdscr.addstr(h - 2, 50, f"{len(formatted_items)}R,{len(formatted_items[0])}C list copied to clipboard", curses.color_pair(6))

def copy_selected_visible_rows_to_clipboard(items, selections, hidden_columns=[]):
    formatted_items = [[x for i, x in enumerate(item) if i not in hidden_columns] for j, item in enumerate(items) if selections[j]]  # Convert to Python list representation

    pyperclip.copy(repr(formatted_items))
    # stdscr.addstr(h - 2, 50, f"{len(formatted_items)}R,{len(formatted_items[0])}C list copied to clipboard", curses.color_pair(6))
