#Import des différentes librairies
import random
import tkinter as tk
import socket
import threading
from tkinter import messagebox, ttk
import pymysql
import json
import time
import datetime

#création de la fenêtre "Serveur"
window = tk.Tk()
window.title("Serveur")

#Utilisation du thème "Forest-Light" https://github.com/rdbende/Forest-ttk-theme
window.tk.call('source', 'forest-light.tcl')
ttk.Style().theme_use('forest-light')

#Initialisation des différents boutons du haut de la fenêtre

topFrame = ttk.Frame(window)
btnStart = ttk.Button(topFrame, text="Connection", command=lambda : start_server())
btnStart.pack(side=tk.LEFT, padx=(7, 0))
btnStop = ttk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT, padx=(7, 0))
entLoginAdmin = ttk.Entry(topFrame)
entLoginAdmin.pack(side=tk.LEFT, padx=(7, 0))
entLoginPasswd = ttk.Entry(topFrame, show="*")
entLoginPasswd.pack(side=tk.LEFT, padx=(7, 7))
topFrame.pack(side=tk.TOP, pady=(15, 0))


#Initialisation des titres avec le port et l'interface d'écoute du serveur
middleFrame = tk.Frame(window)

lblHost = ttk.Label(middleFrame, text = "Écoute sur l'interface: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = ttk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))


#Quand on utilise tk.BOTTOM c'est inversé, les éléments déclarés en premiers apparaissent à partir du BAS de la fenêtre
commandFrame = tk.Frame(window)

commandLine = ttk.Label(commandFrame, text="Commandes").pack()
btnChannels = ttk.Button(commandFrame, text="Channels", style='Accent.TButton', command=lambda : open_channel_window(), state=tk.DISABLED)
btnChannels.pack(side=tk.LEFT, padx=(7, 0))
btnKill = ttk.Button(commandFrame, text="Kill", style='Accent.TButton', command=lambda : Kill(), state=tk.DISABLED)
btnKill.pack(side=tk.LEFT, padx=(7, 0))
btnKick = ttk.Button(commandFrame, text="Kick", style='Accent.TButton', command=lambda : open_kick_window(), state=tk.DISABLED)
btnKick.pack(side=tk.LEFT, padx=(7, 0))
btnBan = ttk.Button(commandFrame, text="Ban", style='Accent.TButton', command=lambda : open_ban_window(), state=tk.DISABLED)
btnBan.pack(side=tk.LEFT, padx=(7, 0))
commandFrame.pack(side=tk.BOTTOM, pady=(5, 10))

#Ici on initialise la fenêtre de visualisation des utilisateurs connectés
clientFrame = tk.Frame(window)

lblLine = ttk.Label(clientFrame, text="Utilisateurs connectés:").pack()
scrollBar = ttk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill="y")
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

#Là on initialise les différentes variables pour le démarrage du serveur
server = None
HOST_ADDR = "0.0.0.0" #Interface d'écoute, ici toutes
HOST_PORT = 12222 #Port d'écoute
client_name = " "

clients = []
clients_names = []
connection = None #Pour la connexion à la base de données
channel_dict = {} #Permet de stocker le client + channel qu'il regarde actuellement

mysql_usr = 'root'
mysql_passwd = ''
mysql_host = '127.0.0.1'
mysql_database = 'sae309'

