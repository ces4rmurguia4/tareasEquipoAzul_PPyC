import os  # Manejo de rutas/carpetas y validación de archivos descargados.
import time  # Medición de tiempos para comparar secuencial vs concurrente.
import threading  # Descarga concurrente usando hilos.
import json  # Parseo del JSON obtenido cuando se usa curl como respaldo.
import subprocess  # Ejecución de curl como fallback ante bloqueos de requests.
from urllib.parse import urlparse  # Extrae partes de la URL para construir nombre de archivo.
import requests  # Cliente HTTP para consultar Unsplash y descargar imágenes.

URL_WALLPAPERS = "https://unsplash.com/t/wallpapers"
TOTAL_IMAGENES = 5


def obtener_urls_imagenes_unsplash(url_pagina: str, limite: int = 5):
    _ = url_pagina  # se mantiene el parámetro para no romper llamadas existentes
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    # Endpoint JSON del tema wallpapers: devuelve metadatos y URLs directas de fotos.
    endpoint = f"https://unsplash.com/napi/topics/wallpapers/photos?page=1&per_page={limite}"
    try:
        # Petición HTTP principal para obtener las imágenes disponibles.
        respuesta = requests.get(endpoint, headers=headers, timeout=20)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.RequestException:
        # Respaldo con curl cuando Unsplash bloquea la petición de requests.
        proceso = subprocess.run(
            ["curl", "-sL", endpoint],
            check=True,
            capture_output=True,
            text=True,
        )
        datos = json.loads(proceso.stdout)

    urls = []  # Lista final de URLs de imagen que se van a descargar.
    vistos = set()  # Evita repetir la misma URL en la lista final.
    for foto in datos:
        imagenes = foto.get("urls", {})
        # Selecciona la mejor URL disponible para descargar la imagen real.
        limpia = imagenes.get("full") or imagenes.get("regular") or imagenes.get("raw")
        if not limpia:
            continue
        if limpia in vistos:
            continue
        vistos.add(limpia)
        urls.append(limpia)
        if len(urls) >= limite:
            break
    return urls


# Obtiene desde Unsplash la lista de imágenes a procesar en este script.
archivos = obtener_urls_imagenes_unsplash(URL_WALLPAPERS, TOTAL_IMAGENES)


def nombre_desde_url(url: str) -> str:
    # Toma el último segmento de la URL como nombre base de archivo.
    nombre = os.path.basename(urlparse(url).path)
    # Si no hay nombre en la URL, usa uno por defecto.
    if not nombre:
        return "archivo.jpg"
    # Si no se detecta extensión, fuerza .jpg para guardar imagen válida.
    if "." not in nombre:
        return f"{nombre}.jpg"
    # Si ya hay extensión, se conserva.
    return nombre


def descargar_archivo(url: str, carpeta_salida: str):
    # Crea la carpeta destino si no existe.
    os.makedirs(carpeta_salida, exist_ok=True)
    # Define la ruta completa donde se guardará cada imagen.
    nombre_salida = os.path.join(carpeta_salida, nombre_desde_url(url))
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        # Descarga por streaming para no cargar toda la imagen en memoria.
        respuesta = requests.get(url, stream=True, headers=headers, timeout=30)
        respuesta.raise_for_status()
        # Escritura binaria por bloques: esta parte materializa la descarga en disco.
        with open(nombre_salida, "wb") as archivo:
            for chunk in respuesta.iter_content(chunk_size=1024):
                if chunk:
                    archivo.write(chunk)
    except requests.RequestException:
        # Fallback final: descarga con curl y guarda directamente en la ruta destino.
        subprocess.run(["curl", "-sL", "-o", nombre_salida, url], check=True)


# -------------------- Versión secuencial --------------------
# Marca el inicio para medir el tiempo de la descarga secuencial.
inicio_seq = time.perf_counter()
# Descarga una por una todas las imágenes.
for url in archivos:
    descargar_archivo(url, "descargas_secuencial")
# Calcula cuánto tardó todo el proceso secuencial.
tiempo_seq = time.perf_counter() - inicio_seq

# -------------------- Versión con hilos --------------------
# Marca el inicio para medir la versión concurrente.
inicio_hilos = time.perf_counter()
hilos = []
# Crea y lanza un hilo por cada URL para descargar en paralelo.
for url in archivos:
    hilo = threading.Thread(target=descargar_archivo, args=(url, "descargas_hilos"))
    hilo.start()
    hilos.append(hilo)

# Espera a que todos los hilos terminen antes de seguir.
for hilo in hilos:
    hilo.join()

# Calcula el tiempo total de la versión con hilos.
tiempo_hilos = time.perf_counter() - inicio_hilos


def verificar_descargas(urls, carpeta):
    # Recorre archivos esperados y lista los que no existen o están vacíos.
    faltantes = []
    for url in urls:
        ruta = os.path.join(carpeta, nombre_desde_url(url))
        if not (os.path.exists(ruta) and os.path.getsize(ruta) > 0):
            faltantes.append(ruta)
    return faltantes


faltantes_seq = verificar_descargas(archivos, "descargas_secuencial")
faltantes_hilos = verificar_descargas(archivos, "descargas_hilos")

# Muestra qué URLs exactas se usaron para descargar.
print("URLs de imagen usadas:")
for i, u in enumerate(archivos, 1):
    print(f"{i}. {u}")

# Reporta tiempos de ambas estrategias de descarga.
print(f"\nTiempo secuencial: {tiempo_seq:.3f} s")
print(f"Tiempo con hilos:  {tiempo_hilos:.3f} s")
if tiempo_hilos > 0:
    # Relación de rendimiento: cuántas veces la versión con hilos acelera a la secuencial.
    print(f"Aceleración aprox: {tiempo_seq / tiempo_hilos:.2f}x")

# Resultado de validación final de archivos descargados.
print("\nVerificación:")
print("Secuencial OK" if not faltantes_seq else f"Faltan en secuencial: {faltantes_seq}")
print("Hilos OK" if not faltantes_hilos else f"Faltan con hilos: {faltantes_hilos}")
