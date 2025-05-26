
from wcwidth import wcwidth, wcswidth
from math import log10

def truncate_to_display_width(text, max_width):
    result = ''
    width = 0
    for char in text:
        w = wcwidth(char)
        if w < 0:
            continue
        if width + w > max_width:
            break
        result += char
        width += w
    # Pad if it's shorter
    padding = max_width - wcswidth(result)
    # return result + ' ' * padding
    return result + ' ' * padding


def format_row_full(row, hidden_columns):
    return '\t'.join(str(row[i]) for i in range(len(row)) if i not in hidden_columns)


def format_row(row, hidden_columns, column_widths, separator):
    row_str = ""
    for i, cell in enumerate(row):
        if i in hidden_columns: continue
        val = truncate_to_display_width(cell, column_widths[i])
        row_str += val + separator
    return row_str.strip()

def get_column_widths(items, header=[], max_width=70, number_columns=True):

    # Calculate maximum width of each column with clipping
    # widths = [max(len(str(row[i])) for row in items) for i in range(len(items[0]))]
    widths = [max(wcswidth(str(row[i])) for row in items) for i in range(len(items[0]))]
    if header:
        # header_widths = [len(str(h))+int(log10(i+1))+3 for i, h in enumerate(header)]
        header_widths = [wcswidth(str(h))+int(log10(i+1))+3*int(number_columns) for i, h in enumerate(header)]
        return [min(max_width, max(widths[i], header_widths[i])) for i in range(len(header))]
    return [min(max_width, width) for width in widths]

def get_mode_widths(item_list):
    widths = [wcswidth(str(row)) for row in item_list]
    return widths

def intStringToExponentString(n):
    n = str(n)
    digitdict = { "0" : "⁰", "1" : "¹", "2" : "²", "3" : "³", "4" : "⁴", "5" : "⁵", "6" : "⁶", "7" : "⁷", "8" : "⁸", "9" : "⁹"}
    return "".join([digitdict[char] for char in n])
