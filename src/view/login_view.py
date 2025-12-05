from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

class LoginView(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/login.ui", self)

        self.user_input = self.findChild(type(self.user_input), "user_input")
        self.pass_input = self.findChild(type(self.pass_input), "pass_input")
        self.login_button = self.findChild(type(self.login_button), "login_button")
