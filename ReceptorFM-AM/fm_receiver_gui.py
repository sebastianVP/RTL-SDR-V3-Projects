# FM Receiver GUI with Waterfall/Spectrogram
# Full implementation using PyQt5 + Matplotlib integrated with RTL-SDR (pyrtlsdr).
# Features:
# - Start/Stop capture
# - Frequency, sample_rate and gain controls
# - Real-time FFT (spectrum) and waterfall (spectrogram)
# - FM demodulation and audio playback
# Notes: Ensure librtlsdr is installed and accessible (librtlsdr.dll on Windows).

import sys
import time
import numpy as np
from collections import deque
from rtlsdr import RtlSdr
import sounddevice as sd
from scipy.signal import butter, lfilter, decimate

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QMessageBox, QSlider
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -----------------------
# DSP helpers
# -----------------------

def bandpass(sig, lowcut, highcut, fs, order=5):
    b, a = butter(order, [lowcut/(fs/2), highcut/(fs/2)], btype='band')
    return lfilter(b, a, sig)


def lowpass(sig, cutoff, fs, order=5):
    b, a = butter(order, cutoff/(fs/2), btype='low')
    return lfilter(b, a, sig)


def fm_demod(iq):
    # phase discriminator
    return np.angle(iq[1:] * np.conj(iq[:-1]))


def deemphasis_filter(audio, fs):
    # 75 microseconds (Americas) de-emphasis implemented as single-pole IIR
    tau = 75e-6
    alpha = fs * tau
    b = [1]
    a = [alpha + 1, -alpha]
    return lfilter(b, a, audio)

# -----------------------
# SDR Worker Thread
# -----------------------

class SDRWorker(QThread):
    spectrum_ready = pyqtSignal(np.ndarray)
    waterfall_ready = pyqtSignal(np.ndarray)
    audio_ready = pyqtSignal(np.ndarray)
    status = pyqtSignal(str)

    def __init__(self, center_freq=107.7e6, sample_rate=2.4e6, gain='auto', fft_size=16384, waterfall_rows=256, parent=None):
        super().__init__(parent)
        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.gain = gain
        self.fft_size = fft_size
        self.waterfall_rows = waterfall_rows
        self._running = False
        self.sdr = None

        # waterfall buffer: will emit the whole image occasionally
        self.waterfall = np.zeros((self.waterfall_rows, int(self.fft_size/2)), dtype=np.float32)

    def configure(self, center_freq=None, sample_rate=None, gain=None):
        if center_freq is not None:
            self.center_freq = center_freq
        if sample_rate is not None:
            self.sample_rate = sample_rate
        if gain is not None:
            self.gain = gain

    def stop(self):
        self._running = False

    def run(self):
        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.center_freq
            self.sdr.gain = self.gain
        except Exception as e:
            self.status.emit(f"Error initializing SDR: {e}")
            return

        self._running = True
        self.status.emit("SDR started")

        # chunk size chosen to be manageable memory-wise
        chunk = 256 * 1024
        fft_n = self.fft_size
        window = np.hanning(fft_n)

        while self._running:
            try:
                samples = self.sdr.read_samples(chunk)
            except Exception as e:
                self.status.emit(f"Read error: {e}")
                break

            # pick last fft_n for spectrum to stay responsive
            if len(samples) < fft_n:
                continue

            frame = samples[-fft_n:]

            # compute FFT (power)
            spec = np.fft.fftshift(np.fft.fft(frame * window))
            power = 20 * np.log10(np.abs(spec) + 1e-12)
            half = power[int(len(power)/2):]  # positive frequencies

            # normalize for display
            pnorm = (half - np.max(half))
            self.spectrum_ready.emit(pnorm)

            # update waterfall by rolling and placing newest row
            row = np.copy(pnorm)
            self.waterfall = np.roll(self.waterfall, -1, axis=0)
            # resize/trim row to fit if necessary
            if row.shape[0] != self.waterfall.shape[1]:
                # interpolate or trim
                row = np.interp(np.linspace(0, len(row)-1, self.waterfall.shape[1]), np.arange(len(row)), row)
            self.waterfall[-1, :] = row
            self.waterfall_ready.emit(self.waterfall)

            # FM audio path: demodulate portion around center
            try:
                # take smaller block for audio
                audio_block = frame
                # bandpass near 50kHz bandwidth around center
                audio_bp = bandpass(audio_block, 30e3, 110e3, self.sample_rate)
                demod = fm_demod(audio_bp)
                audio_lp = lowpass(demod, 16000, self.sample_rate)

                # decimate: reduce sample rate stepwise to target audio 48000
                decim_factor = int(self.sample_rate / 240000)  # to 240k
                if decim_factor < 1:
                    decim_factor = 1
                audio1 = decimate(audio_lp, decim_factor)

                # apply deemphasis
                fs1 = int(self.sample_rate / decim_factor)
                audio1 = deemphasis_filter(audio1, fs1)

                # final decimation to 48k
                final_factor = max(1, int(fs1 / 48000))
                audio_final = decimate(audio1, final_factor)

                # normalize
                if np.max(np.abs(audio_final)) > 0:
                    audio_final = audio_final / np.max(np.abs(audio_final)) * 0.6
                # convert to float32
                audio_final = audio_final.astype(np.float32)

                # emit audio
                self.audio_ready.emit(audio_final)
            except Exception as e:
                # non-fatal for visualization
                self.status.emit(f"Audio pipeline error: {e}")

        # cleanup
        try:
            if self.sdr:
                self.sdr.close()
        except Exception:
            pass
        self.status.emit("SDR stopped")

