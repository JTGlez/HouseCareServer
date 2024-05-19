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

def start_bot():
    bot.polling()
