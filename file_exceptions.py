file_path = "example_file.txt"


try :
    with open(file_path, 'r') as f:
        for l in f:
            l = l.strip('\n')
            print(l)


except FileExistsError:
    print("Le fichier existe déjà")
except IOError:
    print("Erreur lors de l'écriture/lecture du fichier")
except FileNotFoundError:
    print("Le fichier n'existe pas")
except PermissionError:
    print("Vous n'avez pas la permission d'interagir avec ce fichier")
else:
    print("Aucun problème n'est survenu")
finally:
    print("Fin du programme")


