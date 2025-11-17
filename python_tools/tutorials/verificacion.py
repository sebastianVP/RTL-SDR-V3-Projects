from rtlsdr import RtlSdr

sdr = RtlSdr()

print("Sample_rate:",sdr.sample_rate) 
print("Center freq:",sdr.center_freq)
print("Gain:",sdr.gain)

sdr.close()