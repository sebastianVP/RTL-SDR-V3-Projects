import sounddevice as sd
import numpy as np

device_id = 10   # <-- cambia aquí el número exacto de tu salida
print(f"Probando salida de audio en el dispositivo {device_id}...")

fs = 44100
duration = 3
t = np.linspace(0, duration, int(fs*duration), endpoint=False)
tone = 0.3*np.sin(2*np.pi*440*t)  # tono A4

sd.play(tone, fs, device=device_id)
sd.wait()