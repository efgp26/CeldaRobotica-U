# hardware.py
import time

try:
    from gpiozero import AngularServo, DigitalInputDevice
    MODO_RASPBERRY = True
except ImportError:
    MODO_RASPBERRY = False
    print("⚠ Modo Simulación: No se detectó hardware de Raspberry Pi.")

class ControladorHardware:
    def __init__(self):
        self.simulacion = not MODO_RASPBERRY
        self.angulos_actuales = [90, 90, 90, 90]

        if not self.simulacion:
            # Tiempos de pulso para forzar el rango de 180 grados (en segundos para gpiozero)
            # 500 microsegundos = 0.0005s | 2500 microsegundos = 0.0025s
            min_p = 0.0005
            max_p = 0.0025

            # Conexión directa a los pines GPIO de la Raspberry
            self.servo_base = AngularServo(12, initial_angle=90, min_angle=0, max_angle=180, min_pulse_width=min_p, max_pulse_width=max_p)
            self.servo_hombro = AngularServo(16, initial_angle=90, min_angle=0, max_angle=180, min_pulse_width=min_p, max_pulse_width=max_p)
            self.servo_codo = AngularServo(20, initial_angle=90, min_angle=0, max_angle=180, min_pulse_width=min_p, max_pulse_width=max_p)
            self.servo_muneca = AngularServo(21, initial_angle=90, min_angle=0, max_angle=180, min_pulse_width=min_p, max_pulse_width=max_p)
            
            # Gripper
            self.servo_gripper = AngularServo(25, initial_angle=30, min_angle=0, max_angle=180, min_pulse_width=min_p, max_pulse_width=max_p)

            # Sensores (Recuerda que si no los tienes conectados, este pin flotante puede dar falsos positivos)
            self.sensor_slow = DigitalInputDevice(17)
            self.sensor_stop1 = DigitalInputDevice(27)
            self.sensor_stop2 = DigitalInputDevice(22)

    def leer_seguridad(self):
        # --- PARCHE DE PRUEBA: Descomenta esto si no tienes los sensores físicos aún ---
        return "NORMAL"
        
        if self.simulacion: return "NORMAL"
        if self.sensor_stop1.is_active or self.sensor_stop2.is_active: return "STOP"
        if self.sensor_slow.is_active: return "SLOW"
        return "NORMAL"

    def limitar_angulo(self, angulo):
        return max(0.0, min(180.0, float(angulo)))

    def mover_articulaciones(self, q1, q2, q3, q4, interpolacion_suave=True):
        q1 = self.limitar_angulo(q1)
        q2 = self.limitar_angulo(q2)
        q3 = self.limitar_angulo(q3)
        q4 = self.limitar_angulo(q4)

        destinos = [q1, q2, q3, q4]

        if not self.simulacion:
            if interpolacion_suave:
                pasos = 30
                retraso = 0.015
                for paso in range(1, pasos + 1):
                    self.servo_base.angle = self.angulos_actuales[0] + ((q1 - self.angulos_actuales[0]) / pasos) * paso
                    self.servo_hombro.angle = self.angulos_actuales[1] + ((q2 - self.angulos_actuales[1]) / pasos) * paso
                    self.servo_codo.angle = self.angulos_actuales[2] + ((q3 - self.angulos_actuales[2]) / pasos) * paso
                    self.servo_muneca.angle = self.angulos_actuales[3] + ((q4 - self.angulos_actuales[3]) / pasos) * paso
                    time.sleep(retraso)
            else:
                self.servo_base.angle = q1
                self.servo_hombro.angle = q2
                self.servo_codo.angle = q3
                self.servo_muneca.angle = q4

        self.angulos_actuales = destinos

    def accionar_gripper(self, cerrar=True):
        ang_cerrado = 160
        ang_abierto = 30
        angulo = ang_cerrado if cerrar else ang_abierto
        
        if not self.simulacion:
            self.servo_gripper.angle = angulo
            time.sleep(0.3)