"""
“pkg_resources is deprecated”
💬 Es solo un WARNING, no afecta el funcionamiento.
Viene desde el paquete pyrtlsdr, que todavía usa pkg_resources.
En 2025 esa API desaparecerá, pero por ahora todo funciona normal.
"""
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from rtlsdr import RtlSdr

sdr = RtlSdr()

print("Sample_rate:",sdr.sample_rate) 
print("Center freq:",sdr.center_freq)
print("Gain:",sdr.gain)

sdr.close()