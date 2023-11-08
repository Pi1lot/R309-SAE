import socket

port = 5005

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', port))
server_socket.listen(1)

while True:
    try:
        message = conn.recv(1024).decode()
    except:
        conn, address = server_socket.accept()
    else:
        if message == 'bye':
            conn.close()
        elif message == 'arret':
            break
        elif message != '':
            reply = f"Serveur -> Réponse à {message}"
            conn.send(reply.encode())
        print(message)
server_socket.close()
print("Extinction du serveur")
