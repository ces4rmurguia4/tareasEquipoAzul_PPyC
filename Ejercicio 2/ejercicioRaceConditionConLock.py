import threading
import time

# Agregamos la función "Lock" que antes no teníamos para demostrar el uso de que nadie puede pasar al baño 
# sin que tenga la llave para entrar. 

candado = threading.Lock()
boletos_disponibles = 500 

def vender_boletos(cantidad): 
    global boletos_disponibles
    with candado:
        temporal = boletos_disponibles
        time.sleep(0.0001)
        boletos_disponibles = temporal - cantidad

# Multiprocessing
if __name__ == "__main__":

    print(f"Inciciando la venta de boletos {boletos_disponibles}")
    # Comenzamos nuestro cronómetro para saber cuaánto timepo tardó la ejecución. 
    start = time.time()
    threads = []
    num_threads = 1000
    for i in range(num_threads):
        t = threading.Thread(target=vender_boletos, args=(1,))
        threads.append(t)
        t.start()

    for t in threads: 
        t.join()

    # Detenemos nuestro cronómetro y hacemos las respectivas operaciones para determinar el tiempo tolat de ejecución. 
    end = time.time()

    # Extra, escribimos nuestros resoltados sobre los boletos y nuestro tiempo de ejecución para analizar y comparar
    # Los resultados deseados, no es necesario pero se implementó como recurso visual. 
    print(f"Resultado final: {boletos_disponibles}")
    print(f"Tiempo total: {end - start} ")