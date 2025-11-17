import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
import scipy.signal as sig

# ------------------------------------------
#  FM DEMODULATOR
# ------------------------------------------
def fm_demod(iq):
    return np.angle(iq[1:] * np.conj(iq[:-1]))

# ------------------------------------------
#  DE-EMPHASIS (75us)
# ------------------------------------------
def deemphasis(audio, fs=48000):
    tau = 75e-6
    a = np.exp(-1/(fs*tau))
    b = [1 - a]
    a = [1, -a]
    return sig.lfilter(b, a, audio)

# ------------------------------------------
#  SCAN FM BAND (87.5–108 MHz)
# ------------------------------------------
def scan_fm_band(sdr, start=101e6, stop=102e6, step=200e3):# 87.5e6 108e6  step 200e3
    print("🔎 Escaneando espectro FM... (puede tomar ~4–6s)")

    results = []
    freqs = np.arange(start, stop, step)

    for f in freqs:
        sdr.center_freq = f
        samples = sdr.read_samples(32 * 1024)
        power = np.mean(np.abs(samples)**2)
        results.append((f, power))

    results.sort(key=lambda x: x[1], reverse=True)

    print("✔ Escaneo completado")
    return results

# ------------------------------------------
# AUTO-TUNE (Selecciona mejor estación)
# ------------------------------------------
def auto_tune_best_station(sdr):
    results = scan_fm_band(sdr)
    best_freq = results[0][0]
    best_power = results[0][1]

    print(f"\n📡 Mejor estación detectada: {best_freq/1e6:.1f} MHz  (potencia={best_power:.4f})")
    return best_freq

# ------------------------------------------
#  MAIN RECEPTOR
# ------------------------------------------
def main():

    # === CONFIG SDR ===
    sdr = RtlSdr()
    sdr.sample_rate = 1.024e6       # estable y bajo en CPU
    sdr.gain = 40

    AUDIO_RATE = 48000
    sd.default.channels = 1

    # ------------------------------------------
    # AUTO-SINTONÍA
    # ------------------------------------------
    print("🔎 Buscando la mejor estación FM...")
    best = auto_tune_best_station(sdr)
    sdr.center_freq = best

    print(f"🎧 Sintonizando automáticamente: {best/1e6:.1f} MHz\n")

    # STREAM DE AUDIO
    stream = sd.OutputStream(
        samplerate=AUDIO_RATE,
        channels=1,
        dtype='float32',
        blocksize=1024,
        latency='low'
    )
    stream.start()

    BLOCK = 128 * 1024  # balance perfecto rendimiento/calidad

    print("🎶 Reproduciendo FM… CTRL+C para salir")

    while True:
        # --- 1: Captura SDR ---
        samples = sdr.read_samples(BLOCK)

        # --- 2: Demod FM ---
        demod = fm_demod(samples)

        # --- 3: Resampling (1.024 MHz → 48 kHz) ---
        audio = sig.resample_poly(demod, up=3, down=64)

        # --- 4: De-emphasis ---
        audio = deemphasis(audio, AUDIO_RATE)

        # --- 5: Normalizar ---
        m = np.max(np.abs(audio))
        if m > 0:
            audio = audio / m * 0.8

        # --- 6: Enviar audio en frames ---
        for i in range(0, len(audio), 1024):
            stream.write(audio[i:i+1024].astype(np.float32))

    sdr.close()


if __name__ == "__main__":
    main()
