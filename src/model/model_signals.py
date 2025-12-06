import os
import numpy as np
import pandas as pd
import scipy.io as sio

from scipy.signal import find_peaks

class ModelSignals:

    def __init__(self):
        self.results_dir = "results/signals"

        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
   
    def load_mat(self, path):
        mat = sio.loadmat(path)
        key = [k for k in mat.keys() if not k.startswith("__")][0]
        signal = mat[key]

        # Asegurar forma (samples, channels)
        if signal.ndim == 1:
            signal = signal.reshape(-1, 1)

        return signal

   
    def compute_fft(self, signal, fs=250):
        n = signal.shape[0]
        freqs = np.fft.rfftfreq(n, 1/fs)
        fft_vals = np.abs(np.fft.rfft(signal, axis=0))
        return freqs, fft_vals

  
  
    def get_dominant_frequencies(self, freqs, fft_vals, num_peaks=3):
        results = []

        for ch in range(fft_vals.shape[1]):
            peaks, _ = find_peaks(fft_vals[:, ch])
            peak_freqs = freqs[peaks]
            peak_magnitudes = fft_vals[peaks, ch]

            # Ordenar mayores magnitudes
            idx = np.argsort(peak_magnitudes)[::-1][:num_peaks]

            for i in idx:
                results.append({
                    "Canal": ch,
                    "Frecuencia": peak_freqs[i],
                    "Magnitud": peak_magnitudes[i]
                })

        df = pd.DataFrame(results)
        return df

    
    def save_csv(self, df):
        path = f"{self.results_dir}/dominant_frequencies.csv"
        df.to_csv(path, index=False)
        return path

  
    
    def compute_std(self, signal):
        std_vals = np.std(signal, axis=0)
        return std_vals

   
    # DATOS histo
   
    def std_histogram_data(self, std_vals):
        # bins automáticos
        return np.histogram(std_vals, bins="auto")
