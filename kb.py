#!/usr/bin/python3

import os, sys, getpass
import datetime
import threading
import time
import signal
import curses
import curses.ascii
import culour
from curses import wrapper, textpad

lock = threading.Lock()

BAR_FG = 8
BAR_BG = 102

TITLE = 'keybeard alpha'
USER = getpass.getuser()
# used to refresh the screen on resize

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

def test_thread(chat_win, message_input, chat_buffer):
    while True:
        with lock:
            add_line(chat_win, "testing working.\n", chat_buffer)
            message_input.refresh()
        time.sleep(1)

def clock(footer, message_input, stdscr):
    while True:
        maxy, maxx = stdscr.getmaxyx()
        with lock:
            footer.clear()
            rows, cols = footer.getmaxyx()
            footer.addstr(' ' + USER)
            footer.addstr(0, cols - 6, datetime.datetime.now().strftime("%H:%M"))
            footer.refresh()
            message_input.refresh()
        time.sleep(1)

def add_line(chat_win, string, chat_buffer):
    chat_win.erase()
    chat_buffer.append(string)
    cols, rows = chat_win.getmaxyx()
    for line in chat_buffer[-rows + 1:]:
        culour.addstr(chat_win, line)
    chat_win.refresh()

def main(stdscr):

    chat_buffer = []

    # colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1)
    #header
    curses.init_pair(1, BAR_FG, BAR_BG)
    #message
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)

    os.environ['ESCDELAY'] = '25'

    # set terminal title
    if os.getenv('DISPLAY'):
        sys.stdout.write('\x1b]2;{0}\x07'.format(TITLE))
        sys.stdout.flush()

    curses.noecho()
    curses.cbreak()

    stdscr.clear()
    stdscr.keypad(1)

    maxy, maxx = stdscr.getmaxyx()

    # lines, cols, y, x
    # main chat window
    chat_win = stdscr.subwin(maxy - 5, maxx - 21, 1, 0)
    chat_win.scrollok(1)

    user_win = curses.newwin(maxy - 5, 18, 1, maxx - 18)
    culour.addstr(user_win, '\033[73musers online: (2)\n')
    # user_win.addstr('users online:\n')
    user_win.addstr('testuser\n')
    user_win.addstr(USER)

    # the input field
    message_input = curses.newwin(1, maxx - 1 - 9, maxy - 3, 9)
    curses.curs_set(1)
    textbox = textpad.Textbox(message_input)
    textbox.stripspaces = 0

    # header bar
    header = curses.newwin(1, maxx, 0, 0)
    header.erase()
    header.bkgd(SPACE, curses.color_pair(1) + curses.A_BOLD)
    header.addstr(0, int((maxx-len(TITLE))/2), TITLE)

    footer = curses.newwin(1, maxx, maxy - 1, 0)
    footer.erase()
    footer.bkgd(SPACE, curses.color_pair(1) + curses.A_BOLD)

    stdscr.attron(curses.color_pair(73))
    stdscr.hline(maxy - 4, 0, hline(), maxx)
    stdscr.vline(2, maxx - 20, vline(), maxy - 6)
    stdscr.attron(curses.color_pair(73))
    stdscr.addstr(maxy - 3, 0, "message:", curses.color_pair(73))

    stdscr.refresh()
    message_input.refresh()
    user_win.refresh()
    header.touchwin()
    header.refresh()
    footer.refresh()
    curses.doupdate()

    def validate(ch):
        if ch == RETURN:
            # curses.ascii.BEL is termination key for textboxes
            return curses.ascii.BEL
        # fix backspace for iterm
        if ch == curses.ascii.DEL:
            ch = curses.KEY_BACKSPACE
        return ch

    def resize_handler(signum, frame):
        try:
            curses.endwin()
            curses.initscr()
            maxy, maxx = stdscr.getmaxyx()
            stdscr.erase()

            header.resize(1, maxx)
            header.clear()
            header.addstr(0, int((maxx-len(TITLE))/2), TITLE)
            header.noutrefresh()

            chat_win.clear()
            chat_win.resize(maxy - 5, maxx - 21)
            #  chat_win.resize(maxy - 5, maxx - 21)
            # chat_win.mvwin(1, 0)
            chaty, chatx = chat_win.getmaxyx()
            for line in chat_buffer[-chaty:]:
                # chat_win.addstr(line)
                culour.addstr(chat_win, line)
            chat_win.noutrefresh()

            #  user_border = stdscr.subwin(maxy - 4, 1, 1, maxx - 20)
            #  user_border.erase()
            #  user_border.border(' ',vline(),' ',' ',' ',' ',' ',' ');
            #  user_border.refresh()

            # user_win = stdscr.subwin(maxy - 5, 18, 1, maxx - 18)
            # user_win.clear()
            user_win.resize(maxy - 5, 18)
            user_win.mvwin(1, maxx - 18)
            #  culour.addstr(user_win, '\033[228musers online: (2)\n')
            #  user_win.addstr('testuser\n')
            #  user_win.addstr(USER)
            user_win.noutrefresh()

            #  message_border = stdscr.subwin(1, maxx, maxy - 4, 0)
            #  message_border.erase()
            #  message_border.border(' ',' ',' ',hline(),' ',' ',' ',' ');
            #  message_border.refresh()

            # footer = stdscr.subwin(1, maxx, maxy - 1, 0)
            #  footer.clear()
            #  footer.bkgd(SPACE, curses.color_pair(1) + curses.A_BOLD)
            #  footer.addstr(USER)
            footer.resize(1, maxx)
            footer.mvwin(maxy - 1, 0)

            #  stdscr.vline(2, maxx - 20, vline(), maxy - 6)
            #  stdscr.hline(maxy - 4, 0, hline(), maxx)
            #  stdscr.addstr(maxy - 3, 0, "message:", curses.color_pair(219))
            stdscr.attron(curses.color_pair(73))
            stdscr.hline(maxy - 4, 0, hline(), maxx)
            stdscr.vline(2, maxx - 20, vline(), maxy - 6)
            stdscr.attron(curses.color_pair(73))
            stdscr.addstr(maxy - 3, 0, "message:", curses.color_pair(73))

            # message_input.erase()
            message_input.resize(1, maxx - 1 - 9)
            message_input.mvwin(maxy - 3, 9)
            # fixes resizing issue with textbox
            textbox._update_max_yx()
            # refresh textbox
            # textbox.do_command(curses.ascii.FF)

            stdscr.touchwin()
            stdscr.refresh()
            user_win.touchwin()
            user_win.refresh()
            message_input.touchwin()
            message_input.refresh()
            header.touchwin()
            header.refresh()
            footer.touchwin()
            footer.refresh()
            curses.doupdate()

        except:
            print("Resize error occurred.")

    signal.signal(signal.SIGWINCH, resize_handler)

    t = threading.Thread(target=test_thread, args=(chat_win,message_input,chat_buffer))
    t.daemon = True
    t.start()

    c = threading.Thread(target=clock, args=(footer,message_input,stdscr))
    c.daemon = True
    c.start()

    while True:
        out = textbox.edit(validate=validate)
        out = out.strip()
        if out == '':
            message_input.clear()
        elif out == '!exit':
            exit()
        else:
            # 300 is bold
            out = thetime() + " \033[300m\033[57m" + USER + ":\033[0m " + out + '\n'
            add_line(chat_win, out, chat_buffer)
            message_input.clear()

wrapper(main)
