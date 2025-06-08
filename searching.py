import re
from typing import Tuple

def search(query: str, indexed_items: list[Tuple[int, list[str]]], highlights: list[dict]=[], cursor_pos:int=0, unselectable_indices:list=[], reverse:bool=False, continue_search:bool=False) -> Tuple[bool, int, int, int, list[dict]]:
    """
    Search the indexed items and see which rows match the query.

    Accepts:
        regular expressions
        --# to specify column to match
        --i to specify case-sensitivity (it is case insensitive by default)
        --v to specify inverse match

    ---Returns: a tuple consisting of the following
        return_val:     True if search item found
        cursor_pos:     The position of the next search match
        search_index:   If there are x matches then search_index tells us we are on the nth out of x
        search_count:   The number of matches
        highlights:     Adds the search highlights to the existing highlights list 
                            I.e.,, we append the following to the highlights list to be displayed in draw_screen
                            {
                                "match": token,
                                "field": "all",
                                "color": 10,
                                "type": "search",
                            }

    """
    
    # Clear previous search highlights

    highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]

    def apply_filter(row: list[str], filters: dict) -> bool:
        """ Checks if row matches the search. """
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
                        highlights.append({
                            "match": arg,
                            "field": col,
                            "color": 10,
                            "type": "search",
                        })
                else:
                    filters[-1] = token
                    highlights.append({
                        "match": token,
                        "field": "all",
                        "color": 10,
                        "type": "search",
                    })
                    i += 1
            else:
                i += 1
        return filters



    # Ensure we are searching from our current position forwards
    searchables =  list(range(cursor_pos+1, len(indexed_items))) + list(range(cursor_pos+1))
    if reverse:
        searchables =  (list(range(cursor_pos, len(indexed_items))) + list(range(cursor_pos)))[::-1]

    invert_filter = False
    case_sensitive = False
    filters = tokenize(query)

    found = False
    search_count = 0
    search_list = []
    
    for i in searchables:
        # if apply_filter(indexed_items[i][1]):
        if apply_filter(indexed_items[i][1], filters):
            new_pos = i
            if new_pos in unselectable_indices: continue
            search_count += 1
            search_list.append(i)
            
            if not found:
                cursor_pos = new_pos
                found = True
            # break
            # return False
            # for i in range(diff):
            #     cursor_down()
            # break
    if search_list:
        search_index = sorted(search_list).index(cursor_pos)+1
    else:
        search_index = 0

    return bool(search_list), cursor_pos, search_index, search_count, highlights

