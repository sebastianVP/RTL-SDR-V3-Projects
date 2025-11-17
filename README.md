# RTL-SDR V3 Projects

Bienvenido al repositorio **RTL-SDR V3 Projects**, dedicado a proyectos de radio definido por software (SDR) usando el **RTL2838UHIDIR (RTL-SDR V3)**.  
Este dispositivo es un receptor de radio económico y versátil que permite capturar y procesar señales de radio de manera digital usando Python y otras herramientas.

---

## 🔹 Qué es el RTL-SDR V3

El **RTL-SDR V3** es un dispositivo de radio definido por software que permite recibir señales de RF en un amplio rango de frecuencias (aprox. 500 kHz – 1.7 GHz).  
Sus principales características:

1. **Recepción de radio FM/AM, bandas de radioaficionados y señales comerciales**.  
2. **Monitoreo de tráfico aéreo mediante ADS-B y ACARS**.  
3. **Captura de imágenes de satélites meteorológicos (NOAA, METEOR)**.  
4. **Detección de interferencias y análisis de espectro** para aplicaciones educativas, científicas o comerciales.

En esencia, este SDR convierte tu PC en un potente receptor de radio capaz de procesar cualquier señal de RF dentro de su rango.

---

## 🔹 Usos y aplicaciones generales

- Radioaficionados y educación en telecomunicaciones.  
- Seguimiento de aviones y datos ADS-B en tiempo real.  
- Recepción y análisis de señales meteorológicas satelitales.  
- Investigación y desarrollo de proyectos IoT o domótica inalámbrica.  
- Monitoreo de interferencias y análisis de espectro en entornos industriales.  

---

## 🔹 Proyectos iniciales a desarrollar

Este repositorio contiene tres proyectos iniciales diseñados para **mostrar la potencia del RTL-SDR V3 y su programación en Python**:

### 1️⃣ Receptor y visualizador de radio FM/AM
- Captura y decodifica radio FM/AM en tiempo real.  
- Visualización de espectrograma dinámico con Python.  
- Permite grabar audio y decodificar información RDS.

### 2️⃣ Tracker de aviones ADS-B
- Decodificación de señales ADS-B en tiempo real.  
- Visualización de aviones en un mapa interactivo (posición, velocidad, altitud).  
- Posibilidad de guardar histórico de vuelos para análisis.

### 3️⃣ Receptor de satélites meteorológicos (NOAA/METEOR)
- Captura de señales de satélites meteorológicos.  
- Procesamiento y decodificación de imágenes en tiempo real.  
- Guardado de imágenes para análisis de clima o demostraciones educativas.

---

## 🔹 Estructura del repositorio

```yaml
RTL-SDR-V3-Projects/
│
├── fm_receiver/ # Proyecto 1: Radio FM/AM
├── adsb_tracker/ # Proyecto 2: Aviones ADS-B
└── noaa_receiver/ # Proyecto 3: Satélites meteorológicos
```