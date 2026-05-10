# main.py
import sys
import time
from PyQt5 import QtWidgets, QtCore

# Importar nuestros propios módulos
from interfaz import RobotControlGUI
from vision import CamaraVision
from cinematica import CinematicaRobot
from hardware import ControladorHardware

class HiloAutomatico(QtCore.QThread):
    """Hilo secundario para mover el robot sin congelar la ventana"""
    actualizar_estado = QtCore.pyqtSignal(str)
    
    def __init__(self, cam, cine, hard):
        super().__init__()
        self.camara = cam
        self.cinematica = cine
        self.hardware = hard
        self.ejecutando = True

        # Coordenadas hipotéticas
        self.Z_MESA = 15.0
        self.ALTURA_SEG = self.Z_MESA - 8.0
        self.PUNTO_B = (10, 15, self.Z_MESA)
        self.PUNTO_A = (-15, 10, self.Z_MESA)
        self.PUNTO_C = (15, 10, self.Z_MESA)

    def rutina_seguridad(self):
        """Revisa sensores y aplica demoras si es necesario"""
        estado = self.hardware.leer_sensores()
        if estado == "STOP":
            self.actualizar_estado.emit("¡STOP! Peligro inminente.")
            while self.hardware.leer_sensores() == "STOP":
                time.sleep(0.1)
        elif estado == "SLOW":
            time.sleep(0.5) # Pausa extra para simular lentitud

    def mover(self, x, y, z):
        self.rutina_seguridad()
        q1, q2, q3 = self.cinematica.calcular_inversa(x, y, z)
        self.hardware.mover_servos(q1, q2, q3)
        time.sleep(1) # Simula el viaje

    def run(self):
        self.actualizar_estado.emit("Iniciando Ciclo Automático...")
        rojos, verdes = 0, 0
        
        for ciclo in range(1, 9): # 8 piezas
            if not self.ejecutando:
                break
                
            self.actualizar_estado.emit(f"Ciclo {ciclo}/8: Yendo a Bodega")
            self.mover(self.PUNTO_B[0], self.PUNTO_B[1], self.PUNTO_B[2])
            
            color = self.camara.detectar_color()
            self.hardware.operar_gripper("CERRAR")
            self.mover(self.PUNTO_B[0], self.PUNTO_B[1], self.ALTURA_SEG)
            
            # Decidir destino
            if color == "Rojo":
                dest_x, dest_y = self.PUNTO_A[0], self.PUNTO_A[1] + (rojos * 3)
                rojos += 1
            else:
                dest_x, dest_y = self.PUNTO_C[0], self.PUNTO_C[1] + (verdes * 3)
                verdes += 1

            self.actualizar_estado.emit(f"Llevando {color} a destino")
            self.mover(dest_x, dest_y, self.Z_MESA)
            self.hardware.operar_gripper("ABRIR")
            self.mover(dest_x, dest_y, self.ALTURA_SEG)

        self.actualizar_estado.emit("Ciclo Finalizado.")

class ControladorPrincipal:
    def __init__(self):
        # 1. Iniciar la Interfaz
        self.app = QtWidgets.QApplication(sys.argv)
        self.gui = RobotControlGUI()
        
        # 2. Instanciar los módulos
        self.camara = CamaraVision()
        self.cinematica = CinematicaRobot()
        self.hardware = ControladorHardware()
        
        # 3. Crear el hilo automático pasándole los módulos
        self.hilo = HiloAutomatico(self.camara, self.cinematica, self.hardware)
        
        # 4. Conectar señales (Botones y Textos)
        self.gui.btn_start.clicked.connect(self.iniciar_automatico)
        self.hilo.actualizar_estado.connect(self.gui.actualizar_estado)

    def iniciar_automatico(self):
        if not self.hilo.isRunning():
            self.hilo.ejecutando = True
            self.hilo.start()

    def ejecutar(self):
        self.gui.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    sistema = ControladorPrincipal()
    sistema.ejecutar()