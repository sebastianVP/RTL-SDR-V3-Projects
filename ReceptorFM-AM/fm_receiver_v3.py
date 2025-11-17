import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
from scipy.signal import decimate

def fm_demod_wide(samples):
    phase = np.angle(samples)
    diff = np.diff(np.unwrap(phase))
    return diff

def main():
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 107.7e6
    sdr.gain = 40

    AUDIO_SR = 48000
    sd.default.samplerate = AUDIO_SR
    sd.default.channels = 1

    print("🎧 Escuchando FM Wide...")

    while True:
        samples = sdr.read_samples(256*1024)

        # 1. WFM discriminator
        demod = fm_demod_wide(samples)

        # 2. Decimación grande (de 2.4 MHz → 240 kHz)
        audio = decimate(demod, 10)

        # 3. Decimación final (240 kHz → 48 kHz)
        audio = decimate(audio, 5)

        # 4. Normalizar
        m = np.max(np.abs(audio))
        if m > 0:
            audio = (audio / m).astype(np.float32)

        sd.default.device = 11
        sd.play(audio, AUDIO_SR)
        sd.wait()

if __name__ == "__main__":
    main()
