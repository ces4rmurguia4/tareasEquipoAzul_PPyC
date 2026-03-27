import requests
import queue
import threading
import time


MAX_ITEMS = 50
MAX_TIME = 5
NUM_PRODUCTORES = 2
NUM_CONSUMIDORES = 3

cola = queue.Queue(maxsize=20)
stop_event = threading.Event()
contador = 0
contador_lock = threading.Lock()

archivo_lock = threading.Lock()

def productor(id):
    global contador
    endpoint = "https://api.chucknorris.io/jokes/random"
    
    while not stop_event.is_set():
        try:
            r = requests.get(endpoint, timeout=2)
            chiste = r.json()['value']
            
            cola.put(chiste)  # bloquea si está llena
            
            with contador_lock:
                contador += 1
                if contador >= MAX_ITEMS:
                    stop_event.set()
            
            print(f"Productor {id} produjo chiste {contador}")
        
        except Exception as e:
            print(f"Error productor {id}: {e}")

def consumidor(id):
    while True:
        chiste = cola.get()
        
        if chiste is None:  # centinela
            break
        
        with archivo_lock:
            with open("Tarea-05-Practica-en-equipos/chistes.txt", "a", encoding="utf-8") as f:
                f.write(chiste + "\n\n")
        
        print(f"Consumidor {id} guardó un chiste")
        cola.task_done()

def main():
    productores = []
    consumidores = []

    inicio = time.time()

    # Crear consumidores
    for i in range(NUM_CONSUMIDORES):
        t = threading.Thread(target=consumidor, args=(i,))
        t.start()
        consumidores.append(t)

    # Crear productores
    for i in range(NUM_PRODUCTORES):
        t = threading.Thread(target=productor, args=(i,))
        t.start()
        productores.append(t)

    # Control de tiempo
    while time.time() - inicio < MAX_TIME:
        if stop_event.is_set():
            break
        time.sleep(0.1)

    stop_event.set()

    # Esperar productores
    for t in productores:
        t.join()

    # Enviar centinelas para terminar consumidores
    for _ in consumidores:
        cola.put(None)

    # Esperar consumidores
    for t in consumidores:
        t.join()
    print ( f" Tiempo secuencial : { time . time () - inicio } segundos ")
    print("Proceso terminado correctamente")

if __name__ == "__main__":
    main()