import sys
import os
from PyQt5.QtWidgets import QApplication
from src.controller.controller_main import MainController

if __name__ == "__main__":
    # Asegurar ruta absoluta
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(base_path)

    app = QApplication(sys.argv)

    controller = MainController()
    controller.show_login()

    sys.exit(app.exec_())
