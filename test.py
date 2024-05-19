import threading
from bot import start_bot
from helpers.cam_detect import capture_frames
from helpers.gpio import setup_gpio, emergency, abrir_puerta, cerrar_puerta
from helpers.telegram import bot

# Configurar GPIO
setup_gpio(lambda: emergency(bot), abrir_puerta, cerrar_puerta)

# Iniciar el hilo de captura de frames
capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

# Iniciar el bot
start_bot()