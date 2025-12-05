from PyQt5.QtWidgets import QMessageBox
from src.view.login_view import LoginView
from src.view.main_view import MainView
from src.model.model_core import ModelCore
from src.utils.db import MongoManager

class MainController:

    def __init__(self):
        self.model = ModelCore()

        # Login
        self.login_view = LoginView()
        self.login_view.login_button.clicked.connect(self.validate_login)

        # Main
        self.main_view = None

        # BD
        self.db = MongoManager()

    def show_login(self):
        self.login_view.show()

    def validate_login(self):
        username = self.login_view.user_input.text()
        password = self.login_view.pass_input.text()

        if self.model.validate_user(username, password):
            self.db.log_event(username, "Login exitoso")
            self.open_main_window(username)
        else:
            QMessageBox.warning(None, "Error", "Usuario o contraseña incorrectos")

    def open_main_window(self, username):
        self.main_view = MainView()

        # Conexiones con botones
        self.main_view.btn_load_dicom.clicked.connect(self.load_dicom)
        self.main_view.btn_load_png.clicked.connect(self.load_png)
        self.main_view.btn_load_signal.clicked.connect(self.load_signal)
        self.main_view.btn_load_csv.clicked.connect(self.load_csv)
        self.main_view.btn_capture.clicked.connect(self.capture_webcam)

        self.main_view.label_user.setText(f"Usuario: {username}")

        self.login_view.close()
        self.main_view.show()

    def load_dicom(self):
        path = self.main_view.open_file_dialog("DICOM (*.dcm)")
        if path:
            img, info = self.model.process_dicom(path)
            self.main_view.show_image(img)
            self.db.log_event(path, "Cargar DICOM")

    def load_png(self):
        path = self.main_view.open_file_dialog("Imagen (*.png *.jpg *.jpeg)")
        if path:
            img = self.model.process_png(path)
            self.main_view.show_image(img)
            self.db.log_event(path, "Cargar PNG/JPG")

    def load_signal(self):
        path = self.main_view.open_file_dialog("Archivo MAT (*.mat)")
        if path:
            df = self.model.process_signal(path)
            self.main_view.show_table(df)
            self.db.log_event(path, "Cargar Señal")

    def load_csv(self):
        path = self.main_view.open_file_dialog("CSV (*.csv)")
        if path:
            df = self.model.load_csv(path)
            self.main_view.show_table(df)
            self.db.log_event(path, "Cargar CSV")

    def capture_webcam(self):
        img_path = self.model.capture_image()
        if img_path:
            QMessageBox.information(None, "OK", f"Imagen guardada en {img_path}")
            self.db.log_event(img_path, "Captura Webcam")
