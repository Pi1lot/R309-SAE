#Import des différentes librairies
import tkinter as tk
from tkinter import messagebox, ttk
import socket
import threading
import re

#création de la fenêtre "Client"
window = tk.Tk()
window.title("Client")
window.tk.call('source', 'forest-light.tcl')

#Utilisation du thème "Forest-Light" https://github.com/rdbende/Forest-ttk-theme
ttk.Style().theme_use('forest-light')
username = " "

#Initialisation des différents boutons du haut de la fenêtre
topFrame = tk.Frame(window)
lblName = ttk.Label(topFrame, text = "Pseudo:").pack(side=tk.LEFT)
entName = ttk.Entry(topFrame)
entName.pack(side=tk.LEFT, padx=(5,10))
lblPass = ttk.Label(topFrame, text = "MDP:").pack(side=tk.LEFT)
entPass = ttk.Entry(topFrame, show="*")
entPass.pack(side=tk.LEFT)
btnConnect = ttk.Button(topFrame, text="Connect", style='Accent.TButton', command=lambda : connect())
btnConnect.pack(side=tk.LEFT, padx=(5, 0))
btnCreateAccount = ttk.Button(topFrame, text="Crée un compte", style='Accent.TButton', command=lambda: create_account())
btnCreateAccount.pack(side=tk.LEFT, padx=(10, 10))
topFrame.pack(side=tk.TOP, pady=(20,0))

#Zone d'affichage des messages, avec un tag pour les afficher dans une autre couleur pour ses propres messages
displayFrame = tk.Frame(window)
lblHost = ttk.Label(displayFrame, text = "", font=(13))
lblHost.pack(side=tk.TOP)
scrollBar = ttk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill="y")
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="orange")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)

#Bas de la fenêtre
bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)

#Là on initialise les différentes variables pour la connexion au serveur
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 12222

def connect():
    """Cette fonction permet d'initialiser la connexion au serveur

    Parameters:
        None

    Returns:
        None

   """

    global username, client
    if len(entName.get()) < 1 and len(entPass.get()) < 1 :
        tk.messagebox.showerror(title="Erreur", message="Cette zone doit être complétée")
    else:
        username = entName.get()
        password = entPass.get()
        connect_to_server(username, password)

def connect_to_server(name, password):
    """Cette fonction permet d'initialiser la connexion au serveur

    Parameters:
        name (str): Pseudonyme de l'utilisateur
        password (str): Mot de passe correspondant

    Returns:
        None

   """
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))

        # Ici on envoie le username et le password au serveur et on attend une réponse
        credentials = f"{name}|{password}|LOGIN"
        client.send(credentials.encode())

        entName.config(state=tk.DISABLED)
        entPass.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        btnCreateAccount.config(state=tk.DISABLED)

        # Ici on fait un thread pour la réception/émission des messages afin de pas bloquer l'affichage de la fenêtre, et on attend la réponse du serveur
        threading._start_new_thread(receive_message_from_server, (client, ))
    except Exception as e:
        print(e)
        tk.messagebox.showerror(title="Erreur", message="Impossible de se connecter au serveur à l'adresse " + HOST_ADDR + ":" + str(HOST_PORT))

