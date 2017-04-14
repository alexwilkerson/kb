#!/usr/bin/python3

import os, sys, getpass
import datetime
import signal
import curses
import curses.ascii
import culour
from curses import wrapper, textpad

USER = getpass.getuser()

# ASCII CODES
ESCAPE = 27
RETURN = 10
SPACE = 32

def send_to_chat(window, buf, msg):
    window.addstr(thetime() + ' ')
    buf.append(thetime() + ' ')

def thetime():
    return datetime.datetime.now().strftime("[%H:%M:%S]");

def vline():
    return getattr(curses, 'ACS_VLINE', ord('|'))

def hline():
    return getattr(curses, 'ACS_HLINE', ord('-'))

def main(stdscr):

    # used to refresh the screen on resize
    chat_buffer = []


    # colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    #header
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    #message
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)

    os.environ['ESCDELAY'] = '25'

    # set terminal title
    if os.getenv('DISPLAY'):
        title = 'keybeard alpha'
        sys.stdout.write('\x1b]2;{0}\x07'.format(title))
        sys.stdout.flush()

    curses.noecho()
    curses.cbreak()

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
    chat_win = stdscr.subwin(maxy - 5, maxx - 21, 1, 0)
    chat_win.scrollok(1)

    user_border = stdscr.subwin(maxy - 4, 1, 1, maxx - 20)
    user_border.erase()
    user_border.border(' ',vline(),' ',' ',' ',' ',' ',' ');
    user_border.refresh()

    user_win = stdscr.subwin(maxy - 5, 18, 1, maxx - 18)
    culour.addstr(user_win, '\033[228musers online: (2)\n')
    # user_win.addstr('users online:\n')
    user_win.addstr('testuser\n')
    user_win.addstr(USER)

    message_border = stdscr.subwin(1, maxx, maxy - 4, 0)
    message_border.erase()
    message_border.border(' ',' ',' ',hline(),' ',' ',' ',' ');
    message_border.refresh()

    # just the left corner where it says messages
    message_prompt = stdscr.subwin(1, 9, maxy - 3, 0)
    culour.addstr(message_prompt, "\033[11mmessage:")
    # message_prompt.addstr("message:", curses.color_pair(204))

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
        #try:
            curses.endwin()
            curses.initscr()
            maxy, maxx = stdscr.getmaxyx()
            stdscr.erase()

            header.resize(1, maxx)
            header.erase()
            header.addstr('keybeard alpha')
            header.refresh()

            chat_win.clear()
            chat_win.resize(maxy - 5, maxx - 21)
            chat_win.mvwin(1, 0)
            chaty, chatx = chat_win.getmaxyx()
            for line in chat_buffer[-chaty:]:
                # chat_win.addstr(line)
                culour.addstr(chat_win, line)
            chat_win.refresh()

            user_border = stdscr.subwin(maxy - 4, 1, 1, maxx - 20)
            user_border.erase()
            user_border.border(' ',vline(),' ',' ',' ',' ',' ',' ');
            user_border.refresh()

            user_win = stdscr.subwin(maxy - 5, 18, 1, maxx - 18)
            culour.addstr(user_win, '\033[228musers online: (2)\n')
            # user_win.addstr('users online:\n')
            user_win.addstr('testuser\n')
            user_win.addstr(USER)
            user_win.refresh()

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
            culour.addstr(message_prompt, "\033[11mmessage:")
            message_prompt.refresh()

            message_input.erase()
            message_input.resize(1, maxx - 1 - 9)
            message_input.mvwin(maxy - 3, 9)

            stdscr.refresh()
        #  except:
        #      print("Resize error occurred.")

    signal.signal(signal.SIGWINCH, resize_handler)

    while True:
        out = textbox.edit(validate=validate)
        out = out.strip()
        if out == '':
            message_input.clear()
        elif out == '!exit':
            exit()
        else:
            out = thetime() + " \033[10m\033[26m" + USER + ":\033[0m " + out + '\n'
            culour.addstr(chat_win, out)
            # chat_win.addstr(out)
            chat_buffer.append(out)
            message_input.clear()
            chat_win.refresh()

wrapper(main)
