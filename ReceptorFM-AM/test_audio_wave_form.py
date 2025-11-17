import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
from scipy.signal import decimate, lfilter

def fm_demod(iq):
    return np.angle(iq[1:] * np.conj(iq[:-1]))

def deemphasis(audio, fs):
    tau = 75e-6  # FM América
    alpha = fs * tau
    b = [1]
    a = [alpha + 1, -alpha]
    return lfilter(b, a, audio)

def main():
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 107.7e6   # tu emisora
    sdr.gain = 'auto'

    print("📡 Capturando FM WIDE y verificando forma de onda...")

    samples = sdr.read_samples(256*1024)

    # 1. FM discriminator
    demod = fm_demod(samples)

    # 2. Decimación a 240 kHz
    audio = decimate(demod, 10, zero_phase=True)

    # 3. Decimación a 48 kHz
    audio = decimate(audio, 5, zero_phase=True)

    # 4. De-emphasis (suaviza audio)
    audio = deemphasis(audio, 48000)

    # 5. Gráfica
    plt.figure(figsize=(12,4))
    plt.plot(audio[:5000])
    plt.title("Forma de onda de audio FM (48 kHz)")
    plt.grid()
    plt.show()

    sdr.close()

if __name__ == "__main__":
    main()
