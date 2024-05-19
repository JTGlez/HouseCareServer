import threading
from bot import start_bot
from helpers.cam_detect import capture_frames

# Iniciar el hilo de captura de frames
capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

# Iniciar el bot
start_bot()
