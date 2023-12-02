from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
import sys
import socket
import os

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 300)
        self.setWindowTitle("Application avec Sockets")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Messages:")
        layout.addWidget(self.label)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)

        self.input = QLineEdit()
        self.input.setFixedWidth(500)
        layout.addWidget(self.input, alignment=Qt.AlignmentFlag.AlignCenter)

        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        # cette partie permet de gérer la réception des msgs
        self.message_thread = MessageThread(self)
        self.message_thread.message_received.connect(self.update_message_display)
        self.message_thread.start()

    def send_message(self):
        message = self.input.text()
        self.message_thread.send_message(message)
        self.input.clear()

    def update_message_display(self, message):
        current_text = self.message_display.toPlainText()
        self.message_display.setPlainText(f"{current_text}\n{message}")

class MessageThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.host = input("Entrez l'IP du serveur: ")
        self.port = 12222
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def run(self):
        while True:
            try:
                reply = self.s.recv(1024).decode()
                if not reply:
                    break
                if reply == 'bye':
                    print("Bye!")
                    break
                elif reply == 'arret':
                    os._exit(0)
                else:
                    print(f"Serveur dit: {reply}")
                    self.message_received.emit(f"{reply}")
            except Exception as e:
                print(f"Erreur de réception: {e}")
                break

    def send_message(self, message):
        try:
            self.s.send(message.encode())
        except Exception as e:
            print(f"Erreur d'envoi: {e}")

    def __del__(self):
        self.s.close()

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
