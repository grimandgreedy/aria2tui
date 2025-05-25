import re

def filter_items(items, indexed_items, query):
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
            else:
                filters[-1] = token
                i += 1
        else:
            i += 1



    indexed_items = [(i, item) for i, item in enumerate(items) if apply_filter(item)]
    return indexed_items


    # after_count = len(indexed_items)
    # number_of_pages_after = (len(indexed_items) + items_per_page - 1) // items_per_page
    # cursor = (current_page * items_per_page) + current_row
    # if cursor > after_count:
    #     cursor = 0
    #     # current_row = 0
    #     current_page  = number_of_pages_after - 1
    #     current_row = (len(indexed_items) +items_per_page - 1) % items_per_page

    # draw_screen()
