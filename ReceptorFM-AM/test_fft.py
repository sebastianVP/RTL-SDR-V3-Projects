import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr

def main():
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 101.7e6   # pon tu emisora
    sdr.gain = 'auto'

    print("📡 Capturando muestras y generando FFT...")

    samples = sdr.read_samples(256*1024)

    # FFT
    fft_data = np.fft.fftshift(np.fft.fft(samples))
    power = 20 * np.log10(np.abs(fft_data))

    freqs = np.linspace(
        sdr.center_freq - sdr.sample_rate/2,
        sdr.center_freq + sdr.sample_rate/2,
        len(power)
    )

    plt.figure(figsize=(12,5))
    plt.plot(freqs/1e6, power)
    plt.title("Espectro alrededor de la frecuencia sintonizada")
    plt.xlabel("Frecuencia (MHz)")
    plt.ylabel("Potencia (dB)")
    plt.grid()
    plt.show()

    sdr.close()

if __name__ == "__main__":
    main()