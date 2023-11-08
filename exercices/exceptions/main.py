# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

class NullOrNegative(Exception):
    "Nombre négatif ou nul"
    pass

def divEntier(x: int, y: int) -> int:
    if y == 0 or x < 0 or y < 0:
        raise NullOrNegative
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


if __name__ == '__main__':
    try:
        x = int(input("Entrez X"))
        y = int(input("Entrez y"))
        print(divEntier(x, y))
    except ValueError:
        print("Vous avez rentré autre chose qu'un entier")
    except NullOrNegative:
        print("Vous avez rentrer un nombre négatif ou égale à zéro")



"""
Questions:
1. C'est une division euclidienne écrite de manière récursive, qui nous donne le résultat
2. 80 et 5 : on obtient 16, c'est le résultat attendu

Exercices:
1.
2. a. Cela permet d'éviter que un string soit entré dans la fonction et provoque une erreur par exemple.
3. a. Si on entre 0, on obtient un nombre infini de récursions et cela provoque une erreur
"""
