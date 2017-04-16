import threading
import socket

clients = set()
clients_lock = threading.Lock()

def client_handler(client, c_address):
    print('Connected to {}'.format(c_address))
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
                    c.sendall(data)
    except socket.error:
        print('Socket error occurred.')
    finally:
        with clients_lock:
            clients.remove(client)
    print('Disconnected from {}'.format(c_address))
    client.close()

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

