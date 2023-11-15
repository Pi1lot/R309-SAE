import socket
host = '10.128.3.22'
port = 5555
client_socket = socket.socket()
client_socket.connect((host, port))
message = input("Entrez le message")

client_socket.send(message.encode())
reply = client_socket.recv(1024).decode()
print(reply)
client_socket.close()