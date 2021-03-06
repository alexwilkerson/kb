#!/usr/bin/env python3

import os
import sys
import signal
import atexit
import getpass
import curses
import threading
import pickle
import datetime
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

def reconnect(username, ui):
    while True:
        try:
            server = ('', 4242)
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(server)
            ui.s = s
            s.sendall(username.encode())
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

def read_obj(sock):
    f = sock.makefile('rb', 1024)
    data = pickle.load(f)
    f.close()
    return data

def clock(ui):
    while True:
        ui.redraw_footer()
        ui.input_win.refresh()
        sleep(1)

def listener(ui, s, chat_lock, username):
    try:
        s.sendall(username.encode('utf-8'))
        #  ui.userlist = read_obj(s)
        #  ui.redraw_users()
    except:
        pass
    while True:
        try:
            data = s.recv(1024)
            data = data.decode().strip()
            if len(data) > 0:
                if data == "$USERLIST$":
                    ui.userlist = read_obj(s)
                    s.sendall('$USERLIST$'.encode())
                    ui.redraw_users()
                    ui.input_win.refresh()
                elif data == '$USERNAME$':
                    pass
                else:
                    with chat_lock:
                        ui.chatbuffer.append(data + '\n')
                        #  curses.endwin()
                        #  curses.initscr()
                    #ui.redraw_ui()
                    ui.redraw_chat()
                    ui.input_win.refresh()
            else:
                with chat_lock:
                    ui.chatbuffer.append('Lost connection to server.\n')
                ui.redraw_chat()
                ui.input_win.refresh()
                # ui.redraw_ui()
                s.close()
                sleep(1)
                s = reconnect(username, ui)
        except Exception as e:
            ui.chatbuffer.append('Error occurred, tell Alex: ' + str(e) + '\n')

def main(stdscr):
    stdscr.clear()

    s = server_connect()
    atexit.register(exit_client, s=s)
    chat_lock = threading.Lock()

    title = 'kb alpha'
    if len(sys.argv) == 2:
        username = sys.argv[1]
    else:
        username = getpass.getuser()

    ui = UI(stdscr, s, chat_lock, title, username)

    # Use signal to handle window resizing.
    def resize_handler(signum, frame):
        curses.endwin()
        curses.initscr()
        ui.redraw_ui()
    signal.signal(signal.SIGWINCH, resize_handler)

    listener_thread = threading.Thread(target=listener, args=(ui,s,chat_lock, username))
    listener_thread.daemon = True
    listener_thread.start()

    clock_thread = threading.Thread(target=clock, args=(ui,))
    clock_thread.daemon = True
    clock_thread.start()

    #  while True:
    #      c = stdscr.getch()
    #      ui.chatbuffer.append(str(c) + '\n')
    #      ui.redraw_chat()
    #  while True:
    #      ui.input_textbox.edit()
    ui.input_loop()

wrapper(main)
