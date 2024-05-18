import cv2
import numpy as np
import os
from dotenv import load_dotenv
from picamera.array import PiRGBArray
from picamera import PiCamera
import telebot
import time

# Cargar variables de entorno
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telebot.TeleBot(API_TOKEN)

# Configurar la cámara
camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))

# Función para enviar imagen a Telegram
def send_image(chat_id, image_path):
    with open(image_path, 'rb') as photo:
        bot.send_photo(chat_id, photo)

# Función para detectar movimiento
def detect_movement(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 900:
            continue
        return True
    return False

# Captura frames continuamente
while True:
    rawCapture.truncate(0)
    camera.capture(rawCapture, format="bgr")
    frame1 = rawCapture.array
    
    rawCapture.truncate(0)
    camera.capture(rawCapture, format="bgr")
    frame2 = rawCapture.array
    
    if detect_movement(frame1, frame2):
        print("Movimiento detectado")
        # Captura y guarda la imagen
        timestamp = str(int(time.time()))
        img_name = f"{timestamp}.jpg"
        cv2.imwrite(img_name, frame2)
        
        # Envía la imagen a Telegram
        send_image(CHAT_ID, img_name)
        
        # Espera un poco antes de volver a detectar
        time.sleep(5)
