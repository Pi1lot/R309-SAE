import socket

port = 5000

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', port))
server_socket.listen(1)
conn, address = server_socket.accept()
message = conn.recv(1024).decode()
reply = input("Entrez le message")
conn.send(reply.encode())
conn.close()
server_socket.close()