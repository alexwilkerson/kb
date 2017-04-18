#!/usr/bin/env python3

import threading
import socket
import pickle
import datetime
import re
import random

clients = {}
clients_lock = threading.Lock()

def thetime():
    return datetime.datetime.now().strftime("[%H:%M:%S]");

def roll(dice, username):
    try:
        a,b,c=re.findall("^(\d*)d(\d+)(\+\d+)?$",dice)[0];the_roll=int(c or 0)+(sum(random.randint(1,int(b))for i in range(int(a or 1)))or q)
        response = thetime() + " \033[94m" + username + " rolled \033[125m" + dice + " \033[94mand got a \033[125m" + str(the_roll) + "\033[94m."
        with clients_lock:
            for c in clients.values():
                c.sendall(response.encode())
    except Exception as e:
        print(str(e))
        with clients_lock:
            clients[username].sendall('\033[160mWhoopsie! Enter something like \"!roll 1d20\".'.encode())

def send_users(sock):
    sock.sendall('$USERLIST$'.encode())
    users = []
    with clients_lock:
        users = list(clients.keys())
    users.append('idle monster')
    f = sock.makefile('wb', 1024)
    pickle.dump(users, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    # receives response from client
    # empty_buffer = sock.recv(32)
    print('Userlist sent.')

def client_handler(client, c_address):
    print('Connected to {}'.format(c_address))
    username = client.recv(1024)
    username = username.decode()
    with clients_lock:
        clients[username] = client
    print('User: {}\n'.format(username))
    try:
        enter_string = '{} \033[94m{} entered the room.'.format(thetime(), username)
        for c in clients.values():
            send_users(c)
            c.sendall(enter_string.encode())
        while True:
            data = client.recv(1024)
            if not data:
                break
            if data.decode().rstrip()[:5] == '.roll':
                data = data.decode().split()
                if len(data) == 1:
                    dice = '1d20'
                else:
                    dice = data[1]
                roll(dice, username)
            elif data.decode() == '$USERLIST$':
                pass
            else:
                print(data.decode('utf-8'))
                with clients_lock:
                    for c in clients.values():
                        if c == client:
                            response = '{} \033[89m{}:\033[0m {}'.format(thetime(), username, data.decode()).encode()
                        else:
                            response = '{} \033[20m{}:\033[0m {}'.format(thetime(), username, data.decode()).encode()
                        c.sendall(response)
    except socket.error:
        print('Socket error occurred.')
    finally:
        exit_string = '{} \033[94m{} left the room.'.format(thetime(), username)
        with clients_lock:
            del clients[username]
        print('Disconnected from {}'.format(c_address))
        client.close()
        for c in clients.values():
            send_users(c)
            c.sendall(exit_string.encode())

def server(address=('localhost', 4242), backlog=5):
    print('Keybeard server started on address {}.'.format(address[1]))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client, c_address = sock.accept()
        t = threading.Thread(target=client_handler, args=(client,c_address))
        t.daemon = True
        t.start()

def main():
    server()

if __name__ == '__main__':
    main()

