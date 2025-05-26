import re

def search(query, indexed_items, highlights=[], cursor_pos=0, unselectable_indices=[], reverse=False, continue_search=False):
    """
    ---Returns:
        return_val, cursor_pos, search_index: 
        return_val:
                    True: search item found
        cursor_pos: the position of the next search item
        search_index: the index of the search match out of all the matches
        search_count: the number of matches

    """
    
    # Clear previous search highlights

    highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]

    def apply_filter(row):
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

    filters = {}
    invert_filter = False
    case_sensitive = False

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

    before_count = len(indexed_items)

    # for i in list(range(current_row+(current_page*items_per_page)+1, len(indexed_items))) + list(range(current_row+(current_page*items_per_page)+1)):
    searchables =  list(range(cursor_pos+1, len(indexed_items))) + list(range(cursor_pos+1))
    if reverse:
        searchables =  (list(range(cursor_pos, len(indexed_items))) + list(range(cursor_pos)))[::-1]
    # search_indices = list(range(old_pos+1, len(indexed_items))) + list(range(old_pos+1, len(indexed_items)))
    # for i in list(range(old_pos+1, len(indexed_items))):
    # os.system(f"notify-send '{len(indexed_items)}'")
    found = False
    search_count = 0
    search_list = []
    
    for i in searchables:
        # if apply_filter(indexed_items[i][1]):
        if apply_filter(indexed_items[i][1]):
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


    # number_of_pages_before = (len(indexed_items) + items_per_page - 1) // items_per_page
    # indexed_items = [(i, item) for i, item in enumerate(items) if apply_filter(item)]
    # after_count = len(indexed_items)
    # number_of_pages_after = (len(indexed_items) + items_per_page - 1) // items_per_page
    # cursor = (current_page * items_per_page) + current_row
    # if cursor > after_count:
    #     cursor = 0
    #     # current_row = 0
    #     current_page  = number_of_pages_after - 1
    #     current_row = (len(indexed_items) +items_per_page - 1) % items_per_page

    # draw_screen()
