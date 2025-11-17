import numpy as np
from rtlsdr import RtlSdr
import sounddevice as sd
import scipy.signal as sig
from numba import njit
import queue, threading

@njit
def fm_demod(iq):
    out = np.empty(len(iq)-1, dtype=np.float32)
    for i in range(len(iq)-1):
        z = iq[i+1] * np.conj(iq[i])
        out[i] = np.arctan2(z.imag, z.real)
    return out

def deemphasis(audio, fs=48000):
    tau = 75e-6
    a = np.exp(-1/(fs*tau))
    b = [1 - a]
    a = [1, -a]
    return sig.lfilter(b, a, audio)

def audio_worker(q, stream):
    while True:
        frame = q.get()
        stream.write(frame)

def main():

    sdr = RtlSdr()
    sdr.sample_rate = 1.024e6
    sdr.center_freq = 107.1e6
    sdr.gain = 40

    BLOCK = 128 * 1024
    AUDIO_RATE = 48000

    sd.default.channels = 1

    # LOWPASS 200 kHz
    lpf = sig.firwin(101, cutoff=200e3, fs=1.024e6)

    stream = sd.OutputStream(
        samplerate=AUDIO_RATE,
        channels=1,
        dtype='float32',
        blocksize=1024,
        latency='low'
    )
    stream.start()

    audio_q = queue.Queue(maxsize=10)
    threading.Thread(target=audio_worker, args=(audio_q, stream), daemon=True).start()

    print("🎧 Receptor FM Ultra Optimizado iniciado…")

    while True:
        samples = sdr.read_samples(BLOCK)

        samples = sig.lfilter(lpf, 1.0, samples)

        demod = fm_demod(samples)

        audio = sig.resample_poly(demod, up=3, down=64)
        audio = deemphasis(audio, AUDIO_RATE)

        m = np.max(np.abs(audio))
        if m > 0:
            audio = audio / m * 0.8

        for i in range(0, len(audio), 1024):
            audio_q.put(audio[i:i+1024].astype(np.float32))

if __name__ == "__main__":
    main()
