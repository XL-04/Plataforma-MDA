import os
import cv2
import numpy as np
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QImage


class ProcesarImagenesView(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/procesar_imagenes.ui", self)

        # QLabel donde se mostrará la imagen
        self.label_preview = self.findChild(QLabel, "label_preview")

        # Tabla de datos
        self.tableWidget = self.findChild(QTableWidget, "tableWidget")

        # BOTONES
        self.btn_cargar_img = self.findChild(QPushButton, "btn_cargar_img")
        self.btn_cargar_dicom = self.findChild(QPushButton, "btn_cargar_dicom")
        self.btn_cargar_csv = self.findChild(QPushButton, "btn_cargar_csv")
        self.btn_cargar_mat = self.findChild(QPushButton, "btn_cargar_mat")

        self.btn_gray = self.findChild(QPushButton, "btn_gray")
        self.btn_blur = self.findChild(QPushButton, "btn_blur")
        self.btn_binary = self.findChild(QPushButton, "btn_binary")
        self.btn_edges = self.findChild(QPushButton, "btn_edges")
        self.btn_dilate = self.findChild(QPushButton, "btn_dilate")
        self.btn_erode = self.findChild(QPushButton, "btn_erode")

        self.btn_guardar = self.findChild(QPushButton, "btn_guardar")

        # Conectar señales
        if self.btn_cargar_img:
            self.btn_cargar_img.clicked.connect(self.cargar_imagen)
        if self.btn_cargar_dicom:
            self.btn_cargar_dicom.clicked.connect(self.cargar_dicom)
        if self.btn_cargar_csv:
            self.btn_cargar_csv.clicked.connect(self.cargar_csv)
        if self.btn_cargar_mat:
            self.btn_cargar_mat.clicked.connect(self.cargar_mat)

        # Procesamiento
        if self.btn_gray:
            self.btn_gray.clicked.connect(self.convert_gray)
        if self.btn_blur:
            self.btn_blur.clicked.connect(self.apply_blur)
        if self.btn_binary:
            self.btn_binary.clicked.connect(self.apply_binary)
        if self.btn_edges:
            self.btn_edges.clicked.connect(self.detect_edges)
        if self.btn_dilate:
            self.btn_dilate.clicked.connect(self.apply_dilate)
        if self.btn_erode:
            self.btn_erode.clicked.connect(self.apply_erode)

        if self.btn_guardar:
            self.btn_guardar.clicked.connect(self.guardar_resultado)

        # Variables internas
        self.img = None
        self.original_img = None
        self.current_table = None         # tabla cargada (CSV o señales)
        self.current_metadata = None      # metadata DICOM


    # Utilidades para mostrar imagen y tabla
    def show_image(self, img):
        if img is None:
            return
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        if self.label_preview:
            self.label_preview.setPixmap(pixmap)
            self.label_preview.setScaledContents(True)


    # método para recibir imagen desde MainController
    def set_image(self, img):
        """Recibe imagen desde MainController"""
        self.img = img.copy()
        self.original_img = img.copy()
        self.show_image(img)


    # Carga de archivos
    def cargar_imagen(self):
        path, _ = QFileDialog.getOpenFileName(self, "Cargar imagen", "", "Imagen (*.png *.jpg *.jpeg)")
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            QMessageBox.warning(self, "Error", "No se pudo cargar la imagen")
            return
        self.set_image(img)

    def cargar_dicom(self):
        import pydicom
        path, _ = QFileDialog.getOpenFileName(self, "Cargar DICOM", "", "DICOM (*.dcm)")
        if not path:
            return

        dcm = pydicom.dcmread(path)
        arr = dcm.pixel_array.astype(np.float32)

        slope = float(getattr(dcm, "RescaleSlope", 1.0))
        intercept = float(getattr(dcm, "RescaleIntercept", 0.0))
        img = arr * slope + intercept

        img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        img_norm = img_norm.astype(np.uint8)
        img_norm = cv2.cvtColor(img_norm, cv2.COLOR_GRAY2BGR)

        # Guardar imagen y metadata
        self.set_image(img_norm)

        meta = []
        for attr in ["PatientID", "PatientName", "PatientAge", "PatientSex", "Modality"]:
            meta.append([attr, str(getattr(dcm, attr, ""))])

        df = pd.DataFrame(meta, columns=["Campo", "Valor"])
        self.current_metadata = df
        self.show_table(df)

    def cargar_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Cargar CSV", "", "CSV (*.csv)")
        if not path:
            return
        df = pd.read_csv(path)
        self.current_table = df
        self.show_table(df)

    def cargar_mat(self):
        import scipy.io as sio
        path, _ = QFileDialog.getOpenFileName(self, "Cargar Señal", "", "MAT (*.mat)")
        if not path:
            return

        data = sio.loadmat(path)
        key = [k for k in data.keys() if not k.startswith("__")][0]
        signal = np.asarray(data[key]).flatten()

        # FFT
        fft_vals = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal))

        df = pd.DataFrame({"Frecuencia": freqs, "Magnitud": fft_vals})
        self.current_table = df
        self.show_table(df)


    # Mostrar tabla
    def show_table(self, df):
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))


    # Procesamiento de imagen
    def convert_gray(self):
        if self.img is None:
            return
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        self.show_image(self.img)

    def apply_blur(self):
        if self.img is None:
            return
        blurred = cv2.GaussianBlur(self.img, (7, 7), 0)
        self.img = blurred
        self.show_image(self.img)

    def apply_binary(self):
        if self.img is None:
            return
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        self.img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.show_image(self.img)

    def detect_edges(self):
        if self.img is None:
            return
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        self.img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.show_image(self.img)

    def apply_dilate(self):
        if self.img is None:
            return
        kernel = np.ones((5, 5), np.uint8)
        self.img = cv2.dilate(self.img, kernel, iterations=1)
        self.show_image(self.img)

    def apply_erode(self):
        if self.img is None:
            return
        kernel = np.ones((5, 5), np.uint8)
        self.img = cv2.erode(self.img, kernel, iterations=1)
        self.show_image(self.img)


    # Guardar resultado
    def guardar_resultado(self):
        if self.img is None:
            QMessageBox.warning(self, "Error", "No hay imagen para guardar")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", "", "PNG (*.png)")
        if not path:
            return

        cv2.imwrite(path, self.img)
        QMessageBox.information(self, "Guardado", f"Imagen guardada en:\n{path}")
