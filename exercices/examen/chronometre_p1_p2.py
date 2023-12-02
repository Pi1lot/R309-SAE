from PyQt6.QtWidgets import (
    QMessageBox, QApplication, QWidget, QLineEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt
import sys, os

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.arret_thread = False
        self.valeur = 0

        self.resize(500, 1)
        self.setWindowTitle("Chronomètre")

        grid = QGridLayout()
        self.setLayout(grid)



        #Ligne 1
        self.label = QLabel("Compteur:")

        button = QPushButton("Start")
        button.clicked.connect(self.start)

        button1 = QPushButton("Reset")
        button1.clicked.connect(self.reset)

        button2 = QPushButton("Stop")
        button2.clicked.connect(self.get)

        button3 = QPushButton("Connect")
        button3.clicked.connect(self.get)

        button4 = QPushButton("Quitter")
        button4.clicked.connect(self.close)

        #Ligne 3
        self.label_conv = QLabel("Conversion")

        self.result = QLineEdit()
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


    def start(self):
        self.valeur += 1
        self.result.setText(str(self.valeur))

    def reset(self):
        self.valeur = 0
        self.result.setText(str(self.valeur))


    def get(self):
        try:
            text = round(float(self.input.text()), 2)
            if text <0 and self.__convstatus ==1:
                raise ValueError("Inférieur au 0 absolu")
            elif text <-273.15 and self.__convstatus == 0:
                raise ValueError("Inférieur au 0 absolu")
        except ValueError as err:
            self.result.setText(str(err))
        else:
            print(self.__convstatus)
            #self.label.setText(text)
            if self.__convstatus == 0:
                k = text + 273.15
                print(text)
                self.result.setText(str(round(k,2)))

            elif self.__convstatus == 1:
                print(text)
                k = text - 273.15
                self.result.setText(str(round(k,2)))




app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())