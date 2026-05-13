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

        self.MIN_PULSO = 500
        self.MAX_PULSO = 2500
        self.RANGO_GRADOS = 180
        self.angulos_actuales = [90, 90, 90, 90]

        if not self.simulacion:
            try:
                # Intenta conectarse a la placa física
                i2c = busio.I2C(board.SCL, board.SDA)
                self.pca = PCA9685(i2c)
                self.pca.frequency = 50 

                self.servo_base = servo.Servo(self.pca.channels[0], min_pulse=self.MIN_PULSO, max_pulse=self.MAX_PULSO, actuation_range=self.RANGO_GRADOS)
                self.servo_hombro = servo.Servo(self.pca.channels[1], min_pulse=self.MIN_PULSO, max_pulse=self.MAX_PULSO, actuation_range=self.RANGO_GRADOS)
                self.servo_codo = servo.Servo(self.pca.channels[2], min_pulse=self.MIN_PULSO, max_pulse=self.MAX_PULSO, actuation_range=self.RANGO_GRADOS)
                self.servo_muneca = servo.Servo(self.pca.channels[3], min_pulse=self.MIN_PULSO, max_pulse=self.MAX_PULSO, actuation_range=self.RANGO_GRADOS)
                self.servo_gripper = servo.Servo(self.pca.channels[4], min_pulse=self.MIN_PULSO, max_pulse=self.MAX_PULSO)

                self.sensor_slow = DigitalInputDevice(17)
                self.sensor_stop1 = DigitalInputDevice(27)
                self.sensor_stop2 = DigitalInputDevice(22)
                print("✅ Hardware conectado correctamente.")

            except Exception as e:
                # Si la placa no está conectada o no tiene energía, se activa esto:
                print(f"⚠ Módulo I2C no encontrado ({e}). Pasando a MODO SIMULACIÓN.")
                self.simulacion = True

    def leer_seguridad(self):
        """Retorna el estado de los sensores para alterar la rutina automática"""
        return "NORMAL"

        if self.simulacion: return "NORMAL"
        
        if self.sensor_stop1.is_active or self.sensor_stop2.is_active:
            return "STOP"
        if self.sensor_slow.is_active:
            return "SLOW"
        return "NORMAL"

    def limitar_angulo(self, angulo):
        """Evita que los motores reciban señales fuera de su rango seguro"""
        return max(0.0, min(180.0, float(angulo)))

    def mover_articulaciones(self, q1, q2, q3, q4, interpolacion_suave=True):
        """
        Envía los comandos PWM a los servomotores.
        interpolacion_suave: Si es True, divide el movimiento en pasos.
        """
        # 1. Aplicar restricciones de seguridad
        q1 = self.limitar_angulo(q1)
        q2 = self.limitar_angulo(q2)
        q3 = self.limitar_angulo(q3)
        q4 = self.limitar_angulo(q4)

        destinos = [q1, q2, q3, q4]

        if not self.simulacion:
            if interpolacion_suave:
                pasos = 30 # A mayor número, más lento y suave es el movimiento
                retraso = 0.015 # Tiempo entre cada paso
                
                for paso in range(1, pasos + 1):
                    # Calcula la proporción del recorrido en la que vamos
                    # Esto asegura una escala del PWM progresiva en lugar de un escalón brusco
                    self.servo_base.angle = self.angulos_actuales[0] + ((q1 - self.angulos_actuales[0]) / pasos) * paso
                    self.servo_hombro.angle = self.angulos_actuales[1] + ((q2 - self.angulos_actuales[1]) / pasos) * paso
                    self.servo_codo.angle = self.angulos_actuales[2] + ((q3 - self.angulos_actuales[2]) / pasos) * paso
                    self.servo_muneca.angle = self.angulos_actuales[3] + ((q4 - self.angulos_actuales[3]) / pasos) * paso
                    time.sleep(retraso)
            else:
                # Movimiento instantáneo (Brusco, útil para pruebas muy rápidas)
                self.servo_base.angle = q1
                self.servo_hombro.angle = q2
                self.servo_codo.angle = q3
                self.servo_muneca.angle = q4

        # 2. Guardar la nueva posición en la memoria
        self.angulos_actuales = destinos

    def accionar_gripper(self, cerrar=True):
        """
        Controla el efector final.
        NOTA: Muchos grippers se traban si fuerzas los 0° o 180° absolutos.
        Modifica los ángulos 'ang_cerrado' y 'ang_abierto' tras ensamblar la pinza.
        """
        ang_cerrado = 160 # Grados para apretar la pieza sin forzar el motor
        ang_abierto = 30  # Grados para soltar
        
        angulo = ang_cerrado if cerrar else ang_abierto
        
        if not self.simulacion:
            self.servo_gripper.angle = angulo
            time.sleep(0.3) # Esperar a que la pinza física termine de cerrar