# Start server function
def start_server():
    """Cette fonction permet d'initialiser le serveur et commencer à accepter des connexions, et initialise la connexion avec la base de donnée MySQL
        Elle récupère les identifiants entrés dans la fenêtre et regarde s'ils correspondent à un user avec is_admin à 1
    Parameters:
    None

    Returns:
    None

   """
    global server, HOST_ADDR, HOST_PORT, connection, mysql_host, mysql_usr, mysql_database, mysql_passwd #Ici on récupère les différentes variables

    #Ici on vérifie d'abord si l'utilisateur a rentré quelque chose
    if len(entLoginAdmin.get()) < 1 or len(entLoginPasswd.get()) < 1:
        tk.messagebox.showerror(title="ERREUR", message="Rentrez quelque chose")
    else:
        #On se connecte à la base de donnée si c'est le cas
        try:
            connection = pymysql.connect(user=mysql_usr, password=mysql_passwd,host=mysql_host,database=mysql_database)
            print("Connection réussie")
            tkDisplay.config(state=tk.NORMAL)
            tkDisplay.delete('1.0', tk.END)

            #On affiche que la base de donnée est en ligne et qu'on a réussi à se connecter dessus
            tkDisplay.insert(tk.END, "Connexion à la BDD réussie" + "\n")
            tkDisplay.config(state=tk.DISABLED)
        except pymysql.Error as error:
                print(error)

        #Ici on fait appel à la méthode check_credential_admin pour vérifier si l'utilisateur a la permission de démarrer le serveur
        if check_credentials_admin(entLoginAdmin.get(), entLoginPasswd.get()):
            tk.messagebox.showinfo(title="Succès", message="Authentification réussie!")
            btnStart.config(state=tk.DISABLED)
            btnStop.config(state=tk.NORMAL)
            btnKill.config(state=tk.NORMAL)
            btnChannels.config(state=tk.NORMAL)
            btnKick.config(state=tk.NORMAL)
            btnBan.config(state=tk.NORMAL)

            #Là on initialise l'écoute du port 12222 et à accepter des clients
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(socket.AF_INET)
            print(socket.SOCK_STREAM)

            server.bind((HOST_ADDR, HOST_PORT))
            server.listen(5)  # server is listening for client connection

            #Là on initialise un nouveau thread qui va permettre de réceptionner les connexions sans bloquer les fonctions de la fenêtre principale
            threading._start_new_thread(accept_clients, (server, ))

            lblHost["text"] = "Écoute sur l'interface: " + HOST_ADDR
            lblPort["text"] = "Port: " + str(HOST_PORT)
        else:
            tk.messagebox.showerror(title="Erreur!", message="Mauvais passwd/login")

def stop_server():
    """Cette fonction permet d'éteindre proprement le serveur en faisant appel à la méthode Kill déclaré plus bas (elle permet d'envoyer un message à tout les utilisateurs connectés)
    Parameters:
    None

    Returns:
    None

   """
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)

    #On prévient les utilisateurs de l'extinction
    Kill()

    #On ferme la fenêtre
    window.destroy()

def check_credentials_admin(user, passwd):
    """Cette fonction permet de vérifier que l'utilisateur à les permissions suffisante pour utiliser l'interface serveur

    Parameters:
        user (str): Le nom d'utilisateur à vérifier
        passwd (str): Le mot de passe de l'utilisateur à vérifier


    Returns:
        True (bool): Si l'utilisateur a is_admin à 1 dans la base de donnée et que le login/mot de passe est juste
        False (bool): Pour tout les autres cas

   """
    print("Test de vérificatIon")

    global connection #Ici on utilise la connection qu'on a crée au lancement du serveur
    print(connection)
    with connection.cursor() as cursor:

        #On lit seulement une entrée de la BDD
        sql = "SELECT `password` FROM `user` WHERE `user_name`=%s AND `is_admin` = 1"
        cursor.execute(sql, (user,))
        result = cursor.fetchone()
        print(result)
        #Ici on a la logique de la vérification

        if result:
            if result[0] != passwd:
                 return False
            else:
                return True
        else:
            return False

