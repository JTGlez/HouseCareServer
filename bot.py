# Módulo de arranque del bot de Telegram
import telebot
from dotenv import load_dotenv
import os
from helpers.telegram import handle_activity_command, handle_voice_message

# Cargar variables de entorno
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telebot.TeleBot(API_TOKEN)

# Manejar el comando de actividad de cámara
@bot.message_handler(commands=['activity'])
def activity_command(message):
    handle_activity_command(bot, message)

# Manejar mensajes de voz
@bot.message_handler(content_types=['voice'])
def voice_message(message):
    handle_voice_message(bot, message)

# Manejar el comando '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    👋 ¡Hola! Soy el *Asistente Virtual de HouseCareServer* 🏠🤖

    Soy tu mano derecha en el cuidado de tus seres queridos. Aquí tienes algunas cosas que puedo hacer por ti:

    📊 *Mostrar actividad reciente*: Usa el comando /activity para ver la gráfica de actividad reciente.
    💡 *Controlar luces*: Puedes pedirme que encienda o apague las luces.
    🚪 *Controlar puertas*: Puedo abrir o cerrar puertas por ti.
    🌡️ *Monitorear el clima*: Te puedo decir la temperatura y humedad actuales.

    Para ver una lista completa de comandos disponibles, escribe /help.

    ¡Estoy aquí para ayudarte! 😊
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Manejar el comando '/help'
@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """
    🛠️ *Comandos Disponibles* 🛠️

    Aquí tienes algunas acciones que puedes pedirme realizar:

    - 📊 */activity*: Muestra la gráfica de actividad reciente.
    - 💡 *Encender luz*: Enciende la tira de LEDs.
    - 💡 *Apagar luz*: Apaga la tira de LEDs.
    - 🚪 *Abrir puerta*: Abre la puerta.
    - 🚪 *Cerrar puerta*: Cierra la puerta.
    - 🌡️ *Temperatura actual*: Muestra la temperatura y humedad actuales.

    Simplemente envíame un mensaje de voz con alguno de estos comandos.

    *Ejemplos de comandos de voz*:
    - "Encender luz"
    - "Apagar luz"
    - "Abrir puerta"
    - "Cerrar puerta"
    - "Temperatura actual"
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

def start_bot():
    # Enviar mensaje de bienvenida al inicializar el bot
    welcome_text = """
    👋 ¡Hola! Soy el *Asistente Virtual de HouseCareServer* 🏠🤖

    Soy tu mano derecha en el cuidado de tus seres queridos. Aquí tienes algunas cosas que puedo hacer por ti:

    📊 *Mostrar actividad reciente*: Usa el comando /activity para ver la gráfica de actividad reciente.
    💡 *Controlar luces*: Puedes pedirme que encienda o apague las luces.
    🚪 *Controlar puertas*: Puedo abrir o cerrar puertas por ti.
    🌡️ *Monitorear el clima*: Te puedo decir la temperatura y humedad actuales.

    Para ver una lista completa de comandos disponibles, escribe /help.

    ¡Estoy aquí para ayudarte! 😊
    """
    bot.send_message(CHAT_ID, welcome_text, parse_mode='Markdown')
    
    # Iniciar el bot
    bot.polling()