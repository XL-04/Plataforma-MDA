import sys
from PyQt5.QtWidgets import QApplication
from src.controller.controller_main import MainController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = MainController()
    controller.show_login()

    sys.exit(app.exec_())
