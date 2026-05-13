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
        """Maneja el movimiento punto a punto con revisión de sensores en automático"""
        estado = self.hard.leer_seguridad()
        
        if estado == "STOP":
            self.actualizar_gui.emit("¡SISTEMA DETENIDO POR INTRUSIÓN!", "#c0392b")
            while self.hard.leer_seguridad() == "STOP":
                time.sleep(0.1)
            self.actualizar_gui.emit("REANUDANDO MOVIMIENTO...", "#27ae60")
        
        q1, q2, q3, q4 = self.cine.calcular_inversa(x, y, z)
        # En modo automático SÍ usamos interpolación suave
        self.hard.mover_articulaciones(q1, q2, q3, q4, interpolacion_suave=True)
        
        delay = 2.0 if estado == "SLOW" else 1.0
        time.sleep(delay)

    def run(self):
        self.corriendo = True
        rojos, verdes = 0, 0
        
        for i in range(1, 9):
            if not self.corriendo: break
            
            self.actualizar_gui.emit(f"CICLO {i}/8: BUSCANDO PIEZA EN B", "#2980b9")
            self.trayecto_seguro(15, 0, 15) 
            
            color, forma = self.vision.detectar_pieza()
            self.hard.accionar_gripper(cerrar=True)
            time.sleep(0.5)
            
            if color == "Rojo" and forma == "Cuadrado":
                self.actualizar_gui.emit("ENTREGANDO CUADRADO ROJO EN A", "#e67e22")
                self.trayecto_seguro(-15, 10, 15 + (rojos * 2))
                rojos += 1
            elif color == "Verde" and forma == "Circulo":
                self.actualizar_gui.emit("ENTREGANDO CÍRCULO VERDE EN C", "#27ae60")
                self.trayecto_seguro(15, 10, 15 + (verdes * 2))
                verdes += 1
            
            self.hard.accionar_gripper(cerrar=False)
            self.trayecto_seguro(0, 10, 5)

        self.actualizar_gui.emit("PROCESO FINALIZADO CON ÉXITO", "#27ae60")

class MainApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.gui = RobotControlGUI()
        
        self.vision = CamaraVision()
        self.cine = CinematicaRobot()
        self.hard = ControladorHardware()
        
        self.hilo_auto = HiloCicloAuto(self.vision, self.cine, self.hard)
        
        self.conectar_eventos()

    def conectar_eventos(self):
        # 1. Conexiones Modo Automático
        self.gui.btn_start.clicked.connect(self.iniciar_auto)
        self.hilo_auto.actualizar_gui.connect(self.gui.actualizar_estado)
        
        # 2. Conexiones Modo Semiautomático
        self.gui.btn_go.clicked.connect(self.mover_semi)
        
        # =========================================================
        # 3. CONEXIONES MODO MANUAL
        # =========================================================
        # Conectamos cada slider a la función mover_manual
        for slider in self.gui.sliders:
            slider.valueChanged.connect(self.mover_manual)
            
        # Conectamos los botones del Gripper
        self.gui.btn_pick.clicked.connect(self.cerrar_gripper)
        self.gui.btn_place.clicked.connect(self.abrir_gripper)

    # =========================================================
    # LÓGICA DEL MODO MANUAL
    # =========================================================
    def mover_manual(self):
        """Lee los sliders y mueve el robot en tiempo real"""
        # Evitar mover manualmente si el modo automático está corriendo
        if self.hilo_auto.isRunning():
            return 

        # Capturamos los valores actuales de los 4 sliders
        q1 = self.gui.sliders[0].value()
        q2 = self.gui.sliders[1].value()
        q3 = self.gui.sliders[2].value()
        q4 = self.gui.sliders[3].value()
        
        # IMPORTANTE: Desactivamos interpolacion_suave para evitar lag al arrastrar el slider
        self.hard.mover_articulaciones(q1, q2, q3, q4, interpolacion_suave=False)

    def cerrar_gripper(self):
        """Acciona la pinza para agarrar"""
        if not self.hilo_auto.isRunning():
            self.hard.accionar_gripper(cerrar=True)
            self.gui.actualizar_estado("MODO MANUAL: GRIPPER CERRADO", "#34495e")

    def abrir_gripper(self):
        """Acciona la pinza para soltar"""
        if not self.hilo_auto.isRunning():
            self.hard.accionar_gripper(cerrar=False)
            self.gui.actualizar_estado("MODO MANUAL: GRIPPER ABIERTO", "#7f8c8d")

    # =========================================================
    # LÓGICA DEL MODO SEMIAUTOMÁTICO
    # =========================================================
    def mover_semi(self):
        if self.hilo_auto.isRunning():
            self.gui.actualizar_estado("ERROR: Modo Auto en ejecución", "#c0392b")
            return

        try:
            x = float(self.gui.input_x.text())
            y = float(self.gui.input_y.text())
            z = float(self.gui.input_z.text())
            
            # Calculamos ángulos e interpolamos para que el movimiento sea elegante
            q1, q2, q3, q4 = self.cine.calcular_inversa(x, y, z)
            self.hard.mover_articulaciones(q1, q2, q3, q4, interpolacion_suave=True)
            
            # Opcional: Actualizar los sliders en la interfaz para que coincidan con la nueva posición
            # Desconectamos temporalmente las señales para no generar un bucle infinito
            for i in range(4): self.gui.sliders[i].blockSignals(True)
            self.gui.sliders[0].setValue(int(q1))
            self.gui.sliders[1].setValue(int(q2))
            self.gui.sliders[2].setValue(int(q3))
            self.gui.sliders[3].setValue(int(q4))
            for i in range(4): self.gui.sliders[i].blockSignals(False)

            self.gui.actualizar_estado(f"POSICIÓN SEMIAUTO -> X:{x} Y:{y} Z:{z}", "#8e44ad")
        except ValueError:
            self.gui.actualizar_estado("ERROR: Ingrese números válidos en X,Y,Z", "#c0392b")

    def iniciar_auto(self):
        if not self.hilo_auto.isRunning():
            self.hilo_auto.start()

    def ejecutar(self):
        self.gui.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    MainApp().ejecutar()