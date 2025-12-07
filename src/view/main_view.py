import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QPushButton, QLabel, QTableWidget
from PyQt5.QtGui import QPixmap
import cv2

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ruta real del UI
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        ui_path = os.path.join(base, "ui", "main_window.ui")

        uic.loadUi(ui_path, self)

        # Widgets del UI
        self.btn_load_dicom = self.findChild(QPushButton, "btn_load_dicom")
        self.btn_load_png = self.findChild(QPushButton, "btn_load_png")
        self.btn_load_signal = self.findChild(QPushButton, "btn_load_signal")
        self.btn_load_csv = self.findChild(QPushButton, "btn_load_csv")
        self.btn_capture = self.findChild(QPushButton, "btn_capture")

        self.label_user = self.findChild(QLabel, "label_user")
        self.label_image = self.findChild(QLabel, "label_image")
        self.tableWidget = self.findChild(QTableWidget, "tableWidget")

    # Abrir archivo
    def open_file_dialog(self, filters):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", filters)
        return path

    # Mostrar imagen en label_image
    def show_image(self, img):
        if img is None:
            return

        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        from PyQt5.QtGui import QImage
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        self.label_image.setPixmap(pixmap)

    # Mostrar tabla
    def show_table(self, df):
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
