import socket
host = '10.128.2.14'
port = 5005
client_socket = socket.socket()
client_socket.connect((host, port))
while True:

    try:
        message = input("Entrez le message")
        client_socket.send(message.encode())
        if message == 'arret':
            print("Au revoir!")
            break
        reply = client_socket.recv(1024).decode()
        print(reply)
    except ConnectionAbortedError:
        print("Echec de connexion")

client_socket.close()