def check_credentials(user, passwd):
    """Cette fonction permet de vérifier que l'utilisateur peut initialiser une connexion au chat avec son login/mot de passe

    Parameters:
        user (str): Le nom d'utilisateur à vérifier
        passwd (str): Le mot de passe de l'utilisateur à vérifier


    Returns:
        True (bool): Si le login/mot de passe de l'utilisateur est juste
        False (bool): Pour tout les autres cas

   """
    print("Test de vérificatIon")

    global connection #On utilise la même connexion à la BDD pour toutes les fonctions
    print(connection)
    with connection.cursor() as cursor:
        #
        sql = "SELECT `password` FROM `user` WHERE `user_name`=%s"
        cursor.execute(sql, (user,))
        result = cursor.fetchone()
        print(result)

        if result:
            if result[0] != passwd:
                 return False
            else:
                return True
        else:
            return False

def accept_clients(server):
    """Cette fonction permet de gérer la logique de connexion d'un tuilisateur, vérifier s'il est ban, s'il est kick, si il existe dans la BDD etc..
        Si tout est bon on crée un nouveau thread pour la réception/émission de messages pour ce client
    Parameters:
        server (socket): L'objet "serveur"



    Returns:

        TEMP_KICKED (str): Message à destination du client pour lui signaler qu'il est kick avec la durée
        IS_BANNED (str): Message à destination du client pour lui signaler qu'il est banni
        IS_BANNED_IP (str): Message à destination du client pour lui signaler qu'il se connecte depuis une IP bannie
        REGISTER_ALREADYEXIST (str): Message à destination du client pour lui signaler que un utilisateur a déjà ce pseudo
        REGISTER_SUCCESS (str): Message à destination du client pour lui signaler qu'il a bien crée son compte
        ALREADY_CONNECTED (str): Message à destination du client pour lui signaler qu'il est déjà connecté avec ce compte
        GOOD_CREDENTIALS (str): Message à destination du client pour lui autoriser l'accès à l'interface
        BAD_CREDENTIALS (str): Message à destination du client pour lui signaler qu'il s'est trompé de login/mdp


   """
    global client_name, channels, channel_dict  #Ici on ajoute les channels et le nom du client
    while True:
        client, addr = server.accept()
        print("Addr-----")
        print(addr)
        credentials = client.recv(4096).decode()
        tuple = credentials.split("|")
        print(tuple)
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT is_banned FROM user WHERE user_name = %s OR current_ip = %s"
            cursor.execute(sql, (tuple[0], addr[0])) #addr[0] correspond à l'IP, [1] correspond au port
            is_banned = cursor.fetchall()
            print("Affichage is_banned")
            is_banned = str(is_banned)
            print(is_banned) #is banned est un tuple de tuple, ou le premier chiffre correspnd à un bannisement pseudo, et le deuxième à 1 si c'est une IP black listé
            is_banned = ''.join(filter(str.isalnum, is_banned))
            print(is_banned)

        current_datetime = datetime.datetime.now()

        with connection.cursor() as cursor:
            # Lire les entrées dans la BDD
            sql = "SELECT kick_date, kick_time FROM user WHERE user_name = %s OR current_ip = %s"
            cursor.execute(sql, (tuple[0], addr[0]))
            is_kicked = cursor.fetchall()

            for entry in is_kicked:
                print(entry)
                # entry[0] est la date et l'heure
                # entry[1] est le temps en secondes
                if entry[1] is not None:
                    kicked_datetime = entry[0] + datetime.timedelta(seconds=entry[1])

                    if kicked_datetime > datetime.datetime.now():
                        print("L'utilisateur est kick.")
                        msg = f"TEMP_KICKED|{kicked_datetime}\n"
                        client.send(msg.encode())
                    else:
                        print("Vous n'êtes plus kick.")
                        with connection.cursor() as cursor:
                            sql = "UPDATE user SET kick_date = NULL, kick_time = NULL WHERE user_name = %s OR current_ip = %s"
                            cursor.execute(sql, (tuple[0], addr[0]))
                            connection.commit()
                else:
                    print("Le temps de bannissement est indéfini.")

        if '01' in is_banned:
            print("La personne est ban IP")
            msg = "IS_BANNED_IP"
            client.send(msg.encode())
        elif '10' in is_banned or '11' in is_banned:
            print("La personne est ban")
            msg = "IS_BANNED"
            client.send(msg.encode())

        #Là on gère l'enregistrement des nouveaux utilisateurs.
        elif tuple[2] == 'REGISTER':
            with connection.cursor() as cursor:
                sql = "SELECT `user_name` FROM `user`"
                cursor.execute(sql)
                users = cursor.fetchall()
                print(tuple[0])
                print(users)
            if [item for item in users if tuple[0] in item]:
                msg = "REGISTER_ALREADYEXIST"
                client.send(msg.encode())
            else:
                msg = "REGISTER_SUCCESS"
                client.send(msg.encode())
                with connection.cursor() as cursor:
                    sql = "INSERT INTO user(user_name, password, is_admin) VALUES(%s, %s, 0)"
                    cursor.execute(sql, (tuple[0], tuple[1]))
                    connection.commit()
                with connection.cursor() as cursor:
                    # Read a single record
                    sql = "SELECT `channel_name` FROM `channel` WHERE `need_valid` = 0 "
                    cursor.execute(sql)
                    free_channels = [record[0] for record in cursor.fetchall()]
                channel_assignments = []

                for free in free_channels:  # ici on ajoute aussi les channels sans permissions.
                    channel_assignments.append(free)
                # Convert the list to a string, e.g., using JSON or ','.join
                channel_str = json.dumps(channel_assignments)  # or use ','.join(channel_assignments)

                # Insert the channel string into the database
                with connection.cursor() as cursor:
                    sql = "UPDATE user SET channel_name = %s WHERE user_name = %s"
                    cursor.execute(sql, (channel_str, tuple[0]))
                    connection.commit()
        # Là on gère le cas où l'utilisateur est déjà connecté depuis une autre fenêtre
        elif tuple[0] in channel_dict:
            print("Already connected")
            msg = "ALREADY_CONNECTED"
            client.send(msg.encode())
        # Là on signale à l'interface utilisateur que celui-ci s'est authentifié
        elif tuple[2] == 'LOGIN' and check_credentials(tuple[0], tuple[1]):
            print("checking credentials")
            msg = "GOOD_CREDENTIALS"
            client.send(msg.encode())
            client_name = tuple[0]
            #On envoie la liste des channels au client via la fonction send_channes_list
            send_channel_list(client, tuple[0])
            clients.append(client)

            #Création du thread pour ce client en particulier
            threading._start_new_thread(send_receive_client_message, (client, ))
            with connection.cursor() as cursor:
                sql = "UPDATE user SET current_ip = %s WHERE user_name = %s"
                cursor.execute(sql, (addr[0], client_name, ))
                connection.commit()
        # Sinon on lui signale que le login/mdp est incorrecte
        else:
            msg = "BAD_CREDENTIALS"
            client.send(msg.encode())
        print("Contenu de channel_dict")
        print(channel_dict)
        print(tuple[0])

