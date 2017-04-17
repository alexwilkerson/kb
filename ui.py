import os
import sys
import getpass
import datetime
import threading
import time
import random
import signal
import curses
import curses.ascii
from curses import textpad

class UI:

    BAR_FG_COLOR = 107
    BAR_BG_COLOR = 24
    MESSAGE_COLOR = 26
    LINE_COLOR = 10

    def __init__(self, stdscr, s, chat_lock, title, user):

        curses.noecho()
        curses.cbreak()
        curses.curs_set(1)
        curses.use_default_colors()
        curses.start_color()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)

        stdscr.keypad(1)

        self.stdscr = stdscr
        self.s = s
        self.chat_lock = chat_lock
        self.rows, self.cols = stdscr.getmaxyx()

        self.title = title
        self.user = user

        self.userlist = ['alex', 'kimberly']
        self.chatbuffer = []

        title_hwyx = (1, self.cols, 0, 0)
        footer_hwyx = (1, self.cols, self.rows - 1, 0)
        chat_hwyx = (self.rows - 5, self.cols - 21, 1, 0)
        users_hwyx = (self.rows - 5, 18, 1, self.cols - 18)
        input_hwyx = (1, self.cols - 1 - 9, self.rows - 3, 9)

        self.title_win = curses.newwin(*title_hwyx)
        self.footer_win = curses.newwin(*footer_hwyx)
        self.chat_win = stdscr.derwin(*chat_hwyx)
        self.chat_win.scrollok(True)
        self.users_win = curses.newwin(*users_hwyx)
        self.input_win = curses.newwin(*input_hwyx)
        self.input_textbox = textpad.Textbox(self.input_win, insert_mode=True)
        self.input_textbox.stripspaces = 0

        self.redraw_ui()

    def redraw_ui(self):
        try:
            self.rows, self.cols = self.stdscr.getmaxyx()

            curses.init_pair(1, self.BAR_FG_COLOR, self.BAR_BG_COLOR)

            self.stdscr.clear()
            self.stdscr.attron(curses.color_pair(self.LINE_COLOR))
            self.stdscr.hline(self.rows - 4, 0, self._hline(), self.cols)
            self.stdscr.vline(2, self.cols - 20, self._vline(), self.rows - 6)
            self.stdscr.attroff(curses.color_pair(self.LINE_COLOR))
            self.stdscr.attron(curses.color_pair(self.MESSAGE_COLOR))
            self.stdscr.addstr(self.rows - 3, 0, "message:")
            self.stdscr.attroff(curses.color_pair(self.MESSAGE_COLOR))
            self.stdscr.refresh()

            self.redraw_title()
            self.redraw_footer()
            self.redraw_chat()
            self.redraw_users()
            self.redraw_input()
        except Exception as e:
            print("Error drawing UI " + str(e))

    def redraw_title(self):
        self.title_win.clear()
        self.title_win.resize(1, self.cols)
        self.title_win.bkgd(' ', curses.color_pair(1) + curses.A_BOLD)
        self.title_win.addstr(0, int((self.cols-len(self.title))/2), self.title)
        self.title_win.refresh()

    def redraw_footer(self):
        self.footer_win.clear()
        self.footer_win.resize(1, self.cols)
        self.footer_win.mvwin(self.rows - 1, 0)
        self.footer_win.bkgd(' ', curses.color_pair(1) + curses.A_BOLD)
        self.footer_win.addstr(' ' + self.user)
        self.footer_win.addstr(0, self.cols - 6, datetime.datetime.now().strftime('%H:%M'))
        self.footer_win.refresh()

    def update_chat(self):
        self.chat_win.clear()
        chat_rows, chat_cols = self.chat_win.getmaxyx()
        with self.chat_lock:
            for line in self.chatbuffer[-chat_rows:]:
                self.color_parse_addstr(self.chat_win, line)
        self.chat_win.refresh()

    def redraw_chat(self):
        self.chat_win.clear()
        self.chat_win.resize(self.rows - 5, self.cols - 21)
        chat_rows, chat_cols = self.chat_win.getmaxyx()
        with self.chat_lock:
            for line in self.chatbuffer[-chat_rows:]:
                self.color_parse_addstr(self.chat_win, line)
        self.chat_win.refresh()

    def redraw_users(self):
        self.users_win.erase()
        self.users_win.resize(self.rows - 5, 18)
        self.users_win.mvwin(1, self.cols - 18)
        self.color_parse_addstr(self.users_win, '\033[73musers: (' + str(len(self.userlist)) + ')\n')
        for u in self.userlist:
            self.users_win.addstr(u + '\n')
        self.users_win.refresh()

    def redraw_input(self):
        self.input_win.resize(1, self.cols - 1 - 9)
        self.input_win.mvwin(self.rows - 3, 9)
        # fixes resizing issue with textbox
        # self.input_textbox._update_maxyx()
        self.input_win.refresh()
        self.input_win.cursyncup()

    def color_parse_addstr(self, window, string):
        """
        This is a hacked together version of the color parser
        from the culour module.
        """
        # split but \033 which stands for a color change
        color_split = string.split('\033[')

        # Print the first part of the line without color change
        curses.init_pair(0, -1, -1)#curses.COLOR_WHITE, curses.COLOR_BLACK)
        window.addstr(color_split[0], curses.color_pair(0))

        # Iterate over the rest of the line-parts and print them with their colors
        bold = 0

        for substring in color_split[1:]:
            color_str = substring.split('m')[0]
            if color_str == '300': # TerminalColors.BOLD:
                bold = 1
                continue
            if color_str == '0':
                bold = 0
            substring = substring[len(color_str)+1:]
            if bold:
                window.addstr(substring, curses.color_pair(int(color_str)) + curses.A_BOLD)
            else:
                window.addstr(substring, curses.color_pair(int(color_str)))

    def input_loop(self):
        while True:
            out = self.input_textbox.edit(validate=self._validate)
            out = out.rstrip()
            if out == '':
                pass
            elif out == '.e':
                exit()
            elif out == '.r':
                self.random_theme()
            else:
                self.send_input(out)
            self.input_win.clear()
            self.input_win.cursyncup()

    def random_theme(self):
        self.BAR_FG_COLOR = random.randint(2,256)
        self.BAR_BG_COLOR = random.randint(2,256)
        self.MESSAGE_COLOR = random.randint(2,256)
        self.LINE_COLOR = random.randint(2,256)
        self.redraw_ui()

    def send_input(self, out):
        self.s.send(out.encode())
        # self.chatbuffer.append(out + '\n')
        with self.chat_lock:
            if len(self.chatbuffer) > self.rows:
                self.chatbuffer = self.chatbuffer[-self.rows:]
        # self.redraw_chat()

    def _validate(self, ch):
        # 10 is RETURN key
        if ch == 10:
            # curses.ascii.BEL is termination key for textboxes
            return curses.ascii.BEL
        # fix backspace for iterm
        if ch == curses.ascii.DEL:
            ch = curses.KEY_BACKSPACE
        return ch

    def _vline(self):
        return getattr(curses, 'ACS_VLINE', ord('|'))

    def _hline(self):
        return getattr(curses, 'ACS_HLINE', ord('-'))
