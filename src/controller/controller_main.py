from PyQt5.QtWidgets import QMessageBox
from src.view.login_view import LoginView
from src.view.main_view import MainView
from src.model.model_core import ModelCore
from src.utils.db import MongoManager

# Vista procesar imagenes
from src.view.procesar_imagenes_view import ProcesarImagenesView


class MainController:

    def __init__(self):
        self.model = ModelCore()

        # Login
        self.login_view = LoginView()
        self.login_view.login_button.clicked.connect(self.validate_login)

        # Main
        self.main_view = None

        # Vista de procesar imagen
        self.procesar_view = None

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

        # Conexión de botones
        self.main_view.btn_load_dicom.clicked.connect(self.load_dicom)
        self.main_view.btn_load_png.clicked.connect(self.load_png)
        self.main_view.btn_load_signal.clicked.connect(self.load_signal)
        self.main_view.btn_load_csv.clicked.connect(self.load_csv)
        self.main_view.btn_capture.clicked.connect(self.capture_webcam)

        # Mostrar usuario
        self.main_view.label_user.setText(f"Usuario: {username}")

        self.login_view.close()
        self.main_view.show()

    def load_dicom(self):
        path = self.main_view.open_file_dialog("DICOM (*.dcm)")
        if not path:
            return
        try:
            img, meta_df, ds = self.model.process_dicom(path)
            # Mostrar imagen y metadata
            self.main_view.show_image(img)
            try:
                self.main_view.show_table(meta_df)
            except Exception:
                pass
            self.db.log_event(path, "Cargar DICOM")
        except Exception as e:
            QMessageBox.critical(None, "Error DICOM", str(e))

    def load_png(self):
        path = self.main_view.open_file_dialog("Imagen (*.png *.jpg *.jpeg)")
        if not path:
            return
        try:
            img = self.model.process_png(path)
            if img is None:
                raise FileNotFoundError("No se pudo leer la imagen")
            self.main_view.show_image(img)
            self.db.log_event(path, "Cargar PNG/JPG")
            # Abrir interfaz procesar imagen
            self.open_procesar_imagenes(img)
        except Exception as e:
            QMessageBox.critical(None, "Error imagen", str(e))

    def load_signal(self):
        path = self.main_view.open_file_dialog("Archivo MAT (*.mat)")
        if not path:
            return
        try:
            df = self.model.process_signal(path)
            # df ya contiene filas (channel,freq,mag) -> mostramos en tabla
            self.main_view.show_table(df)
            self.db.log_event(path, "Cargar Señal")
        except Exception as e:
            QMessageBox.critical(None, "Error señal", str(e))

    def load_csv(self):
        path = self.main_view.open_file_dialog("CSV (*.csv)")
        if not path:
            return
        try:
            df = self.model.load_csv(path)
            self.main_view.show_table(df)
            self.db.log_event(path, "Cargar CSV")
        except Exception as e:
            QMessageBox.critical(None, "Error CSV", str(e))

    def capture_webcam(self):
        img_path = self.model.capture_image()
        if img_path:
            # Mostrar imagen capturada en la UI principal
            try:
                img = self.model.process_png(img_path)
                self.main_view.show_image(img)
            except Exception:
                pass
            QMessageBox.information(None, "OK", f"Imagen guardada en {img_path}")
            self.db.log_event(img_path, "Captura Webcam")
        else:
            QMessageBox.warning(None, "Error", "No se pudo acceder a la cámara")

    # Abrir ventana procesar imagenes
    def open_procesar_imagenes(self, img):
        self.procesar_view = ProcesarImagenesView()
        self.procesar_view.show()

        # Conectar botón "Volver"
        self.procesar_view.btn_volver.clicked.connect(self.cerrar_procesar)

        # Pasar imagen al widget de edición
        try:
            self.procesar_view.set_image(img)
        except:
            pass

    def cerrar_procesar(self):
        self.procesar_view.close()
