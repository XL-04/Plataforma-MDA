from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QPixmap
import cv2

class MainView(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)

    # -------------------------------------------------------
    def open_file_dialog(self, filters):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", filters)
        return path

    # -------------------------------------------------------
    def show_image(self, img):
        # Convertir imagen a pixmap
        height, width = img.shape[:2]
        bytes_per_line = width
        q_image = QPixmap.fromImage(
            QPixmap(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        )
        self.label_image.setPixmap(q_image)

    # -------------------------------------------------------
    def show_table(self, df):
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
