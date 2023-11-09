# Import socket module
import socket
from _thread import *
import threading
def threaded(c):
	while True:
		# data received from client
		data = c.recv(1024).decode()
		print(data)







def Main():
	host = '10.128.6.23'

	port = 12345

	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	# connect to server on local computer
	s.connect((host,port))

	# message you send to server
	start_new_thread(threaded, (s,))
	while True:
		message = input("Entrez un msg")
		# message sent to server
		s.send(message.encode())


		# ask the client whether he wants to continue
		if message == 'bye':
			continue
		else:
			break

	# close the connection
	s.close()

if __name__ == '__main__':
	Main()
