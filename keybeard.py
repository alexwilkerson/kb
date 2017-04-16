import getpass
import curses
from curses import wrapper
from ui import UI

def main(stdscr):
    stdscr.clear()
    title = 'keybeard alpha'
    user = getpass.getuser()

    ui = UI(stdscr, title, user)

    stdscr.getch()

wrapper(main)
