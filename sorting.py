import re
from datetime import datetime

def parse_numerical(value):
    try:
        match = re.search(r'(\d+(\.\d+)?)', value)
        if match:
            return float(match.group(1))
        return float('inf')  # Default for non-numerical values
    except ValueError:
        return float('inf')

# Helper function to parse human-readable sizes
def parse_size(value):
    size_units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'PB': 1024**5,
        'K': 1024,
        'M': 1024**2,
        'G': 1024**3,
        'T': 1024**4,
        'P': 1024**5
    }
    
    match = re.search(r'(\d+(\.\d+)?)(\s*([KMGTPEB][B]?)\s*)', value, re.IGNORECASE)
    
    if match:
        number = float(match.group(1))
        unit = match.group(4).upper() if match.group(4) else 'B'
        unit = re.sub(r'[^\w]', '', unit)  # Remove non-alphanumeric characters
        return number * size_units.get(unit, 1)
    return float('inf')  # Default for non-size values

def time_to_seconds(time_str):
    """Convert a time string to total seconds."""
    if time_str.strip().upper() == "INF":
        return float('inf')  # Assign infinity for "INF"

    time_units = {
        'year': 365 * 24 * 3600,
        'years': 365 * 24 * 3600,
        'day': 24 * 3600,
        'days': 24 * 3600,
        'hour': 3600,
        'hours': 3600,
        'minute': 60,
        'minutes': 60,
        'sec': 1,
        'secs': 1,
        's': 1,
        'min': 60,
    }
    
    total_seconds = 0
    try:
        tokens = time_str.split()
        for i in range(0, len(tokens), 2):
            if i + 1 < len(tokens):
                num = int(tokens[i])
                unit = tokens[i + 1]
                total_seconds += num * time_units.get(unit, 0)
    except:
        return float('inf')


    return total_seconds

def time_sort(time_str):
    formats = [
        "%Y-%m-%d %H:%M",     # "2021-03-16 15:30"
        "%Y-%m-%d",           # "2021-03-16"
        "%Y/%m/%d",           # "2021/03/16"
        "%d/%m/%Y",           # "05/03/2024"
        "%A %d %b %Y %H:%M:%S",  # "Saturday 01 Feb 2025 21:19:47"
        "%a %d %b %Y %H:%M:%S",  # "Sat 01 Feb 2025 21:19:47"
        "%d/%m/%Y",           # "10/12/2023"
        "%d/%m/%y",            # "1/1/23"
        "%H:%M",               # "04:30"
        "%H:%M:%S",               # "04:30:23"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            pass
    
    return datetime.strptime("00:00", "%H:%M")

def sort_items(indexed_items, sort_method=0, sort_column=0, sort_reverse=False):
    SORT_METHODS = ['original', 'lexical', 'LEXICAL', 'alphanum', 'ALPHANUM', 'time', 'numerical', 'size']
    if sort_column is not None:
        try:
            if SORT_METHODS[sort_method] == 'numerical':
                indexed_items.sort(key=lambda x: parse_numerical(x[1][sort_column]), reverse=sort_reverse)
            elif SORT_METHODS[sort_method] == 'original':
                indexed_items.sort(key=lambda x: x[0], reverse=sort_reverse)
            elif SORT_METHODS[sort_method] == 'lexical':
                # indexed_items.sort(key=lambda x: x[1][sort_column].lower(), reverse=sort_reverse)
                indexed_items.sort(key=lambda x: (1 if x[1][sort_column].strip() == "" else 0, x[1][sort_column].lower()), reverse=sort_reverse)
            elif SORT_METHODS[sort_method] == 'LEXICAL':
                indexed_items.sort(key=lambda x: (1 if x[1][sort_column].strip() == "" else 0, x[1][sort_column]), reverse=sort_reverse)
            elif SORT_METHODS[sort_method] == 'alphanum':
                indexed_items.sort(key=lambda x: (1 if x[1][sort_column].strip() == "" else 0, "".join([chr(ord('z')+ord(c)) if not c.isalnum() else c.lower() for c in x[1][sort_column]])))
            elif SORT_METHODS[sort_method] == 'time':
                indexed_items.sort(key=lambda x:time_sort(x[1][sort_column]))
            elif SORT_METHODS[sort_method] == 'ALPHANUM':
                indexed_items.sort(key=lambda x: (1 if x[1][sort_column].strip() == "" else 0, "".join([chr(ord('z')+ord(c)) if not c.isalnum() else c for c in x[1][sort_column]])))
            elif SORT_METHODS[sort_method] == 'size':
                indexed_items.sort(key=lambda x: parse_size(x[1][sort_column]), reverse=sort_reverse)
        except IndexError:
            pass  # Handle cases where sort_column is out of range
