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
    print("⚠ Modo Simulación: No se detectó hardware de Raspberry Pi.")

class ControladorHardware:
    def __init__(self):
        self.simulacion = not MODO_RASPBERRY

        if not self.simulacion:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(i2c)
            self.pca.frequency = 50

            # 4 Servomotores en los canales 0, 1, 2 y 3
            self.servo_base = servo.Servo(self.pca.channels[0])
            self.servo_hombro = servo.Servo(self.pca.channels[1])
            self.servo_codo = servo.Servo(self.pca.channels[2])
            self.servo_muneca = servo.Servo(self.pca.channels[3])
            
            # Gripper en el canal 4
            self.servo_gripper = servo.Servo(self.pca.channels[4])

            # Sensores de Seguridad (GPIOs sugeridos)
            self.sensor_slow = DigitalInputDevice(17)   # Sensor alejado
            self.sensor_stop1 = DigitalInputDevice(27)  # Sensor cercano 1
            self.sensor_stop2 = DigitalInputDevice(22)  # Sensor cercano 2

    def leer_seguridad(self):
        if self.simulacion: return "NORMAL"
        
        if self.sensor_stop1.is_active or self.sensor_stop2.is_active:
            return "STOP"
        if self.sensor_slow.is_active:
            return "SLOW"
        return "NORMAL"

    def mover_articulaciones(self, q1, q2, q3, q4):
        """Envía los 4 ángulos a los servomotores"""
        if not self.simulacion:
            self.servo_base.angle = q1
            self.servo_hombro.angle = q2
            self.servo_codo.angle = q3
            self.servo_muneca.angle = q4

    def accionar_gripper(self, cerrar=True):
        angulo = 180 if cerrar else 0 # Ajustar según el ensamble físico
        if not self.simulacion:
            self.servo_gripper.angle = angulo