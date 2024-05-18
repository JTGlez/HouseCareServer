from gpiozero import MotionSensor, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
# Configura el pin GPIO del sensor PIR y el servo

factory = PiGPIOFactory()

pir = MotionSensor(26)  # Asume que el sensor PIR está conectado al GPIO 4
servo = Servo(2, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

def abrir_puerta():
    servo.max()  # Mueve el servo a 90 grados para abrir
    print("Puerta abierta")

def cerrar_puerta():
    servo.min()  # Mueve el servo a 0 grados para cerrar
    print("Puerta cerrada")

# Configura las acciones del sensor PIR
pir.when_motion = abrir_puerta
pir.when_no_motion = cerrar_puerta

# Mantén el script corriendo
while True:
	pir.wait_for_motion()
	print("You moved")
	pir.wait_for_no_motion()