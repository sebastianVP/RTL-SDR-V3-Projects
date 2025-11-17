import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
from scipy.signal import decimate, lfilter

# -------------------------
# FM DEMOD (Método robusto)
# -------------------------
def fm_demod(iq):
    return np.angle(iq[1:] * np.conj(iq[:-1]))

# -------------------------
# De-Emphasis (75us)
# -------------------------
def deemphasis(audio, fs=48000):
    tau = 75e-6
    a = np.exp(-1/(fs*tau))
    b = [1 - a]
    a = [1, -a]
    return lfilter(b, a, audio)

# -------------------------
# MAIN
# -------------------------
def main():

    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 101.7e6   # <-- CAMBIA a tu FM
    sdr.gain = 40               # prueba 35–49

    AUDIO_RATE = 48000 # 44100
    sd.default.samplerate = AUDIO_RATE
    sd.default.channels = 1
    sd.default.device = 11  # <-- MUY IMPORTANTE: tu salida de audio REAL


    print("🎧 Receptor FM Wide iniciado…")
    print("Presiona CTRL+C para detener.")

    while True:
        # --- 1. Captura SDR ---
        samples = sdr.read_samples(256*1024)

        # --- 2. Demod FM ---
        demod = fm_demod(samples)

        # --- 3. Decimación grande ---
        audio = decimate(demod, 10, zero_phase=True)   # 2.4 MHz → 240 kHz
        audio = decimate(audio, 5, zero_phase=True)     # 240 kHz → 48 kHz

        # --- 4. De-Emphasis ---
        audio = deemphasis(audio, AUDIO_RATE)

        # --- 5. Normalizar (evita saturación) ---
        m = np.max(np.abs(audio))
        if m > 0:
            audio = audio / m * 0.8

        # --- 6. Reproducir audio ---
        sd.play(audio.astype(np.float32), AUDIO_RATE)
        sd.wait()

    sdr.close()


if __name__ == "__main__":
    main()
