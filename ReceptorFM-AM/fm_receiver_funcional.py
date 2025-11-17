import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
from scipy.signal import butter, lfilter, decimate

# -----------------------
# FILTROS
# -----------------------

def lowpass(sig, cutoff, fs, order=5):
    b, a = butter(order, cutoff / (fs/2), btype='low')
    return lfilter(b, a, sig)

def bandpass(sig, lowcut, highcut, fs, order=5):
    b, a = butter(order, [lowcut/(fs/2), highcut/(fs/2)], btype='band')
    return lfilter(b, a, sig)

# -----------------------
# DEMODULACIÓN FM
# -----------------------

def fm_demod(iq):
    return np.angle(iq[1:] * np.conj(iq[:-1]))

def deemphasis_filter(audio, fs):
    # 75 microsegundos para América
    tau = 75e-6
    alpha = fs * tau
    b = [1]
    a = [alpha + 1, -alpha]
    return lfilter(b, a, audio)

# -----------------------
# MAIN RECEIVER
# -----------------------

def main():
    sdr = RtlSdr()

    sdr.sample_rate = 2.4e6
    sdr.center_freq = 107.7e6   # Cambia tu emisora
    sdr.gain = 'auto'

    print("🎧 Escuchando FM... CTRL+C para detener.")

    while True:
        samples = sdr.read_samples(256*1024)

        # 1. Filtrado: dejar banda de FM (~200 kHz) 
        """
        El audio FM ocupa ~200 kHz, NO 80 kHz.
        Estás filtrando una banda demasiado angosta → pierdes la señal completa → demod salen ceros.
        ✔ Banda correcta de FM comercial: ~100 kHz a cada lado
        El filtro correcto sería:
        """
        filtered = bandpass(samples, 30e3, 200e3, sdr.sample_rate)

        # 2. Demodulación FM
        demod = fm_demod(filtered)

        # 3. Low-pass audio 15 kHz
        audio = lowpass(demod, 16000, sdr.sample_rate)

        # 4. Decimación a 240 kHz
        audio = decimate(audio, 10)

        # 5. De-emphasis (obligatorio)
        audio = deemphasis_filter(audio, int(sdr.sample_rate/10))

        # 6. Decimación final para 48 kHz audio
        audio = decimate(audio, 5)

        # 7. Normalizar sonido
        audio = audio / np.max(np.abs(audio)) * 0.8

        sd.play(audio, 48000)
        sd.wait()

    sdr.close()

if __name__ == "__main__":
    main()
