import re
from typing import Tuple

def filter_items(items: list[list[str]], indexed_items: list[Tuple[int, list[str]]], query: str) -> list[Tuple[int, list[str]]]:
    """ 
    Filter items based on the query.

    Accepts:
        regular expressions
        --# to specify column to match
        --i to specify case-sensitivity (it is case insensitive by default)
        --v to specify inverse match

    E.g.,

        --1 query       matches query in the 1 column


    Returns indexed_items, which is a list of tuples; each tuple consists of the index and the data of the matching row in the original items list. 
    """

    def apply_filter(row: list[str], filters: dict) -> bool:
        """ Checks if row matches the filter. """
        for col, value in filters.items():
            if case_sensitive or (value != value.lower()):
                pattern = re.compile(value)
            else:
                pattern = re.compile(value, re.IGNORECASE)
            if col == -1:  # Apply filter to all columns
                if not any(pattern.search(str(item)) for item in row):
                    return invert_filter
                # return not invert_filter
            elif col >= len(row) or col < 0:
                return False
            else:
                cell_value = str(row[col])
                if not pattern.search(str(cell_value)):
                    return invert_filter
                # return invert_filter

        return True

    def tokenize(query:str) -> dict:
        """ Convert query into dict consisting of filters. """
        filters = {}

        # tokens = re.split(r'(\s+--\d+|\s+--i)', query)
        tokens = re.split(r'((\s+|^)--\w)', query)
        tokens = [token.strip() for token in tokens if token.strip()]  # Remove empty tokens
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token:
                if token.startswith("--"):
                    flag = token
                    if flag == '--v':
                        invert_filter = True 
                        i += 1
                    elif flag == '--i':
                        case_sensitive = True
                        i += 1
                    else:
                        if i+1 >= len(tokens):
                            print("Not enough args")
                            break
                        col = int(flag[2:])
                        arg = tokens[i+1].strip()
                        filters[col] = arg
                        i+=2
                else:
                    filters[-1] = token
                    i += 1
            else:
                i += 1
        return filters

    invert_filter = False
    case_sensitive = False

    filters = tokenize(query)

    indexed_items = [(i, item) for i, item in enumerate(items) if apply_filter(item, filters)]
    return indexed_items
