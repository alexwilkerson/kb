#!/usr/bin/env python3

import curses
import signal
from curses import wrapper
from curses.textpad import Textbox

def enter_is_terminate(x):
    if x == 10:
        return 7
    return x

def main(stdscr):
    stdscr.clear()
    curses.cbreak()

    maxy, maxx = stdscr.getmaxyx()

    # lines, cols, y, x
    chat_border = curses.newwin(maxy - 2, maxx - 1, 0, 0)
    chat_border.border()
    # chat_border.scrollok(True)

    chaty, chatx = chat_border.getmaxyx()
    main_chat = chat_border.subwin(chaty - 1, chatx - 4, 1, 1)
    main_chat.scrollok(True)

    message_win = curses.newwin(1, 10, maxy - 2, 1)
    message_win.addstr("message:")

    text_input = curses.newwin(2, maxx - 11, maxy - 2, 10)
    text_input.keypad(True)
    tb = Textbox(text_input)

    """ RESIZE HANDLING """
    def resize_handler(signum, frame):
        #  chat_border.addstr("resized\n")
        main_chat.refresh()
        chat_border.refresh()
        stdscr.refresh()

    signal.signal(signal.SIGWINCH, resize_handler)
    """ END RESIZE HANDLING """

    chat_border.refresh()
    main_chat.refresh()
    message_win.refresh()
    # text_input.refresh() THIS BREAKS THE EDITOR

    while True:
        word = tb.edit(enter_is_terminate)
        word = word.rstrip('\n').strip()
        if word == "!exit":
            exit()
        else:
            word = word + "\n"
            main_chat.addstr(word)
            text_input.clear()
            chat_border.refresh()
            main_chat.refresh()

wrapper(main)
