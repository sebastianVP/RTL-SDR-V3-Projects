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
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 101.7e6
    sdr.gain = 40

    AUDIO_RATE = 48000
    sd.default.device = 11

    print("🎧 Receptor FM Wide (streaming) iniciado…")

    stream = sd.OutputStream(
        samplerate=AUDIO_RATE,
        channels=1,
        dtype='float32'
    )
    stream.start()

    while True:
        samples = sdr.read_samples(128*1024)

        demod = fm_demod(samples)

        # resample 2.4 MHz → 48 kHz en un solo paso
        audio = sig.resample_poly(demod, up=1, down=50)

        audio = deemphasis(audio, AUDIO_RATE)

        # normalizar
        m = np.max(np.abs(audio))
        if m > 0:
            audio = audio / m * 0.8

        stream.write(audio.astype(np.float32))

    sdr.close()

if __name__ == "__main__":
    main()
