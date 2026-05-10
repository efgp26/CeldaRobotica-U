import time
from PyQt5.QtCore import QThread, pyqtSignal

class SistemaAutomatico(QThread):
    # Señales para comunicarse con la GUI
    actualizar_estado = pyqtSignal(str)
    alerta_seguridad = pyqtSignal(str)
    
    def __init__(self, robot_kinematics, camera, sensores):
        super().__init__()
        self.robot = robot_kinematics  # Clase/funciones de cinemática inversa
        self.camara = camera           # Clase/funciones de visión artificial
        self.sensores = sensores       # Lectura de pines GPIO
        self.ejecutando = True
        
        # Coordenadas base (X, Y, Z) - ¡Por definir!
        self.PUNTO_B = (0, 20, 0) # Bodega (Recogida)
        self.PUNTO_A = (-20, 0, 0) # Entrega Rojo
        self.PUNTO_C = (20, 0, 0)  # Entrega Verde
        self.ALTURA_SEGURIDAD = 8 # cm mínimos de elevación

        # Contadores para apilar en línea recta
        self.cantidad_rojos = 0
        self.cantidad_verdes = 0

    def verificar_seguridad(self):
        """Revisa el estado de los sensores ultrasónicos/infrarrojos"""
        if self.sensores.detecta_parada_emergencia(): # Los 2 sensores más cercanos
            self.alerta_seguridad.emit("¡STOP! Intrusión detectada.")
            # Lógica para frenar motores físicamente
            while self.sensores.detecta_parada_emergencia():
                time.sleep(0.1) # Esperar hasta que se despeje el área
            self.alerta_seguridad.emit("Área despejada. Reanudando...")
            return "NORMAL"
            
        elif self.sensores.detecta_zona_lenta(): # El sensor más alejado
            self.alerta_seguridad.emit("¡SLOW! Movimiento detectado cerca.")
            return "SLOW"
            
        return "NORMAL"

    def mover_robot(self, destino_x, destino_y, destino_z):
        """Función que gestiona el movimiento punto a punto con cinemática"""
        estado_seguridad = self.verificar_seguridad()
        velocidad = 0.5 if estado_seguridad == "SLOW" else 1.0
        
        # Aquí envías los datos a tu función de Cinemática Inversa.
        # Recuerda que, por la disposición geométrica de este montaje, 
        # tu matriz del Tool Center Point (TCP) tiene el eje Z apuntando hacia abajo.
        self.robot.mover_a_coordenada(destino_x, destino_y, destino_z, velocidad)
        time.sleep(1) # Simulación de tiempo de viaje

    def run(self):
        """Ciclo principal del modo automático (Se ejecuta 8 veces)"""
        for ciclo in range(1, 9):
            if not self.ejecutando:
                break
                
            self.actualizar_estado.emit(f"Ciclo {ciclo}/8: Iniciando...")

            # 1. IR A PUNTO B (Bodega) con altura de seguridad
            self.mover_robot(self.PUNTO_B[0], self.PUNTO_B[1], self.ALTURA_SEGURIDAD)
            self.mover_robot(self.PUNTO_B[0], self.PUNTO_B[1], self.PUNTO_B[2]) # Bajar
            
            # 2. CAPTURAR IMAGEN Y DETERMINAR PIEZA
            color_detectado = self.camara.detectar_color()
            self.actualizar_estado.emit(f"Ciclo {ciclo}: Objeto {color_detectado} detectado.")
            
            # 3. PICK (Cerrar Gripper)
            self.robot.cerrar_gripper()
            time.sleep(0.5)
            
            # 4. SUBIR A ALTURA DE SEGURIDAD (Mínimo 8cm)
            self.mover_robot(self.PUNTO_B[0], self.PUNTO_B[1], self.ALTURA_SEGURIDAD)

            # 5. DETERMINAR DESTINO Y CÁLCULO DE APILAMIENTO LINEAL
            # Para apilar en línea recta, sumamos un offset (ej. 3cm) por cada pieza
            offset_apilamiento = 3 
            
            if color_detectado == "Rojo":
                destino_x = self.PUNTO_A[0] + (self.cantidad_rojos * offset_apilamiento)
                destino_y = self.PUNTO_A[1]
                destino_z = self.PUNTO_A[2]
                self.cantidad_rojos += 1
            else: # Asumimos Verde
                destino_x = self.PUNTO_C[0] + (self.cantidad_verdes * offset_apilamiento)
                destino_y = self.PUNTO_C[1]
                destino_z = self.PUNTO_C[2]
                self.cantidad_verdes += 1

            # 6. MOVER A DESTINO (Con altura de seguridad)
            self.mover_robot(destino_x, destino_y, self.ALTURA_SEGURIDAD)
            self.mover_robot(destino_x, destino_y, destino_z) # Bajar
            
            # 7. PLACE (Abrir Gripper)
            self.robot.abrir_gripper()
            time.sleep(0.5)
            
            # 8. SUBIR DE NUEVO A ALTURA DE SEGURIDAD
            self.mover_robot(destino_x, destino_y, self.ALTURA_SEGURIDAD)

        self.actualizar_estado.emit("¡Proceso Automático Finalizado!")

    def detener(self):
        """Detiene el hilo de forma segura"""
        self.ejecutando = False