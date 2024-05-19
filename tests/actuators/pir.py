import threading

from gpiozero import MotionSensor
from signal import pause
from time import sleep

pir = MotionSensor(26)

# Define el comportamiento del primer hilo
def thread_pir(pir):
    prev_active = False
    while True:
        if pir.motion_detected and not prev_active:
            print("Movimiento detectado!")
            #pbuzzer.value= 0.5

            # Aquí enviamos el correo
# #         send_email()
            prev_active = True
        elif not pir.motion_detected:
            prev_active = False
            #pbuzzer.value = 0  # Detiene el buzzer
        sleep(0.1)  # Pausa para evitar una sobrecarga de la CPU

thread1 = threading.Thread(target=thread_pir, args=(pir,))

thread1.start()
thread1.join()