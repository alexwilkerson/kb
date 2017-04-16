import threading
from socket import socket, AF_INET, SOCK_STREAM

clients = set()
clients_lock = threading.Lock()

def client_handler(client, address):
    print('Connected to {}'.format(address))
    with clients_lock:
        clients.add(client)
    try:
        while True:
            data = client.recv(1024)
            if not data:
                break
            print(data.decode('utf-8'))
            with clients_lock:
                for c in clients:
                    client.sendall(data)
    except socket.error:
        print('Socket error occurred.')
    finally:
        with clients_lock:
            clients.remove(client)
    print('Disconnected from {}'.format(address))
    client.close()

def server(address=('localhost', 4242), backlog=5):
    print('Keybeard server started on address {}.'.format(address[1]))
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client, address = sock.accept()
        client_handler(client, address)

def main():
    server()

if __name__ == '__main__':
    main()

