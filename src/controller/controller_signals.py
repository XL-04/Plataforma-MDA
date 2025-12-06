import numpy as np
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from Model.signals.model_signals import ModelSignals


class ControllerSignals:

    def __init__(self, view):
        self.view = view
        self.model = ModelSignals()

        self.signal = None
        self.freqs = None
        self.fft_vals = None

        # Conectar botones de la interfaz
        self.view.btnLoadMat.clicked.connect(self.load_mat)
        self.view.btnComputeFFT.clicked.connect(self.compute_fft)
        self.view.btnPlotChannel.clicked.connect(self.plot_channel)
        self.view.btnStd.clicked.connect(self.compute_std_histogram)

        # Canvas para graficar FFT
        self.canvas_fft = FigureCanvas(Figure(figsize=(4, 3)))
        self.view.layoutFFT.addWidget(self.canvas_fft)

        # Canvas para graficar histograma
        self.canvas_hist = FigureCanvas(Figure(figsize=(4, 3)))
        self.view.layoutHist.addWidget(self.canvas_hist)


    
    def load_mat(self):
        path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Seleccionar archivo .mat",
            "",
            "Archivos MAT (*.mat)"
        )

        if path:
            self.signal = self.model.load_mat(path)
            self.view.lblStatus.setText("Archivo .mat cargado correctamente")

            # Llenar comboBox con número de canales
            self.view.comboChannels.clear()
            for i in range(self.signal.shape[1]):
                self.view.comboChannels.addItem(f"Canal {i}")



    def compute_fft(self):
        if self.signal is None:
            self.view.lblStatus.setText("Primero cargue una señal .mat")
            return

        # Calcular FFT
        self.freqs, self.fft_vals = self.model.compute_fft(self.signal)

        # Obtener frecuencias dominantes
        df = self.model.get_dominant_frequencies(self.freqs, self.fft_vals)

        # Guardar CSV automáticamente
        csv_path = self.model.save_csv(df)

        self.view.lblStatus.setText(f"FFT lista. Resultados guardados en: {csv_path}")

        # Mostrar DataFrame en tabla
        self.show_dataframe(df)


   
    def show_dataframe(self, df):
        self.view.tableFFT.setRowCount(df.shape[0])
        self.view.tableFFT.setColumnCount(df.shape[1])
        self.view.tableFFT.setHorizontalHeaderLabels(list(df.columns))

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                self.view.tableFFT.setItem(row, col, item)


    # ---------------------------------------------------
    # GRAFICAR ESPECTRO DE UN CANAL
    # ---------------------------------------------------
    def plot_channel(self):
        if self.freqs is None:
            self.view.lblStatus.setText("Primero compute la FFT")
            return

        ch = self.view.comboChannels.currentIndex()

        ax = self.canvas_fft.figure.subplots()
        ax.clear()
        ax.plot(self.freqs, self.fft_vals[:, ch])
        ax.set_title(f"Espectro de Frecuencia - Canal {ch}")
        ax.set_xlabel("Frecuencia (Hz)")
        ax.set_ylabel("Magnitud")
        self.canvas_fft.draw()

        self.view.lblStatus.setText(f"Gráfico del canal {ch} generado.")


    def compute_std_histogram(self):
        if self.signal is None:
            self.view.lblStatus.setText("Primero cargue una señal .mat")
            return

        std_vals = self.model.compute_std(self.signal)

        ax = self.canvas_hist.figure.subplots()
        ax.clear()
        ax.hist(std_vals, bins="auto")
        ax.set_title("Histograma de Desviación Estándar por Canal")
        ax.set_xlabel("Valor STD")
        ax.set_ylabel("Frecuencia")
        self.canvas_hist.draw()

        self.view.lblStatus.setText("Histograma generado correctamente.")