def send_channel_list(client, client_name):
    """Cette fonction envoie au client la liste des channels auquel il a accès, via un string

    Parameters:
        client (socket): La connexion initialisée au dernier client à s'être connecté
        client_name (str): Le nom de l'utilisateur connecté


    Returns:
        msg (str): Liste des channels, commence par CHANNEL_LIST| pour être interprêté par le client


   """
    global connection
    with connection.cursor() as cursor:
        sql = "SELECT channel_name FROM user WHERE user_name=%s"
        cursor.execute(sql, (client_name,))
        channels = cursor.fetchall()
        print(channels[0][0])

    msg = f"CHANNEL_LIST|{channels[0][0]}\n"
    print(msg)
    client.send(msg.encode())

def send_receive_client_message(client_connection):

    """Cette fonction gère la réception/émission des message par clients, il y a une instance de cette fonction par client.
        Elle insère aussi les messages dans la abase de données

    Parameters:
        client_connection (socket): La connexion initialisée au dernier client à s'être connecté


    Returns:
        server_message (str): Les différents messages de statuts, client s'est déconnecté/connecté, etc...


   """

    global server, client_name, clients, clients_addr, channel_dict #L'object "serveur", le nom du client, l'adresse du client, et le dictionnaire client/channel
    client_msg = " "


    clients_names.append(client_name)

    update_client_names_display()  #Mettre à jour les clients connectés dans la fenêtre
    for c in clients:
        if c != client_connection:
            server_msg = str(client_name + " s'est connecté")
            c.send(server_msg.encode())

    #Ici on gère les exceptions de déconnexions, et si c'est le cas on supprime toutes les référence au client qui s'est déconnecté
    while True:
        try:
            data = client_connection.recv(4096).decode()
            print(data)

            #Là on regarde si le client ne demande pas les channels auquel il a accès
            if data.startswith("SELECT_CHANNEL"):
                idx = get_client_index(clients, client_connection)
                sending_client_name = clients_names[idx]
                # Handle the SELECT_CHANNEL message differently
                channel_dict[sending_client_name] = data.split("|")[1]
                update_client_names_display()
                get_channel_messages(data.split("|")[1], client_connection, sending_client_name)
                print(channel_dict)

            #Sinon, si les données reçus sont non nulles, on reçois le message et on le transmet aux autres clients en fonction du channel qu'ils regardent
            #Dans tout les autres cas on supprime la connexion au client
            elif len(data)>0:
                idx = get_client_index(clients, client_connection)
                sending_client_name = clients_names[idx]
                with connection.cursor() as cursor:
                    sql = "INSERT INTO message(channel_name, user_name, content, timestamp) VALUES(%s, %s, %s, NOW())"
                    sending_client_channel = channel_dict.get(sending_client_name, "")
                    cursor.execute(sql, (sending_client_channel, sending_client_name, data, ))
                    connection.commit()

                for c in clients:
                    if c != client_connection:
                        receiving_client_name = clients_names[get_client_index(clients, c)]
                        receiving_client_channel = channel_dict.get(receiving_client_name, "")
                        sending_client_channel = channel_dict.get(sending_client_name, "")

                        #Vérifier si le destinataire regarde le même canal que l'émetteur
                        if receiving_client_channel == sending_client_channel:
                            server_msg = str(sending_client_name + "->" + data+ "\n")
                            c.send(server_msg.encode())
            else:
                break
        except:
            break

    #Là on supprime toutes les références au client
    try:
        idx = get_client_index(clients, client_connection)
        print(clients_names[idx])
        disconnect = clients_names[idx]
        del channel_dict[clients_names[idx]]
        del clients_names[idx]
        del clients[idx]
        print(channel_dict)
        for c in clients:
            server_msg = str(disconnect + " s'est déconnecté\n")
            c.send(server_msg.encode())
    except IndexError:
        print("La connexion à été interrompu côté serveur suite à un ban/kick, inutile de re-supprimer")

    client_connection.close()
    print("Déconnexion par exit")

    #Ici on met à jour la liste des clients avec un délai car sinon plusieurs threads vont ajoutés du tete en même temps causant une duplication
    time.sleep(random.random()) #délai pour éviter que plusieurs déconnexion simultannée causent la duplication de l'affichage
    update_client_names_display()

