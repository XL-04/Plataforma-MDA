import os
import cv2
import pydicom
import numpy as np
import pandas as pd
import scipy.io as sio
from datetime import datetime
import xml.etree.ElementTree as ET

class ModelCore:

    def __init__(self):
        self.users_xml = os.path.join("config", "users.xml")
        self.temp_dir = os.path.join("temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs("results", exist_ok=True)

    # VALIDACIÓN DE USUARIO POR XML
    def validate_user(self, username, password):
        try:
            tree = ET.parse(self.users_xml)
            root = tree.getroot()
            for user in root.findall("user"):
                usr = user.find("username").text
                pwd = user.find("password").text
                if usr == username and pwd == password:
                    return True
        except Exception:
            return False
        return False

    # PROCESAR DICOM -> devuelve (imagen_uint8, metadata_df, raw_dataset)
    def process_dicom(self, path):
        ds = pydicom.dcmread(path)
        arr = ds.pixel_array.astype(np.float32)

        # Aplicar slope/intercept si existen (seguro)
        slope = float(getattr(ds, "RescaleSlope", 1.0))
        intercept = float(getattr(ds, "RescaleIntercept", 0.0))
        hu = arr * slope + intercept

        # Normalizar para visualización 0-255 uint8
        img_norm = cv2.normalize(hu, None, 0, 255, cv2.NORM_MINMAX)
        img_norm = img_norm.astype(np.uint8)

        # Extraer metadata relevante a DataFrame
        fields = [
            ("PatientID", getattr(ds, "PatientID", "")),
            ("PatientName", getattr(ds, "PatientName", "")),
            ("PatientAge", getattr(ds, "PatientAge", "")),
            ("PatientSex", getattr(ds, "PatientSex", "")),
            ("Modality", getattr(ds, "Modality", "")),
            ("StudyDate", getattr(ds, "StudyDate", "")),
            ("SeriesDescription", getattr(ds, "SeriesDescription", "")),
            ("Rows", getattr(ds, "Rows", "")),
            ("Columns", getattr(ds, "Columns", "")),
            ("RescaleIntercept", getattr(ds, "RescaleIntercept", "")),
            ("RescaleSlope", getattr(ds, "RescaleSlope", ""))
        ]
        meta_df = pd.DataFrame(fields, columns=["field", "value"])

        return img_norm, meta_df, ds

    # PNG / JPG devuelve imagen BGR (uint8)
    def process_png(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"No se pudo leer la imagen: {path}")
        return img

    # SEÑALES .MAT devuelve DataFrame con columnas ['channel','freq','mag']
    def process_signal(self, path, fs=1.0):
        """
        Carga archivo .mat. Encuentra la primera variable no privada y asume señal
        Puede manejar vectores o matrices (channels x samples) o (samples x channels).
        fs: frecuencia de muestreo (si no se conoce, se asume 1.0)
        Retorna DataFrame con filas por (channel, freq, mag) y además guarda CSV en results/.
        """
        m = sio.loadmat(path)
        arr = None
        for k, v in m.items():
            if k.startswith("__"):
                continue
            if isinstance(v, np.ndarray) and v.size > 0:
                arr = v
                break
        if arr is None:
            raise ValueError("No se encontró señal válida en el .mat")

        # Normalizar forma a (channels, samples)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        elif arr.ndim == 2:
            # Queremos shape (channels, samples). Heurística:
            if arr.shape[0] < arr.shape[1]:
                # asumimos (channels, samples)
                pass
            else:
                arr = arr.T

        results = []
        for ch_idx, ch in enumerate(arr):
            chf = np.asarray(ch, dtype=float).flatten()
            N = len(chf)
            if N < 2:
                continue
            yf = np.fft.rfft(chf)
            xf = np.fft.rfftfreq(N, d=1.0/fs)
            mag = (2.0 / N) * np.abs(yf)
            for i in range(len(xf)):
                results.append({"channel": int(ch_idx), "freq": float(xf[i]), "mag": float(mag[i])})

        df = pd.DataFrame(results)
        # Guardar CSV resumen (frecuencia con mayor magnitud por canal)
        summary = []
        for ch in df["channel"].unique():
            sub = df[df["channel"] == ch]
            idx = sub["mag"].idxmax()
            row = sub.loc[idx]
            summary.append({"channel": int(ch), "dom_freq": float(row["freq"]), "dom_mag": float(row["mag"])})
        summary_df = pd.DataFrame(summary)
        # Guardar archivos
        base = os.path.splitext(os.path.basename(path))[0]
        csv_path = os.path.join("results", f"{base}_fft.csv")
        summary_path = os.path.join("results", f"{base}_fft_summary.csv")
        df.to_csv(csv_path, index=False)
        summary_df.to_csv(summary_path, index=False)
        return df

    # CSV TABULAR
    def load_csv(self, path):
        return pd.read_csv(path)

    # CAPTURA DE WEBCAM -> devuelve ruta al archivo guardado
    def capture_image(self, cam_index=0):
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            return None
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return None
        # Guardar en color (BGR) para mantener compatibilidad con main_view.show_image
        filename = os.path.join(self.temp_dir, f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        cv2.imwrite(filename, frame)
        return filename
