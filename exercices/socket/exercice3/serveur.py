# import socket programming library
import socket
import time
# import thread module
from _thread import *
import threading

print_lock = threading.Lock()
arretFlag = 0

class ArretError(Exception):
	"La connexion a été fermé sur emande de l'un des deux parti"
	pass
def threaded(c):
    while True:
        data = c.recv(1024).decode()
        print(data)
        if data == 'bye':
            print('Bye, déconnexion du client')
            print_lock.release()
            break

        elif data == 'arret':
            print('Arrêt du serveur')
            print_lock.release()
            global arretFlag
            arretFlag = 1

    c.close()



def Main():

    host = "0.0.0.0"

    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket rattaché au port", port)

    # put the socket into listening mode
    s.listen(5)
    print("Port à l'écoute :")
    while True:
        c, addr = s.accept()
        print_lock.acquire()
        print('Connection à :', addr[0], ':', addr[1])
        start_new_thread(threaded, (c,))
        print(arretFlag)
    s.close()


if __name__ == '__main__':
    Main()
