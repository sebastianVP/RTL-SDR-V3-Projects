import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
import scipy.signal as sig

def fm_demod(iq):
    return np.angle(iq[1:] * np.conj(iq[:-1]))

def deemphasis(audio, fs=48000):
    tau = 75e-6
    a = np.exp(-1/(fs*tau))
    b = [1 - a]
    a = [1, -a]
    return sig.lfilter(b, a, audio)

def main():

    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6       # MÁS ESTABLE
    sdr.center_freq = 107.7e6
    sdr.gain = 40

    BLOCK = 256*1024                # BLOQUE ÓPTIMO

    AUDIO_RATE = 48000
    sd.default.device = 11

    print("🎧 Receptor FM Wide (optimizado) iniciado…")

    stream = sd.OutputStream(
        samplerate=AUDIO_RATE,
        channels=1,
        dtype='float32',
        blocksize=1024
    )
    stream.start()

    while True:
        samples = sdr.read_samples(BLOCK)

        demod = fm_demod(samples)

        # resample 2.048 MHz → 48 kHz (factor exacto ~42.666)
        audio = sig.resample_poly(demod, up=3, down=128)

        audio = deemphasis(audio, AUDIO_RATE)

        # normalizar
        m = np.max(np.abs(audio))
        if m > 0:
            audio = audio / m * 0.8

        # enviar en frames pequeños para evitar cortes
        for i in range(0, len(audio), 1024):
            frame = audio[i:i+1024].astype(np.float32)
            stream.write(frame)

    sdr.close()

if __name__ == "__main__":
    main()
