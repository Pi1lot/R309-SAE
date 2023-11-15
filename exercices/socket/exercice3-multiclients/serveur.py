# Imports
import socket
from _thread import *

# Declarations
host = '0.0.0.0'
port = 25565
ThreadCount = 0


def client_handler(connection):
    connection.send(str.encode('You are now connected to the replay server... Type BYE to stop'))
    while True:
        data = connection.recv(1024)
        message = data.decode()
        if message == 'BYE':
            break
        reply = f'Server: {message}'
        connection.sendall(reply.encode())
    connection.close()


def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(client_handler, (Client,))


def start_server(host, port):
    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print(f'Server is listing on the port {port}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)


start_server(host, port)