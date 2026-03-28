import threading
import time

boletos_disponibles = 100

def vender_boletos(cantidad):
    global boletos_disponibles
    temporal = boletos_disponibles
    time.sleep(0.0001)

    boletos_disponibles = temporal - cantidad
# Iniciamos con los hilos haciendo la prueba sin el lock para ver que sucede con el resultado. 
threads = []
num_threads = 50
# Opcional: Iniciamos un temporizador para medir cuánto tiempo tarda la ejecución del programa.
start = time.time()

for i in range(num_threads):
    t = threading.Thread(target=vender_boletos, args=(1,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Finalizamos nuestro temporizador y hacemos las operaciones correspondientes para mostrar el tiempo.
end = time.time()

# Opcional: Mostramos los resultados y verficamos que no es lo que esperamos en la cantidad
# De boletos vendidos. 
print(f"Resultado final: {boletos_disponibles}  de boletos.")
print(f"Resultado esperado: {100 - num_threads} de boletos.")
print(f"Total de tiempo de ejecucion: {end - start} segundos.")