# hardware.py
import time

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
    from gpiozero import DigitalInputDevice
    MODO_RASPBERRY = True
except ImportError:
    MODO_RASPBERRY = False
    print("⚠ Librerías de Raspberry no detectadas. MODO SIMULACIÓN de motores activado.")

class ControladorHardware:
    def __init__(self):
        self.simulacion = not MODO_RASPBERRY

        if not self.simulacion:
            # Inicializar PCA9685 y Sensores reales
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(i2c)
            self.pca.frequency = 50

            self.servo_base = servo.Servo(self.pca.channels[0])
            self.servo_hombro = servo.Servo(self.pca.channels[1])
            self.servo_codo = servo.Servo(self.pca.channels[2])
            self.servo_gripper = servo.Servo(self.pca.channels[3])

            self.sensor_lejos_slow = DigitalInputDevice(17)
            self.sensor_cerca_stop1 = DigitalInputDevice(27)
            self.sensor_cerca_stop2 = DigitalInputDevice(22)

    def leer_sensores(self):
        if self.simulacion:
            return "NORMAL" # En PC siempre está libre
        
        if self.sensor_cerca_stop1.is_active or self.sensor_cerca_stop2.is_active:
            return "STOP"
        if self.sensor_lejos_slow.is_active:
            return "SLOW"
        return "NORMAL"

    def mover_servos(self, q1, q2, q3):
        if not self.simulacion:
            self.servo_base.angle = q1
            self.servo_hombro.angle = q2
            self.servo_codo.angle = q3

    def operar_gripper(self, accion):
        angulo = 0 if accion == "ABRIR" else 180
        if not self.simulacion:
            self.servo_gripper.angle = angulo