#!/usr/bin/python3

import os, sys, getpass
import signal
import curses
import curses.ascii
from curses import wrapper, textpad

USER = getpass.getuser()

# ASCII CODES
ESCAPE = 27
RETURN = 10
SPACE = 32

def hline():
    return getattr(curses, 'ACS_HLINE', ord('-'))

def main(stdscr):

    # used to refresh the screen on resize
    chat_buffer = []

    # colors
    curses.start_color()
    #header
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    #message
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    os.environ['ESCDELAY'] = '25'

    # set terminal title
    if os.getenv('DISPLAY'):
        title = 'keybeard alpha'
        sys.stdout.write('\x1b]2;{0}\x07'.format(title))
        sys.stdout.flush()

    curses.noecho()
    curses.cbreak()
    curses.use_default_colors()

    stdscr.clear()
    stdscr.keypad(1)

    maxy, maxx = stdscr.getmaxyx()

    # header bar
    header = stdscr.subwin(1, maxx, 0, 0)
    header.erase()
    header.bkgd(SPACE, curses.color_pair(1) + curses.A_BOLD)
    header.addstr('keybeard alpha')
    header.refresh()

    # lines, cols, y, x
    # main chat window
    chat_win = stdscr.subwin(maxy - 5, maxx - 1, 1, 0)
    chat_win.scrollok(1)

    message_border = stdscr.subwin(1, maxx, maxy - 4, 0)
    message_border.erase()
    message_border.border(' ',' ',' ',hline(),' ',' ',' ',' ');
    message_border.refresh()

    # just the left corner where it says messages
    message_prompt = stdscr.subwin(1, 9, maxy - 3, 0)
    message_prompt.addstr("message:")

    # the input field
    message_input = stdscr.subwin(1, maxx - 1 - 9, maxy - 3, 9)
    curses.curs_set(1)
    textbox = textpad.Textbox(message_input)
    textbox.stripspaces = 0

    footer = stdscr.subwin(1, maxx, maxy - 1, 0)
    footer.erase()
    footer.bkgd(SPACE, curses.color_pair(1) + curses.A_BOLD)
    footer.addstr(USER)
    footer.refresh()

    stdscr.refresh()

    def validate(ch):
        if ch == RETURN:
            return 7
        # fix backspace for iterm
        if ch == curses.ascii.DEL:
            ch = curses.KEY_BACKSPACE
        #  if ch == curses.KEY_REFRESH:
        #      chat_win.addstr("WORKING")
        #      maxy, maxx = stdscr.getmaxyx()
        #      stdscr.clear()

        #      chat_win.resize(maxy - 20, maxx - 1)
        #      chat_win.mvwin(0, 0)

        #      message_prompt.resize(1, 10)
        #      message_prompt.mvwin(maxy - 3, 0)

        #      message_input.resize(1, maxx - 1 - 11)
        #      message_input.resize(maxy - 3, 10)

        #      stdscr.refresh()
        #      curses.doupdate()
        return ch

    def resize_handler(signum, frame):
        try:
            curses.endwin()
            curses.initscr()
            maxy, maxx = stdscr.getmaxyx()
            stdscr.clear()

            header.resize(1, maxx)
            header.erase()
            header.addstr('keybeard alpha')
            header.refresh()

            chat_win.clear()
            chat_win.resize(maxy - 5, maxx - 1)
            chat_win.mvwin(1, 0)
            chaty, chatx = chat_win.getmaxyx()
            for line in chat_buffer[-chaty:]:
                chat_win.addstr(line)
            chat_win.refresh()

            message_border = stdscr.subwin(1, maxx, maxy - 4, 0)
            message_border.erase()
            message_border.border(' ',' ',' ',hline(),' ',' ',' ',' ');
            message_border.refresh()

            footer = stdscr.subwin(1, maxx, maxy - 1, 0)
            footer.erase()
            footer.bkgd(SPACE, curses.color_pair(1) + curses.A_BOLD)
            footer.addstr(USER)
            footer.refresh()

            message_prompt = stdscr.subwin(1, 9, maxy - 3, 0)
            message_prompt.clear()
            message_prompt.addstr("message:")
            message_prompt.refresh()

            message_input.resize(1, maxx - 1 - 9)
            message_input.mvwin(maxy - 3, 9)

            stdscr.refresh()
        except:
            print("Resize error occurred.")

    signal.signal(signal.SIGWINCH, resize_handler)

    while True:
        out = textbox.edit(validate=validate)
        out = out.strip()
        if out == '':
            message_input.clear()
        elif out == '!exit':
            exit()
        else:
            out = out + '\n'
            chat_win.addstr(out)
            chat_buffer.append(out)
            message_input.clear()
            chat_win.refresh()

wrapper(main)
