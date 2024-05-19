import time
import threading
import telebot
import board
import neopixel
import adafruit_dht
import speech_recognition as sr
from gpiozero import MotionSensor, Servo, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from pydub import AudioSegment
import os
from dotenv import load_dotenv
load_dotenv()

# Telegram Bot Instance
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telebot.TeleBot(API_TOKEN)
stop_event = threading.Event()

# LED Strip configs
pixel_pin = board.D21
num_pixels = 30
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)

def turn_on_leds():
    color = (255 // 2, 255 // 2, 255 // 2)
    pixels.fill(color)
    pixels.show()

def turn_off_leds():
    pixels.fill((0, 0, 0))
    pixels.show()

# GPIO Init
factory = PiGPIOFactory()
button = Button(23)
pir = MotionSensor(26)
servo = Servo(2, max_pulse_width=2.05/1000, min_pulse_width=0.75/1000, pin_factory=factory)
dhtDevice = adafruit_dht.DHT11(board.D4)

# Manual Actions
def emergency():
    print("El botón fue presionado!")
    mensaje_alerta = (
        "\U0001F6A8\U0001F6A8 ALERTA DE EMERGENCIA \U0001F6A8\U0001F6A8\n\n"
        "El familiar ha enviado una alerta de que no se siente bien y debe ser atendido de inmediato."
    )
    bot.send_message(CHAT_ID, mensaje_alerta)

def abrir_puerta():
    servo.max()  # Ajusta esto según la necesidad de tu servo para abrir la puerta
    print("Puerta abierta")

def cerrar_puerta():
    servo.min()  # Ajusta esto según la necesidad de tu servo para cerrar la puerta
    print("Puerta cerrada")

# GPIO Handlers
button.when_pressed = emergency
pir.when_motion = abrir_puerta
pir.when_no_motion = cerrar_puerta

def read_dht11():
    start_time = time.time()  # Guarda el tiempo de inicio
    while time.time() - start_time <= 5:  # Continúa durante un máximo de 5 segundos
        try:
            # Intenta obtener los valores del sensor
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            if temperature_c is not None and humidity is not None:
                return "\U0001F321 Temperatura: {:.1f} F / {:.1f} C \n\U0001F4A7 Humedad: {}% ".format(temperature_f, temperature_c, humidity)
            else:
                print("Lectura nula, reintentando...")
        except RuntimeError as error:
            # Los errores ocurren bastante a menudo, los DHT son difíciles de leer, simplemente continúa
            print("Error al leer el DHT11, reintentando...")
        time.sleep(1.0)  # Espera un poco antes de reintentar para no saturar el sensor

    # Si se alcanza este punto, significa que no se obtuvo una lectura válida en 5 segundos
    return "\U000026A0 No se pudo recuperar la lectura del DHT11 después de 5 segundos."

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(
    message,
    """¡Hola! Soy el asistente virtual de HouseCareServer: tu mano derecha en el cuidado de tus seres queridos. 
    Puedes ejecutar acciones por medio de este Bot para facilitar la vida de tus seres queridos.
    Si deseas obtener una tabla de los comandos disponibles, escribe /help"""
  )

# Handle '/help'
@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """
Aquí tienes algunas acciones que puedes pedirme realizar:

- *Encender luz*: Enciende la tira de LEDs.
- *Apagar luz*: Apaga la tira de LEDs.
- *Fecha*: Te diré la fecha actual.
- *Hora*: Te diré la hora actual.

Simplemente envíame un mensaje de voz con alguno de estos comandos.
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('voice.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Convertir .ogg a .wav
    audio = AudioSegment.from_ogg("voice.ogg")
    audio.export("voice.wav", format="wav")

    r = sr.Recognizer()

    with sr.AudioFile('voice.wav') as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="es-MX")
            text = text.lower()
            print(text)
            
            if "encender luz" in text:
                print('Encendiendo luz')
                turn_on_leds()  # Llama a la función para encender la tira de LEDs
                bot.reply_to(message, "Luz encendida")
            elif "apagar luz" in text:
                print('Apagando luz')
                turn_off_leds()  # Llama a la función para apagar la tira de LEDs
                bot.reply_to(message, "Luz apagada")
            elif "abrir puerta" in text:
                print('Abriendo puerta')
                abrir_puerta()
                bot.reply_to(message, "Puerta abierta")
            elif "cerrar puerta" in text:
                print('Cerrando puerta')
                cerrar_puerta()
                bot.reply_to(message, "Puerta cerrada")
            elif "temperatura actual" in text:
                respuesta = read_dht11()
                bot.reply_to(message, respuesta)
            else:
                print("Comando no reconocido")
                bot.reply_to(message, "Comando no reconocido")
        except sr.UnknownValueError:
            bot.reply_to(message, "No pude entender el audio")
        except sr.RequestError as e:
            bot.reply_to(message, f"Error de servicio; {e}")

def run_telebot():
    print("Telegram Bot running")
    while not stop_event.is_set():
        try:
            bot.polling(none_stop=False, interval=0, timeout=20)
        except Exception as e:
            print(f"Error en bot.polling: {e}")
            if stop_event.is_set():
                break
            time.sleep(10)

if __name__ == '__main__':
    telebot_thread = threading.Thread(target=run_telebot)
    telebot_thread.start()

    try:
        while telebot_thread.is_alive():
            telebot_thread.join(timeout=1)
    except KeyboardInterrupt:
        print("Deteniendo el programa...")
        stop_event.set()  # Señaliza a los hilos que deben detenerse
        telebot_thread.join()  # Espera a que el hilo termine de forma limpia
        print("Programa detenido correctamente.")