def receive_message_from_server(sck):
    """Ici, on réceptionne les nouveaux messages provenant du serveur, en fonction du début du message ils déclenchent des évènements différents

    Parameters:
        sck (socket): La connexion initialisée au serveur


    Returns:
        None

   """

    while True:
        from_server = ''
        try:
            from_server = sck.recv(4096).decode()
        except ConnectionResetError:
            tk.messagebox.showerror(title="Déconnexion", message="Le serveur à mis fin à la connexion de manière inattendue")
            window.destroy()

        #Tout les messages finissent par des \n (retours à la ligne)
        history = from_server.split("\n")
        print(history)

        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)

        #Là on teste tout les cas de figures
        for message in history:
            if message.startswith('Moi'):
                tkDisplay.insert(tk.END, "\n\n" + message, "tag_your_message")
                print("Message commence par Moi")
            elif message.startswith('BAD_CREDENTIALS'):
                tk.messagebox.showerror(title="Erreur", message="Mauvais mot de passe/username")
                entName.config(state=tk.NORMAL)
                entPass.config(state=tk.NORMAL)
                btnConnect.config(state=tk.NORMAL)
                print("Échec connexion")
                sck.close()
            elif message.startswith('GOOD_CREDENTIALS'):
                tk.messagebox.showinfo(title="Succès!", message="Connexion réussie!")
                tkMessage.config(state=tk.NORMAL)
                join_channel('general')
            elif message.startswith('REGISTER_ALREADYEXIST'):
                tk.messagebox.showerror(title="Erreur!", message="Cet utilisateur existe déjà!!")
                tkMessage.config(state=tk.NORMAL)
                sck.close()
            elif message.startswith('REGISTER_SUCCESS'):
                tk.messagebox.showinfo(title="Succès!", message="Création de compte réussie!")
                tkMessage.config(state=tk.NORMAL)
                sck.close()
            elif message.startswith('KILL'):
                sck.close()
                tk.messagebox.showinfo(title="Extinction!", message="[KILL] Le serveur va s'éteindre!")
                tkMessage.config(state=tk.NORMAL)
                window.destroy()
                break
            elif message.startswith('IS_BANNED'):
                sck.close()
                tk.messagebox.showerror(title="Banni!", message="[BANNI] Vous êtes banni du serveur!")
                tkMessage.config(state=tk.NORMAL)
                window.destroy()
                # time.sleep(1)
                break
            elif message.startswith('IS_KICKED'):
                sck.close()
                tk.messagebox.showerror(title="Kicked!", message="[KICK] Vous avez été kick.")
                tkMessage.config(state=tk.NORMAL)
                window.destroy()
                break
            elif message.startswith('TEMP_KICK|'):
                sck.close()
                time = message.split("|")[1]
                print(time)
                if time != '':
                    tk.messagebox.showerror(title="Kicked!",message="[KICK] Vous êtes kick pour " + time + " secondes.")
                    tkMessage.config(state=tk.NORMAL)
                    sck.close()
                    window.destroy()
                    break
            elif message.startswith('TEMP_KICKED'):
                sck.close()
                time = message.split("|")[1]
                print(time)
                if time != '':
                    tk.messagebox.showerror(title="Kicked!",message="[KICK] Vous êtes kick jusqu'à " + time)
                    tkMessage.config(state=tk.NORMAL)
                    sck.close()
                    window.destroy()
                    break
                else:
                    tk.messagebox.showerror(title="Kicked!", message="[KICK] Vous avez été kick.")
                    tkMessage.config(state=tk.NORMAL)
                    sck.close()
                    window.destroy()
                    break
            elif message.startswith('IS_BANNED_IP'):
                sck.close()
                tk.messagebox.showerror(title="Banni!", message="[BANNI] Cette IP est bannie!")
                tkMessage.config(state=tk.NORMAL)
                sck.close()
                window.destroy()
                break
            elif message.startswith('CHANNEL_LIST|'):
                channel_str = message.split("|")[1]
                print(channel_str)
                channels = channel_str
                update_channel_list_display(channels)
            elif message == 'ALREADY_CONNECTED':
                tk.messagebox.showerror(title="Erreur",message="Ce compte est déjà connecté ailleurs. Déconnexion.")
                tkMessage.config(state=tk.NORMAL)
                sck.close()
                window.destroy()
                break
            else:
                tkDisplay.insert(tk.END, "\n\n" + message)
        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)


def update_channel_list_display(channels):
    """Ici, on crée un bouton par channel reçu dans la fonction receive_message_from_server

    Parameters:
        sck (socket): La connexion initialisée au serveur

    Returns:
        None


   """
    #Là on supprime tout les boutons des channels s'ils y en a déjà
    for widget in window.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()

    #On récupère la liste des channels, mais on veut uniquement leurs noms
    channels_list = channels.split(',')
    regex = re.compile('[^a-zA-Z]')

    #Là on conserve que les caractères alphabétiques
    display_list = []
    for sub in channels_list:

        display_list.append(regex.sub('', sub))
    print(channels_list)
    buttonContainer = tk.Frame(window)
    buttonContainer.pack(side=tk.TOP, pady=(20, 0))

    #Là on génère un bouton par channel
    for i, channel in enumerate(display_list):
        btn = ttk.Button(buttonContainer, text=channel, command=lambda c=channel: join_channel(c))
        btn.grid(row=0, column=i, padx=5, pady=5)

    #Ici on fait en sorte qu'ils sont alignés proprement
    buttonContainer.grid_columnconfigure(0, weight=1)

