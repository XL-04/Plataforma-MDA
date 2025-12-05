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
        self.users_xml = "config/users.xml"
        self.temp_dir = "temp"

        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    # -------------------------------------------------------
    # VALIDACIÓN DE USUARIO POR XML
    # -------------------------------------------------------
    def validate_user(self, username, password):
        try:
            tree = ET.parse(self.users_xml)
            root = tree.getroot()

            for user in root.findall("user"):
                usr = user.find("username").text
                pwd = user.find("password").text

                if usr == username and pwd == password:
                    return True
        except:
            return False

        return False

    # -------------------------------------------------------
    # PROCESAR DICOM
    # -------------------------------------------------------
    def process_dicom(self, path):
        dcm = pydicom.dcmread(path)

        img = dcm.pixel_array.astype(np.int16)
        slope = float(dcm.RescaleSlope)
        intercept = float(dcm.RescaleIntercept)

        img = img * slope + intercept

        img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        img_norm = img_norm.astype(np.uint8)

        patient_info = f"DICOM: {getattr(dcm, 'PatientName', 'Anon')}"
        return img_norm, patient_info

    # -------------------------------------------------------
    # PNG / JPG
    # -------------------------------------------------------
    def process_png(self, path):
        return cv2.imread(path)

    # -------------------------------------------------------
    # SEÑALES .MAT
    # -------------------------------------------------------
    def process_signal(self, path):
        mat = sio.loadmat(path)

        # detect first array
        key = [k for k in mat.keys() if not k.startswith("__")][0]
        signal = mat[key]

        # FFT
        fft_vals = np.abs(np.fft.rfft(signal, axis=0))

        df = pd.DataFrame(fft_vals)
        return df

    # -------------------------------------------------------
    # CSV TABULAR
    # -------------------------------------------------------
    def load_csv(self, path):
        return pd.read_csv(path)

    # -------------------------------------------------------
    # CAPTURA DE WEBCAM
    # -------------------------------------------------------
    def capture_image(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return None

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        filename = f"{self.temp_dir}/capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(filename, gray)

        return filename
