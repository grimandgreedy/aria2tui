import pyperclip
from utils import get_selected_indices, get_selected_values, format_row, format_row_full
from typing import Tuple

def copy_indices(indexed_items: list[Tuple[int, list[str]]], selections: dict) -> None:
    """ Copy list of selected indices to clipboard. """
    indices = get_selected_indices(indexed_items, selections)
    pyperclip.copy(', '.join(map(str, indices)))

def copy_values(indexed_items: list[Tuple[int, list[str]]], selections: dict, hidden_columns: list, column_widths:list, separator:str="  ") -> None:
    """ Copy list of selected values to clipboard. """
    formatted_values = [format_row(item[1], hidden_columns, column_widths, separator) for item in indexed_items if item[0] in get_selected_indices(indexed_items, selections)]
    pyperclip.copy('\n'.join(formatted_values))

def copy_full_values(indexed_items: list[Tuple[int, list[str]]], selections: dict, hidden_columns:list=[]) -> None:
    """ Copy full values of selected entries to clipboard. """
    selected_indices = get_selected_indices(indexed_items, selections)
    full_values = [format_row_full(indexed_items[i][1], hidden_columns) for i in selected_indices]
    pyperclip.copy('\n'.join(full_values))

def copy_all_to_clipboard(items: list[list[str]], hidden_columns: list) -> None:
    """ Copy all items to clipboard, not including hidden columns. """
    formatted_items = [[x for i, x in enumerate(item) if i not in hidden_columns] for item in items]
    pyperclip.copy(repr(formatted_items))

def copy_selected_rows_to_clipboard(items: list[list[str]], selections: dict) -> None:
    """ Copy selected rows to clipboard as python list. """
    formatted_items = [[x for i, x in enumerate(item)] for j, item in enumerate(items) if selections[j]] 

    pyperclip.copy(repr(formatted_items))

def copy_selected_visible_rows_to_clipboard(items: list[list[str]], selections: dict, hidden_columns:list=[]) -> None:
    """ Copy selected visible rows to clipboard as python list. """
    formatted_items = [[x for i, x in enumerate(item) if i not in hidden_columns] for j, item in enumerate(items) if selections[j]]  # Convert to Python list representation

    pyperclip.copy(repr(formatted_items))
