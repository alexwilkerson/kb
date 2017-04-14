import curses
import signal
import curses.ascii
from curses import wrapper, textpad

class Terminal():

    MIN_HEIGHT = 10
    MIN_WIDTH = 20

    # ASCII code
    ESCAPE = 27
    RETURN = 10
    SPACE = 32

    def __init__(self, stdscr):

        self.stdscr = stdscr

    @property
    def vline(self):
        return getattr(curses, 'ACS_VLINE', ord('|'))

    @property
    def hline(self):
        return getattr(curses, 'ACS_HLINE', ord('-'))

    @staticmethod
    def flash():
        """
        Flash the screen to indicate that an action was invalid.
        """
        return curses.flash()

    @staticmethod
    def curs_set(val):
        """
        Change the cursor visibility, may fail for some terminals with limited
        cursor support.
        """
        try:
            curses.curs_set(val)
        except:
            pass

    def getch(self)
        """
        Wait for a keypress and return the corresponding character code (int).
        """
        return self.stdscr.getch()

    def cmdline(self, window):
        window.clear()

        self.curs_set(1)

        textbox = textpad.Textbox(window)
        textbox.stripspaces = 0

        def validate(ch):
            if ch == self.ESCAPE:
                raise exceptions.EscapeInterrupt()
            if ch == curses.ascii.DEL:
                ch = curses.KEY_BACKSPACE
            return ch

    @staticmethod
    def strip_textpad(text):
        """
        Attempt to intelligently strip excess whitespace from the output of a
        curses textpad.
        """

        if text is None:
            return text

        # Trivial case where the textbox is only one line long.
        if '\n' not in text:
            return text.rstrip()

        # allow one space at the end of the line. If there is more than one
        # space, assume that a newline operation was intended by the user

        stack, current_line = [], ''
        for line in text.split('\n'):
            if line.endswith('  ') or not line:
                stack.append(current_line + line.rstrip())
                current_line = ''
            else:
                current_line += line
        stack.append(current_line)

        # prune empty lines at bottom of the textbox.
        for item in stack[::-1]:
            if len(item) == 0:
                stack.pop()
            else:
                break

        out = '\n'.join(stack)
        return out
