import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
from scipy.signal import butter, lfilter
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def lowpass(sig, cutoff, fs, order=4):
    b, a = butter(order, cutoff / (fs/2), btype='low')
    return lfilter(b, a, sig)

def fm_demodulate(iq):
    phase = np.unwrap(np.angle(iq))
    return np.diff(phase)

def main():
    sdr = RtlSdr()

    sdr.sample_rate = 2.4e6
    sdr.center_freq = 107.7e6      # <-- pon aquí la FM local
    sdr.gain = 'auto'

    print("🔊 Recibiendo FM... CTRL+C para parar.")

    while True:
        samples = sdr.read_samples(256*1024)

        # FM demod
        demod = fm_demodulate(samples)

        # Low-pass para audio (15 kHz)
        audio = lowpass(demod, 15000, sdr.sample_rate - 1)

        # Downsample a audio (48 kHz)
        decim = int((sdr.sample_rate - 1) / 48000)
        audio = audio[::decim]
        #sd.default.device = 11

        sd.play(audio, 48000)
        sd.wait()

    sdr.close()

if __name__ == "__main__":
    main()
