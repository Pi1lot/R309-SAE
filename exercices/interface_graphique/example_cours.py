from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
import sys, os


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 1)
        self.setWindowTitle("Une première fenêtre")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label2 = QLabel("Saisir votre nom")
        self.label2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label2.adjustSize()

        layout.addWidget(self.label2)


        self.input = QLineEdit()
        self.input.setFixedWidth(500)
        layout.addWidget(self.input, alignment=Qt.AlignmentFlag.AlignCenter)

        button = QPushButton("Ok")
        button.clicked.connect(self.get)
        layout.addWidget(button)

        self.label = QLabel("")


        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.adjustSize()
        layout.addWidget(self.label)



        button = QPushButton("Quitter")
        button.clicked.connect(self.close)
        layout.addWidget(button)

    def get(self):
        text = f"Bonjour {self.input.text()}"
        self.label.setText(text)
        print(text)



app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())