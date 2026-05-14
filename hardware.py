# hardware.py
import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from gpiozero import DigitalInputDevice

class ControladorHardware:
    def __init__(self):
        # Configuraciones de pulsos para servos estándar (500-2500us)
        self.MIN_PULSE = 500
        self.MAX_PULSE = 2500
        self.RANGO = 180
        self.angulos_actuales = [90, 90, 90, 90]
        self.simulacion = False

        try:
            # Inicialización I2C
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(i2c)
            self.pca.frequency = 50 

            # Configuración de los 4 GDL + Gripper
            self.servos = [
                servo.Servo(self.pca.channels[0], min_pulse=self.MIN_PULSE, max_pulse=self.MAX_PULSE, actuation_range=self.RANGO),
                servo.Servo(self.pca.channels[1], min_pulse=self.MIN_PULSE, max_pulse=self.MAX_PULSE, actuation_range=self.RANGO),
                servo.Servo(self.pca.channels[2], min_pulse=self.MIN_PULSE, max_pulse=self.MAX_PULSE, actuation_range=self.RANGO),
                servo.Servo(self.pca.channels[3], min_pulse=self.MIN_PULSE, max_pulse=self.MAX_PULSE, actuation_range=self.RANGO)
            ]
            self.servo_gripper = servo.Servo(self.pca.channels[4], min_pulse=self.MIN_PULSE, max_pulse=self.MAX_PULSE)

            # Sensores de seguridad ECCI
            self.sensor_slow = DigitalInputDevice(17)
            self.sensor_stop1 = DigitalInputDevice(27)
            self.sensor_stop2 = DigitalInputDevice(22)
            print("✅ Hardware PCA9685 y Sensores listos.")

        except Exception as e:
            print(f"⚠ Error de hardware: {e}. Entrando en MODO SIMULACIÓN.")
            self.simulacion = True

    def leer_seguridad(self):
        if self.simulacion: return "NORMAL"
        # Prioridad a la detención total (Stop)
        if self.sensor_stop1.is_active or self.sensor_stop2.is_active: return "STOP"
        if self.sensor_slow.is_active: return "SLOW"
        return "NORMAL"

    def mover_articulaciones(self, q1, q2, q3, q4, interpolacion_suave=True):
        destinos = [q1, q2, q3, q4]
        if self.simulacion:
            self.angulos_actuales = destinos
            return

        if interpolacion_suave:
            pasos = 25
            for paso in range(1, pasos + 1):
                for i in range(4):
                    angulo = self.angulos_actuales[i] + ((destinos[i] - self.angulos_actuales[i]) / pasos) * paso
                    self.servos[i].angle = max(0, min(180, angulo))
                time.sleep(0.02)
        else:
            for i in range(4):
                self.servos[i].angle = max(0, min(180, destinos[i]))
        
        self.angulos_actuales = destinos

    def accionar_gripper(self, cerrar=True):
        if self.simulacion: return
        angulo = 160 if cerrar else 30 # Ajustar según tu pinza física
        self.servo_gripper.angle = angulo
        time.sleep(0.4)