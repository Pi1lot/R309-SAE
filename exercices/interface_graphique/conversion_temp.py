from PyQt6.QtWidgets import (
    QMessageBox, QApplication, QWidget, QLineEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt
import sys, os

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.__convstatus = 0

        self.resize(500, 1)
        self.setWindowTitle("Une première fenêtre")

        grid = QGridLayout()
        self.setLayout(grid)



        #Ligne 1
        self.label = QLabel("Température")

        self.input = QLineEdit()

        self.label2 = QLabel("°C")

        #Ligne 2
        self.cb = QComboBox()
        self.cb.addItem("°C -> K")
        self.cb.addItem("K -> °C")
        self.cb.currentIndexChanged.connect(self.selectionchange)

        button = QPushButton("Convertir")
        button.clicked.connect(self.get)

        #Ligne 3
        self.label_conv = QLabel("Conversion")

        self.result = QLineEdit()
        self.result.setEnabled(False)

        self.label_result = QLabel("K")

        #Ligne4
        help = QPushButton("?")
        help.clicked.connect(self.show_popup)


        #Ligne 1
        grid.addWidget(self.label, 0, 0)

        grid.addWidget(self.label2 ,0, 2)

        grid.addWidget(self.input, 0,1)

        #Ligne2
        grid.addWidget(self.cb, 1,3)

        grid.addWidget(button, 1,1)

        #Ligne3
        grid.addWidget(self.label_conv, 2, 0)

        grid.addWidget(self.result, 2, 1)

        grid.addWidget(self.label_result, 2, 2)

        #Ligne4
        grid.addWidget(help, 3, 3)

        #Message d'aide

    def show_popup(self):
        QMessageBox.information(self,"Aide","Permet de convertir un nombre soit de Kelvin vers Celsius, soit de Celsius vers Kelvin",QMessageBox.StandardButton.Ok)

    def selectionchange(self, i):
        for count in range(self.cb.count()):
            print(self.cb.itemText(count))
        print("Current index", i, "selection changed ", self.cb.currentText())
        if i == 0:
            self.label2.setText("°C")
            self.label_result.setText("K")
            self.__convstatus = 0
        else:
            self.label2.setText("K")
            self.label_result.setText("°C")
            self.__convstatus = 1

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