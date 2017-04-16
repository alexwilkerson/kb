from socket import socket, AF_INET, SOCK_STREAM

def client_handler(client_sock, client_addr):
    print('Connected to {}'.format(client_addr))
    try:
        #  user = client_sock.recv(1024)
        #  client_sock.sendall(user)
        while True:
            msg = client_sock.recv(1024)
            if not msg:
                break
            print(msg.decode('utf-8'))
            client_sock.send(msg)
    except socket.error:
        print('Socket error occurred.')
    print('Disconnected from {}'.format(client_addr))
    client_sock.close()

def server(address=('localhost', 4242), backlog=5):
    print('Keybeard server started on address {}.'.format(address[1]))
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client_sock, client_addr = sock.accept()
        client_handler(client_sock, client_addr)

def main():
    server()

if __name__ == '__main__':
    main()

