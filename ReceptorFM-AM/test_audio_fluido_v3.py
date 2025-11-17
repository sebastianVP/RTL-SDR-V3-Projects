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
    sdr.sample_rate = 1.024e6         # BAJADO PARA MENOS CPU
    sdr.center_freq = 101.1e6
    sdr.gain = 40

    BLOCK = 128 * 1024                # BLOQUE MÁS LIGERO

    AUDIO_RATE = 48000
    sd.default.channels = 1

    print("🎧 Receptor FM Wide optimizado")

    stream = sd.OutputStream(
        samplerate=AUDIO_RATE,
        channels=1,
        dtype='float32',
        blocksize=1024,
        latency='low'
    )
    stream.start()

    while True:
        samples = sdr.read_samples(BLOCK)

        demod = fm_demod(samples)

        # resample 1.024 MHz → 48 kHz (aprox 21.33:1)
        audio = sig.resample_poly(demod, up=3, down=64)

        audio = deemphasis(audio, AUDIO_RATE)

        # Normalización
        m = np.max(np.abs(audio))
        if m > 0:
            audio = audio / m * 0.8

        # enviar audio por frames
        for i in range(0, len(audio), 1024):
            stream.write(audio[i:i+1024].astype(np.float32))

if __name__ == "__main__":
    main()
