import os
import time
import threading
from urllib.parse import urlparse
import requests

# Si ya existe "archivos" en otra celda, se respeta y se completa hasta 5.
try:
    archivos
except NameError:
    archivos = []

extras = [
    "https://www.gutenberg.org/cache/epub/11/pg11.txt",
    "https://www.gutenberg.org/cache/epub/84/pg84.txt",
    "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    "https://www.gutenberg.org/cache/epub/2701/pg2701.txt",
]

for u in extras:
    if len(archivos) >= 5:
        break
    if u not in archivos:
        archivos.append(u)

archivos = archivos[:5]  # exactamente 5


def nombre_desde_url(url: str) -> str:
    nombre = os.path.basename(urlparse(url).path)
    return nombre if nombre else "archivo.bin"


def descargar_archivo(url: str, carpeta_salida: str):
    os.makedirs(carpeta_salida, exist_ok=True)
    nombre_salida = os.path.join(carpeta_salida, nombre_desde_url(url))
    respuesta = requests.get(url, stream=True, timeout=20)
    respuesta.raise_for_status()
    with open(nombre_salida, "wb") as archivo:
        for chunk in respuesta.iter_content(chunk_size=1024):
            if chunk:
                archivo.write(chunk)


# -------------------- Versión secuencial --------------------
inicio_seq = time.perf_counter()
for url in archivos:
    descargar_archivo(url, "descargas_secuencial")
tiempo_seq = time.perf_counter() - inicio_seq

# -------------------- Versión con hilos --------------------
inicio_hilos = time.perf_counter()
hilos = []
for url in archivos:
    hilo = threading.Thread(target=descargar_archivo, args=(url, "descargas_hilos"))
    hilo.start()
    hilos.append(hilo)

for hilo in hilos:
    hilo.join()

tiempo_hilos = time.perf_counter() - inicio_hilos


def verificar_descargas(urls, carpeta):
    faltantes = []
    for url in urls:
        ruta = os.path.join(carpeta, nombre_desde_url(url))
        if not (os.path.exists(ruta) and os.path.getsize(ruta) > 0):
            faltantes.append(ruta)
    return faltantes


faltantes_seq = verificar_descargas(archivos, "descargas_secuencial")
faltantes_hilos = verificar_descargas(archivos, "descargas_hilos")

print("URLs usadas:")
for i, u in enumerate(archivos, 1):
    print(f"{i}. {u}")

print(f"\nTiempo secuencial: {tiempo_seq:.3f} s")
print(f"Tiempo con hilos:  {tiempo_hilos:.3f} s")
if tiempo_hilos > 0:
    print(f"Aceleración aprox: {tiempo_seq / tiempo_hilos:.2f}x")

print("\nVerificación:")
print("Secuencial OK" if not faltantes_seq else f"Faltan en secuencial: {faltantes_seq}")
print("Hilos OK" if not faltantes_hilos else f"Faltan con hilos: {faltantes_hilos}")