def join_channel(selected_channel):
    """Ici on va afficher #ñomduchannel en haut de la fenêtre, puis envoyer l'information au serveur pour récupérer les messages

    Parameters:
        selected_channel (str): Le channel que l'utilisateur vient de sélectionner

    Returns:
        None


   """
    #On affiche le nom du channel
    lblHost["text"] = "#" + selected_channel
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)
    tkDisplay.config(state=tk.DISABLED)

    #On envoie le channel au serveur
    send_channel_to_server(selected_channel)


def send_channel_to_server(selected_channel):
    """Ici on va envoyer le channel actuel au serveur pour récupérer les messages

    Parameters:
        selected_channel (str): Le channel que l'utilisateur vient de sélectionner

    Returns:
        None


   """
    global client

    #Préfixe pour signaler au serveur qu'on a changer de channel
    msg = f"SELECT_CHANNEL|{selected_channel}"
    print(f"Je regarde {selected_channel}")
    client.send(msg.encode())

def getChatMessage(msg):
    """Là on va récupérer le message que l'utilisateur vient de taper et l'envoyer au serveur, et l'afficher dans la fenêtre en orange

    Parameters:
        msg (str): Le message dans la zone de texte de la fenêtre

    Returns:
        msg (str): le message à destiantion du serveur


   """
    #Ici on enlève le saut de ligne quand l'utilisateur a envoyer le message avec la touche entrée
    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "Moi->" + msg, "tag_your_message")
    else:
        tkDisplay.insert(tk.END, "\n\n" + "Moi->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)

def register_to_server(name, password):
    """Cette fonction permet de créer un compte auprès du serveur

    Parameters:
        name (str): Le nom d'utilisateur pour le nouveau compte
        password (str): Le mot de passe pour le nouveau compte

    Returns:
        None


   """
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        credentials = f"{name}|{password}|REGISTER"
        client.send(credentials.encode())



        #On démarre un nouveau thread en attendant la réponse du serveur
        threading._start_new_thread(receive_message_from_server, (client, ))
    except Exception as e:
        print(e)
        tk.messagebox.showerror(title="Erreur", message="Impossible de se connecter au serveur à l'adresse " + HOST_ADDR + ":" + str(HOST_PORT))

def send_mssage_to_server(msg):
    """Cette fonction permet d'envoyer les messages au serveur

    Parameters:
        msg (str): Le message

    Returns:
        None


   """
    client_msg = str(msg)
    client.send(client_msg.encode())
    print(f"Envoi du message {client_msg}")

def create_account():
    """Cette fonction permet d'afficher une fenêtre pour la création du nouveau compte

    Parameters:
        None

    Returns:
        None

   """

    global username, client

    #On crée une nouvelle fenêtre
    account_window = tk.Toplevel(window)
    account_window.title("Create Account")

    #Ici on crée les différents champs avec leurs descriptions
    ttk.Label(account_window, text="Username:").pack()
    new_username = ttk.Entry(account_window)
    new_username.pack()

    ttk.Label(account_window, text="Password:").pack()
    new_password = ttk.Entry(account_window, show="*")
    new_password.pack()

    ttk.Label(account_window, text="Confirm Password:").pack()
    password_confirmation = ttk.Entry(account_window, show="*")
    password_confirmation.pack()

    def process_account_creation():
        """Cette fonction permet d'afficher une fenêtre pour la création du nouveau compte

        Parameters:
            None

        Returns:
            None

       """
        nonlocal new_username, new_password, password_confirmation
        entered_username = new_username.get()
        entered_password = new_password.get()
        entered_confirmation = password_confirmation.get()

        #On vérifie que le mot de passe renseigné est le même dans les deux champs
        if entered_password == entered_confirmation:

            #On appel la fonction pour demander confirmation au serveur
            register_to_server(entered_username, entered_password)

            # Si c'est bon on peut fermer la fenêtre
            account_window.destroy()
        else:
            tk.messagebox.showerror("Erreur", "Les deux mots de passes sont différents")
    btnCreateAccount = ttk.Button(account_window, text="Créer un compte", command=process_account_creation)
    btnCreateAccount.pack()

#Enfin on démarre la fenêtre principale
window.mainloop()
