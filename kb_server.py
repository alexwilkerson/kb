#!/usr/bin/env python3

import threading
import socket
import pickle
import datetime

clients = {}
clients_lock = threading.Lock()

def thetime():
    return datetime.datetime.now().strftime("[%H:%M:%S]");

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
    sock.recv(64)
    print('Userlist sent.')

def client_handler(client, c_address):
    print('Connected to {}'.format(c_address))
    username = client.recv(1024)
    username = username.decode()
    print('User: {}\n'.format(username))
    with clients_lock:
        clients[username] = client
    try:
        enter_string = '{} \033[94m{} entered the room.'.format(thetime(), username)
        for c in clients.values():
            send_users(c)
            c.sendall(enter_string.encode())
        while True:
            data = client.recv(1024)
            if not data:
                break
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
        with clients_lock:
            del clients[username]
        print('Disconnected from {}'.format(c_address))
        client.close()
        for c in clients.values():
            send_users(c)
            c.sendall(enter_string.encode())

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

