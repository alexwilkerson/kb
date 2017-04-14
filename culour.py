import os
import curses

COLOR_PAIRS_CACHE = {}

"""
To add a custom color, add a character command to the TerminalColors
class. Then add the name, and color code to the TERMINAL_COLOR_TO_CURSES array.
"""

class TerminalColors(object):
    MAGENTA = '[95'
    BLUE = '[94'
    GREEN = '[92'
    YELLOW = '[93'
    LIGHT_YELLOW = '[228'
    RED = '[91'
    PEACH = '[10'
    NICE_BLUE = '[26'
    END = '[0'


# Translates between the terminal notation of a color, to it's curses color number
TERMINAL_COLOR_TO_CURSES = {
    TerminalColors.RED: curses.COLOR_RED,
    TerminalColors.GREEN: curses.COLOR_GREEN,
    TerminalColors.YELLOW: curses.COLOR_YELLOW,
    TerminalColors.BLUE: curses.COLOR_BLUE,
    TerminalColors.MAGENTA: curses.COLOR_MAGENTA,
    TerminalColors.PEACH: 204,
    TerminalColors.LIGHT_YELLOW: 228,
    TerminalColors.NICE_BLUE: 26
}


def _get_color(fg, bg):
    key = (fg, bg)
    if key not in COLOR_PAIRS_CACHE:
        # Use the pairs from 101 and after, so there's less chance they'll be overwritten by the user
        pair_num = len(COLOR_PAIRS_CACHE) + 101
        curses.init_pair(pair_num, fg, bg)
        COLOR_PAIRS_CACHE[key] = pair_num

    return COLOR_PAIRS_CACHE[key]


def _color_str_to_color_pair(color):
    if color == TerminalColors.END:
        fg = -1#curses.COLOR_WHITE
    else:
        fg = TERMINAL_COLOR_TO_CURSES[color]
    color_pair = _get_color(fg, -1) # curses.COLOR_BLACK)
    return color_pair


def addstr(window, string):
    # split but \033 which stands for a color change
    color_split = string.split('\033')

    # Print the first part of the line without color change
    default_color_pair = _get_color(-1, -1)#curses.COLOR_WHITE, curses.COLOR_BLACK)
    window.addstr(color_split[0], curses.color_pair(default_color_pair))

    # Iterate over the rest of the line-parts and print them with their colors
    for substring in color_split[1:]:
        color_str = substring.split('m')[0]
        substring = substring[len(color_str)+1:]
        color_pair = _color_str_to_color_pair(color_str)
        window.addstr(substring, curses.color_pair(color_pair))

#  def _inner_addstr(window, string, y=-1, x=-1, nl=0):
#      assert curses.has_colors(), "Curses wasn't configured to support colors. Call curses.start_color()"

#      if nl == 1:
#          window.addstr('\n')
#      cur_y, cur_x = window.getyx()
#      if y == -1:
#          y = cur_y
#      if x == -1:
#          x = cur_x
#      for line in string.split(os.linesep):
#          _add_line(y, x, window, line)
#          # next line
#          y += 1


#  def addstr(window, string):
#      """
#      Adds the color-formatted string to the given window, in the given coordinates
#      To add in the current location, call like this:
#          addstr(window, string)
#      and to set the location to print the string, call with:
#          addstr(window, y, x, string)
#      Only use color pairs up to 100 when using this function,
#      otherwise you will overwrite the pairs used by this function
#      """

#      return _inner_addstr(window, string)
