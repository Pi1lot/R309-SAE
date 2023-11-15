# Import socket module
import socket
from _thread import *
import threading
import os, sys
class ArretError(Exception):
	"La connexion a été fermé sur emande de l'un des deux parti"
	pass
def threaded(c):
	Listening = True
	while Listening:
		reply = c.recv(1024).decode()
		if reply == 'arret':
			print("Extinction!")
			raise ArretError
			break

		elif reply == 'bye':
			print("Bye!")
			Listening = False
			break

		elif reply == 'arret':
			print("Arret!")
			os._exit(1)
	c.close()




def Main():

	host = input("Entrez l'IP du serveur")
	port = 25565
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))

	start_new_thread(threaded, (s,))
	while True:
		message = input("Entrez un msg")
		s.send(message.encode())
		if message == 'bye':
			break
		elif message == 'arret':
			os._exit(0)
		else:
			continue

	s.close()

if __name__ == '__main__':
	Main()
