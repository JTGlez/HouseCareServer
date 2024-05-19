import os
import telebot
from dotenv import load_dotenv
from db.db_helper import get_activity_data
import matplotlib.pyplot as plt
import pandas as pd
import random
import datetime

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telebot.TeleBot(API_TOKEN)

# Directorio para guardar las fotos
PHOTO_DIR = 'photos'
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

def send_image(image_path):
    with open(image_path, 'rb') as photo:
        bot.send_photo(CHAT_ID, photo)

def notify_movement_start(start_time):
    bot.send_message(CHAT_ID, f"🚨 *Nuevo periodo de movimiento detectado* 🚨\n\n🕒 *Inicio:* {start_time}", parse_mode='Markdown')

def notify_movement_end(end_time):
    bot.send_message(CHAT_ID, f"✅ *Periodo de movimiento finalizado* ✅\n\n🕒 *Fin:* {end_time}", parse_mode='Markdown')

def notify_activity_log(start_time, end_time):
    bot.send_message(CHAT_ID, f"📝 *Registro de movimiento añadido* 📝\n\n🕒 *Inicio:* {start_time}\n🕒 *Fin:* {end_time}", parse_mode='Markdown')

def handle_activity_command(bot, message):
    plot_path = create_activity_plot()
    if plot_path:
        bot.send_message(message.chat.id, "📊 *Gráfica de Actividad Reciente* 📊\n\nAquí tienes la gráfica de los movimientos detectados hoy:", parse_mode='Markdown')
        send_image(plot_path)
    else:
        bot.send_message(message.chat.id, "No hay datos de actividad disponibles.")

# Función para crear la gráfica de actividad
def create_activity_plot():
    data = get_activity_data()
    if not data:
        return None

    df = pd.DataFrame(data, columns=['ID', 'Start Time', 'End Time', 'Image Path'])
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])

    # Filtrar los datos para el día actual
    today = datetime.now().date()
    df = df[df['Start Time'].dt.date == today]

    if df.empty:
        return None

    times = []
    durations = []

    for entry in df.itertuples():
        start_time = entry._2
        end_time = entry._3
        duration = (end_time - start_time).total_seconds()
        
        time_str = start_time.strftime("%H:%M")
        times.append(time_str)
        durations.append(duration)

    colors = ['#%06X' % random.randint(0, 0xFFFFFF) for _ in range(len(times))]
    plt.figure(figsize=(10, 6))
    plt.plot(times, durations, marker='o', linestyle='-', color='b')  # Conectar los puntos con líneas

    for i in range(len(times)):
        plt.plot(times[i], durations[i], 'o', color=colors[i])

    plt.xlabel('Hora')
    plt.ylabel('Duración del Movimiento (segundos)')
    plt.title(f'Movimientos el {today.strftime("%Y-%m-%d")}')
    plt.grid(True, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_path = os.path.join(PHOTO_DIR, 'activity_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path