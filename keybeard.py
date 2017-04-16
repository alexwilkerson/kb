import os
import signal
import getpass
import curses
from time import sleep
from curses import wrapper
from ui import UI

def main(stdscr):
    stdscr.clear()
    title = 'keybeard alpha'
    user = getpass.getuser()

    ui = UI(stdscr, title, user)

    def resize_handler(signum, frame):
        curses.endwin()
        curses.initscr()
        ui.redraw_ui()
    signal.signal(signal.SIGWINCH, resize_handler)

    ui.input_loop()

wrapper(main)
