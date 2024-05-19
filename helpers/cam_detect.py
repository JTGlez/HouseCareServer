# Módulo de algoritmo de detección de movimiento en la cámara
import time
import os
import cv2
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
from helpers.camera import detect_movement, initialize_camera
from helpers.telegram import send_image, notify_movement_start, notify_movement_end, notify_activity_log
from db.db_helper import log_activity

# Configurar la cámara
camera, rawCapture = initialize_camera()

# Variables para el control de periodos de actividad
activity_detected = False
last_activity_time = None
activity_start_time = None
wait_time = 30  # Tiempo de espera en segundos
capture_delay = 2  # Retraso antes de capturar la imagen representativa

def capture_frames():
    global activity_detected, last_activity_time, activity_start_time

    # Ignorar los primeros 10 fotogramas para evitar lecturas falsas al inicio
    for _ in range(10):
        rawCapture.truncate(0)
        camera.capture(rawCapture, format="bgr")

    while True:
        rawCapture.truncate(0)
        camera.capture(rawCapture, format="bgr")
        frame1 = rawCapture.array

        rawCapture.truncate(0)
        camera.capture(rawCapture, format="bgr")
        frame2 = rawCapture.array

        if detect_movement(frame1, frame2):
            current_time = time.time()
            if not activity_detected:
                activity_detected = True
                activity_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("Movimiento detectado, iniciando periodo de actividad")
                notify_movement_start(activity_start_time)

            last_activity_time = current_time

            # Introducir un retraso antes de capturar la imagen representativa
            time.sleep(capture_delay)

            # Captura y guarda la imagen representativa
            rawCapture.truncate(0)
            camera.capture(rawCapture, format="bgr")
            frame_representative = rawCapture.array
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            img_name = os.path.join('photos', f"{timestamp}.jpg")
            cv2.imwrite(img_name, frame_representative)

            # Envía la imagen a Telegram
            send_image(img_name)

            # Espera un poco antes de volver a detectar
            time.sleep(5)
        else:
            if activity_detected and (time.time() - last_activity_time > wait_time):
                activity_detected = False
                activity_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("Periodo de actividad finalizado")
                notify_movement_end(activity_end_time)
                log_activity(activity_start_time, activity_end_time, img_name)
                notify_activity_log(activity_start_time, activity_end_time)
                activity_start_time = None
                last_activity_time = None