# import socket programming library
import socket
import time
# import thread module
from _thread import *
import threading
import os, sys
print_lock = threading.Lock()



stop = 0

class ArretError(Exception):
	"La connexion a été fermé sur demande de l'un des deux parti"
	pass
def threaded(c):
    global stop
    while True:
        data = c.recv(1024).decode()
        print(f"Client dit : {data}")
        if data == 'bye':
            print('Bye, déconnexion du client')
            print_lock.release()
            break

        elif data == 'arret':
            print('Arrêt du serveur')
            print_lock.release()
            stop = 1
            break
    c.close()



def sendmessage(s):
    while True:
        message = input("Entrez un msg")
        s.send(message.encode())


def Main():

    host = "0.0.0.0"

    port = 12222
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Socket rattaché au port", port)

    s.listen(5)
    print("Port à l'écoute :")
    while not stop:
        c, addr = s.accept()
        print_lock.acquire()
        print('Connection à :', addr[0], ':', addr[1])
        start_new_thread(threaded, (c,))
        start_new_thread(sendmessage, (c,))

    print("Arret du serveur")
    s.close()
    os._exit(0)


if __name__ == '__main__':
    Main()
