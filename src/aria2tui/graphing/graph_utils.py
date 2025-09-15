import curses
import re

def display_ansi(stdscr, ansi_lines, x=0, y=0, w=None, h=None, colour_pair_map={}, pair_offset=1, default_colours=(curses.COLOR_WHITE, curses.COLOR_BLACK)):
    max_pairs = 255 if hasattr(curses, 'COLOR_PAIRS') else 64

    colour_pair_map = {}
    next_pair_number = pair_offset

    def get_color_pair(fg, bg):
        nonlocal next_pair_number

        key = (fg, bg)
        if key in colour_pair_map:
            return curses.color_pair(colour_pair_map[key])

        if next_pair_number >= max_pairs:
            return curses.A_NORMAL  # fallback

        try:
            fg_c = fg if fg is not None else default_colours[0]
            bg_c = bg if bg is not None else default_colours[1]
            curses.init_pair(next_pair_number, fg_c, bg_c)
            colour_pair_map[key] = next_pair_number
            pair = curses.color_pair(next_pair_number)
            next_pair_number += 1
            return pair
        except curses.error:
            return curses.A_NORMAL

    # Set width/height defaults if not provided
    screen_h, screen_w = stdscr.getmaxyx()
    w = w if w is not None else screen_w - x
    h = h if h is not None else screen_h - y

    # Clip lines to available height
    visible_lines = ansi_lines[:h]

    for row_offset, line in enumerate(visible_lines):
        draw_y = y + row_offset
        draw_x = x
        x_offset = 0

        parsed = parse_ansi(line)
        for segment, fg, bg in parsed:
            segment = segment[:max(0, w - x_offset)]  # Clip segment width
            try:
                attr = get_color_pair(fg, bg)
                stdscr.addstr(draw_y, draw_x + x_offset, segment, attr)
            except curses.error:
                pass
            x_offset += len(segment)
            if x_offset >= w:
                break

def parse_ansi(text):
    """
    Parses ANSI escape sequences and returns a list of (text, fg, bg) tuples.
    Supports full SGR sequences including 8-bit foreground and background.
    """
    ansi_code_pat = re.compile(r'\033\[([0-9;]+)m')
    parts = []
    last_end = 0
    current_fg = None
    current_bg = None

    for match in ansi_code_pat.finditer(text):
        start, end = match.span()
        sgr_sequence = match.group(1)
        sgr_params = list(map(int, filter(None, sgr_sequence.split(';'))))

        # Append the text before the escape code
        if start > last_end:
            parts.append((text[last_end:start], current_fg, current_bg))

        # Parse the SGR codes
        i = 0
        while i < len(sgr_params):
            code = sgr_params[i]
            if code == 0:
                current_fg = None
                current_bg = None
                i += 1
            elif code == 38 and i + 2 < len(sgr_params) and sgr_params[i + 1] == 5:
                current_fg = sgr_params[i + 2]
                i += 3
            elif code == 48 and i + 2 < len(sgr_params) and sgr_params[i + 1] == 5:
                current_bg = sgr_params[i + 2]
                i += 3
            elif 30 <= code <= 37:
                current_fg = code - 30
                i += 1
            elif 40 <= code <= 47:
                current_bg = code - 40
                i += 1
            else:
                # Unsupported code — skip
                i += 1

        last_end = end

    if last_end < len(text):
        parts.append((text[last_end:], current_fg, current_bg))

    return parts