def get_client_index(client_list, curr_client):
    """Cette fonction permet de récupérer l'index du client actuel dans la liste des clients connectés

    Parameters:
        client_list (list): La liste des clients actuellement connectés
        curr_client (str): Le nom du client dont l'on veut obtenir l'index



    Returns:
        idx (int): L'index du client ciblé


   """
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

def get_channel_messages(channel_name, client, requester):
    """Cette focntion permet d'envoyer l'historique des messages précédents aux clients en les formattants pour qu'il y ai écrit "moi" devant les messages du client

    Parameters:
        channel_name (str): Le channel d'où l'on vuet récupérer les messages
        client (socket): La connexion au client pour lui envoyer le message
        requester (str): Nom du client pour le comparer avec celui dans la BDD et formater le message



    Returns:
        msg(str): Le message récupéré la base de donné


   """

    global connection
    with connection.cursor() as cursor:
        sql = "SELECT user_name, content FROM message WHERE channel_name = %s ORDER BY timestamp"
        cursor.execute(sql, (channel_name,))
        messages = cursor.fetchall()
        for user, message in messages:
            if user != requester:
                msg = user + "->" + message + "\n"
            else:
                msg = "Moi->" + message + "\n"
            print(msg)
            client.send(msg.encode())

def update_client_names_display():
    """Cette fonction permet de mettre à jour l'affichage des clients connectés

    Parameters:
        None



    Returns:
        None


   """

    global channel_dict
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)
    for user, channel in channel_dict.items():
        tkDisplay.insert(tk.END, user + " regarde " + channel + "\n")
    tkDisplay.config(state=tk.DISABLED)
    print("Updating client list")

