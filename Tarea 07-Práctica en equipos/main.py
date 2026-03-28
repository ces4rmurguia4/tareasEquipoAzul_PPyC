import requests
import time
import threading

ciudades = [
    {"lat": 19.43, "lon": -99.13}, # CDMX
    {"lat": 40.71, "lon": -74.00}, # NY
    {"lat": 51.50, "lon": -0.12},  # Londres
    {"lat": 35.68, "lon": 139.69}  # Tokio
]

def obtener_clima(lat, lon):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = f"?latitude={lat}&longitude={lon}&current_weather=true"
    url = base_url + params
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()['current_weather']
    return None

# --- EJECUCIÓN SECUENCIAL ---
print("Iniciando consulta secuencial...")
inicio_seq = time.time()
for ciudad in ciudades:
    obtener_clima(ciudad['lat'], ciudad['lon'])
tiempo_seq = time.time() - inicio_seq
print(f"Tiempo secuencial: {tiempo_seq:.2f} segundos")

# --- EJECUCIÓN CON THREADING ---
print("\nIniciando consulta con hilos...")
hilos = []
inicio_thr = time.time()

for ciudad in ciudades:
    hilo = threading.Thread(target=obtener_clima, args=(ciudad['lat'], ciudad['lon']))
    hilos.append(hilo)
    hilo.start()

for hilo in hilos:
    hilo.join()

tiempo_thr = time.time() - inicio_thr
print(f"Tiempo con hilos: {tiempo_thr:.2f} segundos")

print(f"\nLa versión con hilos fue {tiempo_seq/tiempo_thr:.1f} veces más rápida")