import curses

def main(stdscr):
    col = 0
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1)
    try:
        for i in range(0, 256):
            if col == 16:
                stdscr.addstr('\n')
                col = 0
            stdscr.addstr(str(i).rjust(3, ' ') + " ", curses.color_pair(i))
            col += 1
    except curses.ERR:
        # End of screen reached
        pass
    stdscr.getch()

curses.wrapper(main)
