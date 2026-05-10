# main.py
import sys
import time
from PyQt5 import QtWidgets, QtCore
from interfaz import RobotControlGUI
from vision import CamaraVision
from cinematica import CinematicaRobot
from hardware import ControladorHardware

class HiloCicloAuto(QtCore.QThread):
    actualizar_gui = QtCore.pyqtSignal(str, str) # Mensaje, Color
    
    def __init__(self, vision, cine, hard):
        super().__init__()
        self.vision = vision
        self.cine = cine
        self.hard = hard
        self.corriendo = False

    def trayecto_seguro(self, x, y, z):
        """Maneja el movimiento punto a punto con revisión de sensores"""
        estado = self.hard.leer_seguridad()
        
        if estado == "STOP":
            self.actualizar_gui.emit("¡SISTEMA DETENIDO POR INTRUSIÓN!", "#c0392b")
            while self.hard.leer_seguridad() == "STOP":
                time.sleep(0.1)
            self.actualizar_gui.emit("REANUDANDO MOVIMIENTO...", "#27ae60")
        
        # Calcular y mover
        q1, q2, q3, q4 = self.cine.calcular_inversa(x, y, z)
        self.hard.mover_articulaciones(q1, q2, q3, q4)
        
        # Velocidad según sensor 'Slow'
        delay = 2.0 if estado == "SLOW" else 1.0
        time.sleep(delay)

    def run(self):
        self.corriendo = True
        rojos, verdes = 0, 0
        
        for i in range(1, 9): # 8 iteraciones según el proyecto
            if not self.corriendo: break
            
            self.actualizar_gui.emit(f"CICLO {i}/8: BUSCANDO PIEZA EN B", "#2980b9")
            # 1. Ir a Bodega B (Ajustar coordenadas reales luego)
            self.trayecto_seguro(15, 0, 15) 
            
            # 2. Visión: Identificar Color y Forma
            color, forma = self.vision.detectar_pieza()
            self.hard.accionar_gripper(cerrar=True)
            time.sleep(0.5)
            
            # 3. Clasificación y Apilamiento
            if color == "Rojo" and forma == "Cuadrado":
                self.actualizar_gui.emit("ENTREGANDO CUADRADO ROJO EN A", "#e67e22")
                self.trayecto_seguro(-15, 10, 15 + (rojos * 2)) # Offset apilado
                rojos += 1
            elif color == "Verde" and forma == "Circulo":
                self.actualizar_gui.emit("ENTREGANDO CÍRCULO VERDE EN C", "#27ae60")
                self.trayecto_seguro(15, 10, 15 + (verdes * 2))
                verdes += 1
            
            self.hard.accionar_gripper(cerrar=False)
            self.trayecto_seguro(0, 10, 5) # Posición de descanso/seguridad

        self.actualizar_gui.emit("PROCESO FINALIZADO CON ÉXITO", "#27ae60")

class MainApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.gui = RobotControlGUI()
        
        # Instancias de módulos
        self.vision = CamaraVision()
        self.cine = CinematicaRobot()
        self.hard = ControladorHardware()
        
        # Hilo de automatización
        self.hilo_auto = HiloCicloAuto(self.vision, self.cine, self.hard)
        
        self.conectar_eventos()

    def conectar_eventos(self):
        # Botón Automático
        self.gui.btn_start.clicked.connect(self.iniciar_auto)
        self.hilo_auto.actualizar_gui.connect(self.gui.actualizar_estado)
        
        # Botón Semiautomático
        self.gui.btn_go.clicked.connect(self.mover_semi)
        
        # Sliders Manuales (Conecta los 4)
        for i, slider in enumerate(self.gui.sliders):
            slider.valueChanged.connect(self.mover_manual)

    def mover_manual(self):
        # Lee los 4 sliders y mueve el hardware directamente
        angulos = [s.value() for s in self.gui.sliders]
        self.hard.mover_articulaciones(*angulos)

    def mover_semi(self):
        try:
            x = float(self.gui.input_x.text())
            y = float(self.gui.input_y.text())
            z = float(self.gui.input_z.text())
            q = self.cine.calcular_inversa(x, y, z)
            self.hard.mover_articulaciones(*q)
            self.gui.actualizar_estado(f"Movido a X:{x} Y:{y} Z:{z}")
        except ValueError:
            self.gui.actualizar_estado("Error: Ingrese números válidos", "#c0392b")

    def iniciar_auto(self):
        if not self.hilo_auto.isRunning():
            self.hilo_auto.start()

    def ejecutar(self):
        self.gui.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    MainApp().ejecutar()