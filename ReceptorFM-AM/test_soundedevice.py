import sounddevice as sd

print("\n=== DISPOSITIVOS DISPONIBLES ===")
print(sd.query_devices())

print("\n=== DISPOSITIVO DE SALIDA DEFECTO ===")
print(sd.default.device)