def Kill():
    """Cette fonction permet d'envoyer un ordre "Kill" à tout les clients connectés pour les forcer à s'éteindres

    Parameters:
        None



    Returns:
        None


   """
    print("Sending KILL to all clients")
    for client_connection in clients:
        try:
            client_connection.send("KILL".encode())
        except:
            print(f"Failed to send KILL to {client_connection}")

    #On détruit la fenêtre
    window.destroy()

def disconnect_banned_user(user, reason, duration = ''):
    """Cette fonction permet de bannir/kick, en fonction de la valeur de "reason", on peut aussi mettre un argument facultatif pour la durée.

    Parameters:
        user (str): Le nom de l'utilisateur cible
        reason (str): 'kick ou 'ban', permet d'utiliser la focntion pour les deux cas
        duration (str): Exprimée en secondes, peut être vide


    Returns:
        IS_KICKED (str): Déconnecte le client côté client en lui affichant un message
        IS_BANNED (str): Déconnecte le client côté client en lui affichant un message
        TEMP_KICK (str):Déconnecte le client côté client en lui affichant un message avec la durée du kick


   """
    global clients, clients_names, channel_dict
    print("Deconnexion d'un user suite à " + reason)
    if user in clients_names:
        print("User trouvé " + user)
        idx = get_client_index(clients_names, user)
        client_connection = clients[idx]

        # Fermez la connexion du client par le client
        if reason == 'ban':
            for c in clients:
                server_msg = str(user + " a été banni.\n")
                c.send(server_msg.encode())
            client_connection.send("IS_BANNED\n".encode())
            print(server_msg)
        elif reason == 'kick' and duration == '':
            for c in clients:
                server_msg = str(user + " a été kick.\n")
                c.send(server_msg.encode())
            client_connection.send("IS_KICKED\n".encode())
            print(server_msg)
        elif reason == 'kick' and duration != '':
            for c in clients:
                server_msg = str(user + " a été kick "+ duration+" secondes.\n")
                c.send(server_msg.encode())
            client_msg = f"TEMP_KICK|{duration}\n"
            client_connection.send(client_msg.encode())
            print(server_msg)

