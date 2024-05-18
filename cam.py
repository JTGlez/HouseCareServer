import sys
import os

# Añadir la versión del sistema de NumPy al PYTHONPATH para OpenCV
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import cv2

# Eliminar la versión del sistema de NumPy del PYTHONPATH para Matplotlib
sys.path.pop(0)

# Añadir la versión del entorno virtual de NumPy al PYTHONPATH para Matplotlib
sys.path.insert(0, '/home/jorje/HouseCareServer/venv/lib/python3.9/site-packages')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from picamera.array import PiRGBArray
from picamera import PiCamera
import telebot
import time
from datetime import datetime
from db.db_helper import init_db, get_db_connection

# Inicializar la base de datos
init_db()

# Cargar variables de entorno
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telebot.TeleBot(API_TOKEN)

# Configurar la cámara
camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))

# Directorio para guardar las fotos
PHOTO_DIR = 'photos'
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# Función para enviar imagen a Telegram
def send_image(chat_id, image_path):
    with open(image_path, 'rb') as photo:
        bot.send_photo(chat_id, photo)

# Función para detectar movimiento
def detect_movement(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    _, thresh = cv2.threshold(blur, 30, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 1500:
            continue
        return True
    return False

# Función para registrar actividad en la base de datos
def log_activity(start_time, end_time, image_path):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO activity (start_time, end_time, image_path)
        VALUES (?, ?, ?)
    ''', (start_time, end_time, image_path))
    conn.commit()
    conn.close()

# Función para obtener los registros de actividad
def get_activity_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM activity ORDER BY start_time DESC')
    rows = c.fetchall()
    conn.close()
    return rows

# Función para crear la gráfica de actividad
def create_activity_plot():
    data = get_activity_data()
    if not data:
        return None

    df = pd.DataFrame(data, columns=['ID', 'Start Time', 'End Time', 'Image Path'])
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])

    plt.figure(figsize=(10, 6))
    for _, row in df.iterrows():
        plt.plot([row['Start Time'], row['End Time']], [1, 1], marker='o')

    plt.xlabel('Time')
    plt.ylabel('Activity')
    plt.title('Activity Periods')
    plt.grid(True)
    plt.tight_layout()

    plot_path = os.path.join(PHOTO_DIR, 'activity_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

# Función para manejar el comando de actividad de cámara
@bot.message_handler(commands=['actividad_de_camara'])
def handle_activity_command(message):
    plot_path = create_activity_plot()
    if plot_path:
        send_image(message.chat.id, plot_path)
    else:
        bot.send_message(message.chat.id, "No hay datos de actividad disponibles.")

# Variables para el control de periodos de actividad
activity_detected = False
last_activity_time = None
activity_start_time = None
wait_time = 30  # Tiempo de espera en segundos
capture_delay = 2  # Retraso antes de capturar la imagen representativa

# Captura frames continuamente
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
        
        last_activity_time = current_time
        
        # Introducir un retraso antes de capturar la imagen representativa
        time.sleep(capture_delay)
        
        # Captura y guarda la imagen representativa
        rawCapture.truncate(0)
        camera.capture(rawCapture, format="bgr")
        frame_representative = rawCapture.array
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        img_name = os.path.join(PHOTO_DIR, f"{timestamp}.jpg")
        cv2.imwrite(img_name, frame_representative)
        
        # Envía la imagen a Telegram
        send_image(CHAT_ID, img_name)
        
        # Espera un poco antes de volver a detectar
        time.sleep(5)
    else:
        if activity_detected and (time.time() - last_activity_time > wait_time):
            activity_detected = False
            activity_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("Periodo de actividad finalizado")
            log_activity(activity_start_time, activity_end_time, img_name)
            activity_start_time = None
            last_activity_time = None

# Iniciar el bot
bot.polling()
