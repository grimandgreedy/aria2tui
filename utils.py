from wcwidth import wcwidth, wcswidth
from math import log10
from typing import Tuple

def truncate_to_display_width(text: str, max_column_width: int, centre=False) -> str:
    """ 
    Truncate and/or pad text to max_column_width using wcwidth to ensure visual width is correct 
        with foreign character sets. 

    Return: The truncated and/or padded string which has a visual length of max_column_width. 
        If centre=True then the string is centred, if applicable.

    """
    result = ''
    width = 0
    for char in text:
        w = wcwidth(char)
        if w < 0:
            continue
        if width + w > max_column_width:
            break
        result += char
        width += w
    # Pad if it's shorter
    padding = max_column_width - wcswidth(result)
    # return result + ' ' * padding
    if centre:
        result = ' '*(padding//2) + result + ' '*(padding//2 + padding%2)
    else:
        result = result + ' ' * padding 
    return result

def format_row_full(row: list[str], hidden_columns:list = []) -> str:
    """ Format list of strings as a tab-separated single string. No hidden columns. """
    return '\t'.join(str(row[i]) for i in range(len(row)) if i not in hidden_columns)

def format_full_row(row:str) -> str:
    """ Format list of strings as a tab-separated single string. Includes hidden columns. """
    return '\t'.join(row)


def format_row(row: list[str], hidden_columns: list, column_widths: list[int], separator: str, centre:bool=False) -> str:
    """ Format list of strings as a single string. Requires separator string and the maximum width of the columns. """
    row_str = ""
    for i, cell in enumerate(row):
        if i in hidden_columns: continue
        val = truncate_to_display_width(str(cell), column_widths[i], centre)
        row_str += val + separator
    return row_str
    # return row_str.strip()

def get_column_widths(items: list[list[str]], header: list[str]=[], max_column_width:int=70, number_columns:bool=True) -> list[int]:
    """ Calculate maximum width of each column with clipping. """
    widths = [max(wcswidth(str(row[i])) for row in items) for i in range(len(items[0]))]
    if header:
        header_widths = [wcswidth(str(h))+int(log10(i+1))+3*int(number_columns) for i, h in enumerate(header)]
        return [min(max_column_width, max(widths[i], header_widths[i])) for i in range(len(header))]
    return [min(max_column_width, width) for width in widths]

def get_mode_widths(item_list: list[str]) -> list[int]:
    """ Calculate the maximum width of modes with clipping. """
    widths = [wcswidth(str(row)) for row in item_list]
    return widths

def intStringToExponentString(n: str) -> str:
    """ Return exponent representation of integer. E.g., 1234 -> ¹²³⁴ """
    n = str(n)
    digitdict = { "0" : "⁰", "1" : "¹", "2" : "²", "3" : "³", "4" : "⁴", "5" : "⁵", "6" : "⁶", "7" : "⁷", "8" : "⁸", "9" : "⁹"}
    return "".join([digitdict[char] for char in n])

def convert_seconds(seconds:int, long_format:bool=False) -> str:
    """ Convert seconds to human readable format. E.g., 60*60*24*3+62=772262 -> 3d2m2s """
    if isinstance(seconds, str):
        seconds = int(seconds)

    # Calculate years, days, hours, minutes, and seconds
    years = seconds // (365 * 24 * 3600)
    days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    # Long format = years, days, hours, minutes, seconds
    if long_format:
        human_readable = []
        if years > 0:
            human_readable.append(f"{years} year{'s' if years > 1 else ''}")
        if days > 0:
            human_readable.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            human_readable.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            human_readable.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        if remaining_seconds > 0 or not human_readable:
            human_readable.append(f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}")
        return ', '.join(human_readable)
    else:
        # Compact format = y, d, h, m, s
        compact_parts = []
        if years > 0:
            compact_parts.append(f"{years}y")
        if days > 0:
            compact_parts.append(f"{days}d")
        if hours > 0:
            compact_parts.append(f"{hours}h")
        if minutes > 0:
            compact_parts.append(f"{minutes}m")
        if remaining_seconds > 0 or not compact_parts:
            compact_parts.append(f"{remaining_seconds}s")
        return ''.join(compact_parts)

def convert_percentage_to_ascii_bar(p:int, chars:int=8) -> str:
    """ Convert percentage to an ascii status bar of length chars. """

    done = "█"
    notdone = "▒"
    return done * int(p / 100 * chars) + (chars-(int(p / 100 * chars)))*notdone
    return "[" + "=" * int(p / 100 * chars) + ">" + " " * (chars - int(p / 100 * chars) - 1) + "]"


def get_selected_indices(indexed_items: list[Tuple[int, list[str]]], selections: dict[int, bool]) -> list[int]:
    """ Return a list of indices which are True in the selections dictionary. """
    selected_indices = [x[0] for x in indexed_items if selections[x[0]]]
    return selected_indices

def get_selected_values(items: list[list[str]], indexed_items: list[Tuple[int, list[str]]], selections: dict[int, bool]) -> list[list[str]]:
    """ Return a list of rows based on wich are True in the selections dictionary. """
    selected_values = [items[x] for x in get_selected_indices(indexed_items, selections)]
    return selected_values

def format_size(n:int) -> str:
    """
    Convert bytes to a human-readable format. E.g., 8*1024*1024*3 -> 8MB
    
    Args:
        n (int): The number of bytes to convert.
        
    Returns:
        str: A string representing the bytes in a more human-readable form.
    """
    if n < 0:
        raise ValueError("Number must be non-negative")
    
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = {}
    for i, symbol in enumerate(symbols):
        prefix[symbol] = 1 << (i * 10)
        
    if n == 0:
        return "0B"
    
    symbol, value = "B", 0
    for symbol in reversed(symbols):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            break
    
    return f"{value:.1f}{symbol}"

