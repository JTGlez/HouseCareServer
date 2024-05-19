from gpiozero import Button, Servo
from signal import pause
from gpiozero.pins.pigpio import PiGPIOFactory
servo = Servo(2)  # Asume que el servo está conectado al GPIO 17

factory = PiGPIOFactory()

servo = Servo(2, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

def when_pressed():
    print("El botón fue presionado!")
    servo.max()  # Mueve el servo a 90 grados para abrir


def when_released():
    print("El botón fue liberado!")
    servo.min()  # Mueve el servo a 0 grados para cerrar

button = Button(23)

button.when_pressed = when_pressed
button.when_released = when_released

pause()
