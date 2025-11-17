# 📡 Receptor FM con RTL-SDR — Documentación Técnica y Proceso Completo

Este repositorio documenta el proceso completo de desarrollo, depuración y optimización de un Receptor FM en Python utilizando un RTL-SDR V3.
El proyecto cubre desde los primeros prototipos de demodulación hasta la reproducción de audio fluida, la visualización de espectros, el análisis de forma de onda, la selección de dispositivos de audio y la auto-sintonía de estaciones.

## 🎯 Objetivo del Proyecto

Construir un pipeline estable para recibir señales FM, demodularlas en tiempo real, visualizar elementos clave del procesamiento y reproducir audio sin cortes.
Además, se incorporan herramientas de diagnóstico y escaneo del espectro para automatizar la búsqueda de estaciones.

## 🧱 Estructura del Proyecto

El repositorio está organizado en etapas claras, cada una representada por un script independiente.

1. Primer Receptor FM (Prototipo)

Archivo: fm_receiver_initial.py

Objetivo: implementar la cadena básica IQ → demodulación FM → decimación → audio.

2. Diagnóstico de Señal con FFT

Archivo: test_fft.py

Objetivo: verificar la presencia de señal en la frecuencia sintonizada antes de intentar escuchar audio.

Permite validar antena, ganancia y correcto funcionamiento del SDR.

3. Visualización de Forma de Onda de Audio

Archivo: test_audio_waveform.py

Objetivo: observar la forma de onda de audio demodulado para evaluar si el proceso FM funciona.

4. Verificación y Selección del Dispositivo de Audio

Archivo: test_sounddevice.py

Objetivo: listar dispositivos de audio disponibles y seleccionar manualmente la salida correcta (altavoces, auriculares, etc.).

Este paso resolvió el problema de que “no se escuchaba nada”.

5. Receptor en Tiempo Real (Streaming Fluido)

Archivo: fm_receiver_stream.py

Objetivo: reemplazar sd.play() por un flujo continuo (OutputStream), eliminando cortes en la reproducción.

Introduce:

streaming de audio por frames

resampleo mediante resample_poly

filtro de de-énfasis

mejora significativa de estabilidad

6. Versión Optimizada

Archivo: fm_receiver_optimized.py

Objetivo: mejorar rendimiento reduciendo carga de CPU y latencia.

Incluye opciones como:

menor sample rate del SDR

bufferización por cola (queue.Queue)

hilo separado para la salida de audio

filtro pasa-bajos previo

posibilidad de acelerar el demodulador con Numba

7. Auto-Sintonía y Escaneo de Potencia

Archivo: scan_fm_band.py

Objetivo: barrer todo el rango FM (87.5–108 MHz), medir potencia en cada paso e identificar automáticamente la mejor estación disponible.

8. Receptor Final con Auto-Sintonía

Archivo: fm_receiver_final.py

Combina:

escaneo automático

selección de mejor estación

streaming de audio fluido

de-énfasis

resampleo eficiente

buffer de audio optimizado

## 🔍 Flujo de Trabajo (Resumen del Proceso)

El desarrollo se realizó en etapas secuenciales, identificando y resolviendo obstáculos clave:

1. Recepción y Demodulación Básica

Se logra recibir IQ y demodular FM.

El audio no se escuchaba correctamente.

2. Verificación de Señal

Se incorpora FFT para observar el espectro y confirmar la presencia de estaciones.

Esto permitió validar antena, ganancia y funcionamiento del dongle.

3. Visualización del Audio

Se grafica la forma de onda del audio demodulado.

Confirmamos que la demodulación producía señal válida.

4. Problema Detectado: Dispositivo de Audio Incorrecto

El audio se enviaba a un dispositivo no deseado.

Se listaron dispositivos de audio y se estableció manualmente el dispositivo adecuado.

5. Cambio a Streaming

Se reemplaza el método bloqueante por un flujo continuo.

Se mejora la calidad y estabilidad del audio.

6. Optimización

Se ajusta el sample rate del SDR.

Se usa resampleo polifásico más eficiente.

Se implementa un hilo para audio y otro para recepción.

Se reduce la latencia y se eliminan cortes.

7. Auto-Sintonía

Se incorpora un escaneo del rango FM por potencia.

El receptor ahora se autoajusta a la mejor estación disponible.

## 🧪 Scripts de Diagnóstico Incluidos
Script	Propósito
test_fft.py	Verificar que haya señal en la frecuencia seleccionada.
test_audio_waveform.py	Revisar la forma de onda de audio demodulado.
test_sounddevice.py	Identificar y elegir el dispositivo de salida correcto.

Estos scripts son fundamentales para detectar problemas típicos de SDR, audio o recepción.

## 🚀 Receptor Final

El archivo fm_receiver_final.py integra todo el proceso:

Auto-sintonía del espectro FM

Selección de la mejor estación

Demodulación FM

Filtro de de-énfasis (75 µs)

Resampleo eficiente

Reproducción continua de audio sin cortes

Configuración explícita del dispositivo de salida

Está diseñado como la versión estable y lista para uso.

## 📎 Requisitos del Sistema

RTL-SDR V3 o compatible

Python 3.10+

Bibliotecas principales:

rtlsdr

numpy

scipy

sounddevice

matplotlib (opcional para diagnósticos)

Se recomienda ejecutar en Windows o Linux con suficiente ancho de banda USB.

## 🛠 Próximos Pasos Sugeridos

Implementar waterfall en tiempo real.

Agregar grabación de audio.

Integrar GUI en PyQt o Qt for Python.

Añadir decodificación RDS opcional.

Subir ejemplos de espectros y audio al repositorio.

## 👨‍💻 Autor

Desarrollado y documentado por Alexander Valdez, integrando técnicas de DSP, SDR y depuración en tiempo real.