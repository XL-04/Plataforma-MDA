from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QImage
import cv2


class ProcesarImagenesView(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/procesar_imagenes.ui", self)

        # Buscar QLabel donde se mostrará la imagen
        self.label_preview = self.findChild(QLabel, "label_preview")

        if self.label_preview is None:
            print("⚠ ERROR: No existe un QLabel llamado 'label_preview' en procesar_imagenes.ui")

    def set_image(self, img):
        if img is None:
            return

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        if self.label_preview:
            self.label_preview.setPixmap(pixmap)
            self.label_preview.setScaledContents(True)
