import os
from PyQt5.QtWidgets import QFileDialog

def open_dialog(filter_text):
    path, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo", "", filter_text)
    return path