def open_ban_window():
    """Cette fonction permet de d'ouvrir une fenêtre pour la gestion du ban

    Parameters:
        None

    Returns:
        None


   """
    global connection
    ban_window = tk.Toplevel(window)
    ban_window.title("Bannir des utilisateurs")

    #On récupère l'état actuel de l'utilisaeur de la base de donnée pour adapter l'affichage
    with connection.cursor() as cursor:
        sql = "SELECT `user_name`, `is_banned` FROM `user`"
        cursor.execute(sql)
        user_data = cursor.fetchall()

    #Ensuite on crée dynamiquement les checkboxes avec les noms
    ttk.Label(ban_window, text="Utilisateurs").grid(row=0, column=0, padx=5, pady=5)
    ttk.Label(ban_window, text="Bannir").grid(row=0, column=1, padx=5, pady=5)

    #Pour chaque utilisateur dans la base de données on crée un bouton
    user_checkboxes = {}
    for i, (user, is_banned) in enumerate(user_data, start=1):
        user_checkboxes[user] = tk.IntVar(value=is_banned)
        ttk.Label(ban_window, text=user).grid(row=i, column=0, padx=5, pady=5)
        ttk.Checkbutton(ban_window, variable=user_checkboxes[user]).grid(row=i, column=1, padx=5, pady=5)

    def save_banned_status():
        """Cette fonction permet de sauvegarder l'état de bannisment de l'utilisateur dans la base de données

        Parameters:
            None


        Returns:
            None


       """
        for user, var in user_checkboxes.items():
            is_banned = var.get()
            with connection.cursor() as cursor:
                sql = "UPDATE user SET is_banned = %s WHERE user_name = %s"
                cursor.execute(sql, (is_banned, user))
                connection.commit()
                if is_banned:
                    #Si l'utilisateur à la case "banni" cochée, on le déconnecte avec la fonction disconnect_banned_user
                    disconnect_banned_user(user, 'ban')
        ban_window.destroy()

    ttk.Button(ban_window, text="Enregistrer", command=save_banned_status).grid(row=len(user_data) + 1, column=0, columnspan=2, pady=10)

def open_kick_window():
    """Cette fonction permet de d'ouvrir une fenêtre pour la gestion du kick

    Parameters:
        None

    Returns:
        None


   """
    global connection
    kick_window = tk.Toplevel(window)
    kick_window.title("Kick des utilisateurs")

    #On récupère la liste des users
    with connection.cursor() as cursor:
        sql = "SELECT `user_name`, `kick_date`, `kick_time` FROM `user`"
        cursor.execute(sql)
        user_data = cursor.fetchall()

    #On crée les "labels" avec les boutons pour chaque utilisateur

    ttk.Label(kick_window, text="Utilisateurs").grid(row=0, column=0, padx=5, pady=5)
    ttk.Label(kick_window, text="Kick").grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(kick_window, text="Durée (en secondes)").grid(row=0, column=2, padx=5, pady=5)
    ttk.Label(kick_window, text="Date d'expiration").grid(row=0, column=3, padx=5, pady=5)
    user_checkboxes = {}
    duration_entries = {}
    expiration_labels = {}

    for i, (user, kick_date, kick_time) in enumerate(user_data, start=1):
        is_banned = 0
        user_checkboxes[user] = tk.IntVar(value=is_banned)
        ttk.Label(kick_window, text=user).grid(row=i, column=0, padx=5, pady=5)
        ttk.Checkbutton(kick_window, variable=user_checkboxes[user]).grid(row=i, column=1, padx=5, pady=5)
        duration_entries[user] = ttk.Entry(kick_window)
        duration_entries[user].grid(row=i, column=2, padx=5, pady=5)

        #On calcule la date d'expiration des kicks et on l'affiche
        if kick_date is not None:
            kick_date = datetime.datetime.strptime(str(kick_date), '%Y-%m-%d %H:%M:%S')
            kick_duration = datetime.timedelta(seconds=kick_time)
            expiration_date = kick_date + kick_duration

        #Comme la valeur par défaut est NULL il faut gérer ce cas
        else:
            print("Pas kick")
            expiration_date = "Pas kick"

        expiration_labels[user] = ttk.Label(kick_window, text=expiration_date)
        expiration_labels[user].grid(row=i, column=3, padx=5, pady=5)

    def kick_users():
        """Cette fonction permet de sauvegarder les kicks et leurs durées.

        Parameters:
            None

        Returns:
            None


       """
        for user, var in user_checkboxes.items():
            is_kicked = var.get()
            print("Print de var() is_kicked" + str(is_kicked))
            duration = duration_entries[user].get()
            print(duration)

            if is_kicked and duration != '':
                with connection.cursor() as cursor:
                    sql = "UPDATE user SET kick_date = NOW(), kick_time = %s WHERE user_name = %s"
                    cursor.execute(sql, (int(duration), user ))
                    connection.commit()

                #Là on déconnecte les users kicks.
                disconnect_banned_user(user, 'kick', duration)
            elif is_kicked and duration == '':
                disconnect_banned_user(user, 'kick')

        kick_window.destroy()

    ttk.Button(kick_window, text="Kick", command=kick_users).grid(row=len(user_data) + 1, column=0, columnspan=3, pady=10)

