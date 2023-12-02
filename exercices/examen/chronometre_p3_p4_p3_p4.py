from PyQt6.QtWidgets import (
    QMessageBox, QApplication, QWidget, QLineEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt
import sys, os
import time
import threading
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.valeur = 0
        self.arret_thread = False
        self.resize(500, 1)
        self.setWindowTitle("Chronomètre")

        grid = QGridLayout()
        self.setLayout(grid)

        self.t1 = threading.Thread(target=self.__start)  # important de mettre self.__start et pas juste __start

        #Ligne 1
        self.label = QLabel("Compteur:")

        button = QPushButton("Start")
        button.clicked.connect(self.start)

        button1 = QPushButton("Reset")
        button1.clicked.connect(self.reset)

        button2 = QPushButton("Stop")
        button2.clicked.connect(self.stop)

        button3 = QPushButton("Connect")
        button3.clicked.connect(self.close)

        button4 = QPushButton("Quitter")
        button4.clicked.connect(self.stop)
        button4.clicked.connect(self.close)

        #Ligne 3
        self.label_conv = QLabel("Conversion")

        self.result = QLineEdit("0")
        self.result.setEnabled(False)


        #Ligne4

        grid.addWidget(self.label, 0, 0, 1, 2)
        grid.addWidget(self.result, 1, 0, 1,2)
        grid.addWidget(button, 2, 0, 1, 2)
        grid.addWidget(button1, 3, 0, 1, 1)
        grid.addWidget(button2, 3, 1, 1, 1)
        grid.addWidget(button3, 4, 0, 1, 1)
        grid.addWidget(button4, 4, 1, 1, 1)
        #Ligne 1

    def __start(self):
        while self.arret_thread == False:
            time.sleep(1)
            self.valeur += 1
            self.result.setText(str(self.valeur))

    def start(self):
        self.arret_thread = False
        self.t1.start()  # je démarre la thread

    def stop(self):
        self.arret_thread = True
        self.t1.join()  # empêche de recliquer sur start lorsque le bouton stop est pressé.
    def reset(self):
        self.valeur = 0
        self.result.setText(str(self.valeur))

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())