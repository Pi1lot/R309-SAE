import socket
from threading import Thread

stop = False
clients = {}


class ArretError(Exception):
    "La connexion a été fermée sur demande de l'un des deux parties"
    pass


def threaded(c, addr, name):
    global stop
    while True:
        try:
            data = c.recv(1024).decode()
            print(f"{name} dit : {data}")
            if data == 'bye':
                print(f'{name} a quitté la conversation')
                c.close()
                del clients[name]
                break

            elif data == 'arret':
                print('Arrêt du serveur')
                stop = True
                c.close()
                del clients[name]
                break

            # Envoyer le message à tous les clients sauf à l'émetteur
            for client_socket, client_name in clients.values():
                if client_socket != c:
                    try:
                        client_socket.send(f"{name} dit : {data}".encode())
                    except socket.error as e:
                        # Gérer les erreurs de connexion ici si nécessaire
                        pass
        except Exception as e:
            print(f"Erreur de communication avec {name}: {e}")
            c.close()
            del clients[name]
            break


def Main():
    global stop
    host = "0.0.0.0"
    port = 12222
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Socket rattaché au port", port)

    s.listen(5)
    print("Port à l'écoute :")

    while not stop:
        try:
            c, addr = s.accept()
            name = f"Client-{addr[1]}"
            clients[name] = (c, addr)
            print(f'Connection de {name} : {addr[0]}, {addr[1]}')
            thread = Thread(target=threaded, args=(c, addr, name))
            thread.start()
        except Exception as e:
            print(f"Erreur lors de la création d'un thread pour le client : {e}")

    print("Arrêt du serveur")
    s.close()


if __name__ == '__main__':
    Main()