# -----------------------
# GUI
# -----------------------

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        fig.tight_layout()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTL-SDR FM Receiver (GUI)")

        # default settings
        self.center_freq = 107.7e6
        self.sample_rate = 2.4e6
        self.gain = 'auto'

        # SDR worker
        self.worker = SDRWorker(center_freq=self.center_freq, sample_rate=self.sample_rate, gain=self.gain)
        self.worker.spectrum_ready.connect(self.update_spectrum)
        self.worker.waterfall_ready.connect(self.update_waterfall)
        self.worker.audio_ready.connect(self.play_audio)
        self.worker.status.connect(self.on_status)

        # UI elements
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        controls = QHBoxLayout()

        controls.addWidget(QLabel("Freq (MHz):"))
        self.freq_edit = QLineEdit(str(self.center_freq/1e6))
        controls.addWidget(self.freq_edit)

        controls.addWidget(QLabel("Sample rate (MS/s):"))
        self.sr_combo = QComboBox()
        self.sr_combo.addItems(["2.4", "1.024", "0.5"])  # in MS/s
        self.sr_combo.setCurrentIndex(0)
        controls.addWidget(self.sr_combo)

        controls.addWidget(QLabel("Gain:"))
        self.gain_combo = QComboBox()
        self.gain_combo.addItems(["auto", "0", "10", "20"]) 
        controls.addWidget(self.gain_combo)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.on_start)
        controls.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        controls.addWidget(self.stop_btn)

        main_layout.addLayout(controls)

        plots = QHBoxLayout()

        # Spectrum plot
        self.spec_canvas = MplCanvas(self, width=5, height=3)
        self.spec_line, = self.spec_canvas.ax.plot([], [])
        self.spec_canvas.ax.set_title("Spectrum (dB)")
        self.spec_canvas.ax.set_xlabel("Frequency bin")
        plots.addWidget(self.spec_canvas)

        # Waterfall
        self.wf_canvas = MplCanvas(self, width=5, height=3)
        self.wf_im = self.wf_canvas.ax.imshow(np.zeros((256, int(self.worker.fft_size/2))), aspect='auto', origin='lower')
        self.wf_canvas.ax.set_title("Waterfall")
        plots.addWidget(self.wf_canvas)

        main_layout.addLayout(plots)

        # status
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        central.setLayout(main_layout)

        # audio playback queue
        self.audio_queue = deque()
        self.audio_timer = QTimer()
        self.audio_timer.setInterval(200)  # ms
        self.audio_timer.timeout.connect(self.audio_playback_loop)

        self.show()

    def on_start(self):
        try:
            freq = float(self.freq_edit.text()) * 1e6
        except ValueError:
            QMessageBox.critical(self, "Error", "Frecuencia inválida")
            return
        self.center_freq = freq
        sr = float(self.sr_combo.currentText()) * 1e6
        self.sample_rate = sr
        gain = self.gain_combo.currentText()

        # configure worker and start
        self.worker.configure(center_freq=self.center_freq, sample_rate=self.sample_rate, gain=gain)
        if not self.worker.isRunning():
            self.worker.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.audio_timer.start()
        self.status_label.setText("Running")

    def on_stop(self):
        self.worker.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.audio_timer.stop()
        self.status_label.setText("Stopped")

    def update_spectrum(self, spec):
        x = np.arange(len(spec))
        self.spec_line.set_data(x, spec)
        self.spec_canvas.ax.relim()
        self.spec_canvas.ax.autoscale_view()
        self.spec_canvas.draw()

    def update_waterfall(self, wf):
        # update image
        self.wf_im.set_data(wf)
        self.wf_canvas.draw()

    def play_audio(self, audio):
        # enqueue audio buffer
        self.audio_queue.append(audio)

    def audio_playback_loop(self):
        if not self.audio_queue:
            return
        buffer = self.audio_queue.popleft()
        try:
            sd.play(buffer, 48000, blocking=False)
        except Exception as e:
            self.status_label.setText(f"Audio error: {e}")

    def on_status(self, msg):
        self.status_label.setText(msg)

# -----------------------
# Run app
# -----------------------

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