def open_channel_window():
    """Cette fonction permet de d'ouvrir une fenêtre pour la gestion des channels par utilisateurs

    Parameters:
        None

    Returns:
        None


   """
    global connection
    channel_window = tk.Toplevel(window)
    channel_window.title("Attribution des channels")

    # On récupère la liste de tout les channels mais on affiche que ceux qui nécessitent une validation
    with connection.cursor() as cursor:
        sql = "SELECT `channel_name` FROM `channel` WHERE `need_valid` = 1 "
        cursor.execute(sql)
        channels = [record[0] for record in cursor.fetchall()]
        print(channels)

    with connection.cursor() as cursor:
        sql = "SELECT `channel_name` FROM `channel` WHERE `need_valid` = 0 "
        cursor.execute(sql)
        free_channels = [record[0] for record in cursor.fetchall()]
        print(channels)

    #On récupère les channels actuels des utilisateurs pour afficher leurs états.
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `user_name`, `channel_name` FROM `user`"
        cursor.execute(sql)
        user_data = cursor.fetchall()
        print(user_data)

    #Pour chaque utilisateur dans la liste on crée les boutons et les labels.
    ttk.Label(channel_window, text="Users").grid(row=0, column=0, padx=5, pady=5)
    ttk.Label(channel_window, text="Channels").grid(row=0, column=1, padx=5, pady=5)
    user_checkboxes = {}
    for i, (user, channel_id_str) in enumerate(user_data, start=1):
        user_checkboxes[user] = {}
        ttk.Label(channel_window, text=user).grid(row=i, column=0, padx=5, pady=5)

        #Ici on charge les permissions actuels des utilisateurs
        existing_permissions = json.loads(channel_id_str) if channel_id_str else []

        for j, channel in enumerate(channels, start=1):
            var = tk.IntVar()
            var.set(1 if channel in existing_permissions else 0)
            ttk.Checkbutton(channel_window, text=channel, style='ToggleButton', variable=var).grid(row=i, column=j, padx=5, pady=5)
            user_checkboxes[user][channel] = var


    def save_channel_assignment():
        """Cette fonction permet de sauvegarder les channels par users dans la BDD

        Parameters:
            None

        Returns:
            None


       """
        for user, channels_dict in user_checkboxes.items():
            #Liste pour les channels par users
            channel_assignments = []

            for channel, var in channels_dict.items():
                #var permet de récupérer l'état de la checkbox (booléen)
                print(f"{user} - {channel}: {var.get()}")
                if var.get() == 1:
                    channel_assignments.append(channel)

            for free in free_channels: #ici on ajoute aussi les channels sans permissions car sinon les utilisateurs les auront pas
                channel_assignments.append(free)

            #On génère un string contenant les channels
            channel_str = json.dumps(channel_assignments)  # or use ','.join(channel_assignments)

            #Puis on insert ce string dans la database
            with connection.cursor() as cursor:
                sql = "UPDATE user SET channel_name = %s WHERE 'user_name' = %s"
                cursor.execute(sql, (channel_str, user))
                connection.commit()
        channel_window.destroy()

    ttk.Button(channel_window, text="Save", command=save_channel_assignment).grid(row=len(user_data) + 1, column=0, columnspan=len(channels) + 1, pady=10)

#Ici on initialise la fenêtre
window.mainloop()
