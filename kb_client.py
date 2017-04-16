import os
import signal
import atexit
import getpass
import curses
import threading
from threading import Lock
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from curses import wrapper
from ui import UI

def server_connect():
    server = ('', 4242)
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect(server)
    except:
        print("Could not connect to server.")
        exit()
    return s

def reconnect(ui):
    while True:
        try:
            server = ('', 4242)
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(server)
            ui.s = s
            ui.chatbuffer.append('Reconnected.\n')
            ui.redraw_ui()
            return s
        except:
            s.close()
            ui.chatbuffer.append('Could not reconnect.\n')
            ui.redraw_ui()
            sleep(1)

def exit_client(s):
    s.close()

def listener(ui, s, chat_lock):
    while True:
        try:
            data, addr = s.recvfrom(1024)
            if len(data) > 0:
                with chat_lock:
                    ui.chatbuffer.append(data.decode('utf-8') + '\n')
                    ui.redraw_ui()
            else:
                with chat_lock:
                    ui.chatbuffer.append('Lost connection to server.\n')
                    ui.redraw_ui()
                s.close()
                sleep(1)
                s = reconnect(ui)
        except:
            pass

def main(stdscr):
    stdscr.clear()

    s = server_connect()
    atexit.register(exit_client, s=s)
    chat_lock = threading.Lock()

    title = 'keybeard alpha'
    user = getpass.getuser()

    ui = UI(stdscr, s, chat_lock, title, user)
    ui.chatbuffer.append("testing\n")

    # Use signal to handle window resizing.
    def resize_handler(signum, frame):
        curses.endwin()
        curses.initscr()
        ui.redraw_ui()
    signal.signal(signal.SIGWINCH, resize_handler)

    listener_thread = threading.Thread(target=listener, args=(ui,s,chat_lock))
    listener_thread.daemon = True
    listener_thread.start()

    ui.input_loop()

wrapper(main)
