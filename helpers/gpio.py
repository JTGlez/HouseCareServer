import board
import time
import neopixel
import adafruit_dht
from gpiozero import MotionSensor, Servo, Button
from gpiozero.pins.pigpio import PiGPIOFactory
import os
from dotenv import load_dotenv
from helpers.telegram import bot

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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

def setup_gpio(emergency_callback, motion_start_callback, motion_end_callback):
    button.when_pressed = emergency_callback
    pir.when_motion = motion_start_callback
    pir.when_no_motion = motion_end_callback

def emergency(bot):
    print("El botón fue presionado!")
    mensaje_alerta = (
        "\U0001F6A8\U0001F6A8 ALERTA DE EMERGENCIA \U0001F6A8\U0001F6A8\n\n"
        "El familiar ha enviado una alerta de que no se siente bien y debe ser atendido de inmediato."
    )
    bot.send_message(os.getenv('CHAT_ID'), mensaje_alerta)

def abrir_puerta():
    servo.max()  # Ajusta esto según la necesidad de tu servo para abrir la puerta
    print("Puerta abierta")

def cerrar_puerta():
    servo.min()  # Ajusta esto según la necesidad de tu servo para cerrar la puerta
    print("Puerta cerrada")

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
