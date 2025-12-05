import os
from PyQt5.QtWidgets import QMessageBox

from src.view.login_view import LoginView
from src.view.main_view import MainView
from src.model.model_core import ModelCore
from src.utils.db import MongoManager


class MainController:

    def __init__(self):
        # MODELO principal
        self.model = ModelCore()

        # Vista de login
        self.login_view = LoginView()
        self.login_view.login_button.clicked.connect(self.validate_login)

        # Vista principal (se crea después de login exitoso)
        self.main_view = None

        # Base de Datos Mongo
        self.db = MongoManager()

    def show_login(self):
        self.login_view.show()

    # -------------------------------------------------------
    # VALIDAR LOGIN CON XML
    # -------------------------------------------------------
    def validate_login(self):
        username = self.login_view.user_input.text()
        password = self.login_view.pass_input.text()

        if self.model.validate_user(username, password):
            self.db.log_event(username, "Login exitoso")
            self.open_main_window(username)
        else:
            QMessageBox.warning(None, "Error", "Usuario o contraseña incorrectos")

    # -------------------------------------------------------
    # ABRIR VENTANA PRINCIPAL
    # -------------------------------------------------------
    def open_main_window(self, username):
        self.main_view = MainView()

        # Conectar botones a funciones del modelo
        self.main_view.btn_load_dicom.clicked.connect(self.load_dicom)
        self.main_view.btn_load_png.clicked.connect(self.load_png)
        self.main_view.btn_load_signal.clicked.connect(self.load_signal)
        self.main_view.btn_load_csv.clicked.connect(self.load_csv)
        self.main_view.btn_capture.clicked.connect(self.capture_webcam)

        self.main_view.label_user.setText(f"Usuario activo: {username}")

        self.login_view.close()
        self.main_view.show()

    # -------------------------------------------------------
    # PROCESAMIENTO DE IMÁGENES AMIGABLE
    # -------------------------------------------------------
    def load_dicom(self):
        path = self.main_view.open_file_dialog("DICOM (*.dcm)")
        if not path:
            return

        img, info = self.model.process_dicom(path)
        self.main_view.show_image(img)
        self.db.log_event(info, "DICOM cargado")

    def load_png(self):
        path = self.main_view.open_file_dialog("Imagen (*.png *.jpg *.jpeg)")
        if not path:
            return

        img = self.model.process_png(path)
        self.main_view.show_image(img)
        self.db.log_event(path, "PNG/JPG cargado")

    # -------------------------------------------------------
    # PROCESAMIENTO DE SEÑALES
    # -------------------------------------------------------
    def load_signal(self):
        path = self.main_view.open_file_dialog("Archivo MAT (*.mat)")
        if not path:
            return

        df = self.model.process_signal(path)
        self.main_view.show_table(df)
        self.db.log_event(path, "Señal MAT cargada")

    # -------------------------------------------------------
    # CSV TABULAR
    # -------------------------------------------------------
    def load_csv(self):
        path = self.main_view.open_file_dialog("CSV (*.csv)")
        if not path:
            return

        df = self.model.load_csv(path)
        self.main_view.show_table(df)
        self.db.log_event(path, "CSV cargado")

    # -------------------------------------------------------
    # CAPTURA DE WEBCAM
    # -------------------------------------------------------
    def capture_webcam(self):
        img_path = self.model.capture_image()

        if img_path:
            self.db.log_event(img_path, "Captura de webcam")
            QMessageBox.information(None, "OK", f"Imagen guardada en:\n{img_path}")
        else:
            QMessageBox.warning(None, "Error", "No se pudo capturar la imagen")
