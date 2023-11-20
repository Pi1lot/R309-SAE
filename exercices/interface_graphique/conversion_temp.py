from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt
import sys, os


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 1)
        self.setWindowTitle("Une première fenêtre")

        grid = QGridLayout()
        self.setLayout(grid)

        #Ligne 1
        self.label = QLabel("Température")
        self.input = QLineEdit()
        self.label2 = QLabel("°C")


        button = QPushButton("Ok")
        button.clicked.connect(self.get)
        button = QPushButton("Quitter")
        button.clicked.connect(self.close)

        #Ligne 1
        grid.addWidget(self.label, 0, 0)
        grid.addWidget(self.label2 ,0, 2)
        grid.addWidget(self.input, 0,1)


        grid.addWidget(button)
        grid.addWidget(button)

    def get(self):
        text = f"Bonjour {self.input.text()}"
        self.label.setText(text)
        print(text)



app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())