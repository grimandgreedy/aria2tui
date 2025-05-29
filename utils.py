
from wcwidth import wcwidth, wcswidth
from math import log10

def truncate_to_display_width(text, max_column_width):
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
    return result + ' ' * padding


def format_row_full(row, hidden_columns):
    return '\t'.join(str(row[i]) for i in range(len(row)) if i not in hidden_columns)

def format_full_row(row):
    return '\t'.join(row)


def format_row(row, hidden_columns, column_widths, separator):
    row_str = ""
    for i, cell in enumerate(row):
        if i in hidden_columns: continue
        val = truncate_to_display_width(str(cell), column_widths[i])
        row_str += val + separator
    return row_str
    # return row_str.strip()

def get_column_widths(items, header=[], max_column_width=70, number_columns=True):

    # Calculate maximum width of each column with clipping
    # widths = [max(len(str(row[i])) for row in items) for i in range(len(items[0]))]
    widths = [max(wcswidth(str(row[i])) for row in items) for i in range(len(items[0]))]
    if header:
        # header_widths = [len(str(h))+int(log10(i+1))+3 for i, h in enumerate(header)]
        header_widths = [wcswidth(str(h))+int(log10(i+1))+3*int(number_columns) for i, h in enumerate(header)]
        return [min(max_column_width, max(widths[i], header_widths[i])) for i in range(len(header))]
    return [min(max_column_width, width) for width in widths]

def get_mode_widths(item_list):
    widths = [wcswidth(str(row)) for row in item_list]
    return widths

def intStringToExponentString(n):
    n = str(n)
    digitdict = { "0" : "⁰", "1" : "¹", "2" : "²", "3" : "³", "4" : "⁴", "5" : "⁵", "6" : "⁶", "7" : "⁷", "8" : "⁸", "9" : "⁹"}
    return "".join([digitdict[char] for char in n])

def convert_seconds(seconds, long_format=False):
    # Ensure the input is an integer
    if isinstance(seconds, str):
        seconds = int(seconds)

    # Calculate years, days, hours, minutes, and seconds
    years = seconds // (365 * 24 * 3600)
    days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    # Build the human-readable format
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
        # Compact format: using abbreviated units
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

def convert_percentage_to_ascii_bar(p, chars=8):
    # Convert percentage to an ascii status bar

    done = "█"
    notdone = "▒"
    return done * int(p / 100 * chars) + (chars-(int(p / 100 * chars)))*notdone
    return "[" + "=" * int(p / 100 * chars) + ">" + " " * (chars - int(p / 100 * chars) - 1) + "]"


def get_selected_indices(indexed_items, selections):
    selected_indices = [x[0] for x in indexed_items if selections[x[0]]]
    return selected_indices

def get_selected_values(items, indexed_items, selections):
    selected_values = [items[x][0] for x in get_selected_indices(indexed_items, selections)]
    return selected_values

def format_size(size_bytes):
    if size_bytes == 0:
        return "0.0 MB"
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_mb / 1024
    if size_gb >= 1:
        return f"{size_gb:.1f} GB"
    return f"{size_mb:.1f} MB"
