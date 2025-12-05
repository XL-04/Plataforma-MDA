from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/login.ui", self)

        self.user_input = self.findChild(QLineEdit, "user_input")
        self.pass_input = self.findChild(QLineEdit, "pass_input")
        self.login_button = self.findChild(QPushButton, "login_button")
