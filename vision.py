# vision.py
import cv2
import numpy as np
import time

class CamaraVision:
    def __init__(self, indice_camara=0):
        # indice_camara=0 normalmente abre la cámara por defecto (USB o la de la Raspberry)
        self.cap = cv2.VideoCapture(indice_camara)
        
        # Reducir la resolución para que la Raspberry Pi no se sature procesando
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        if not self.cap.isOpened():
            print("⚠ Advertencia: No se pudo abrir la cámara. Revisa la conexión.")

    def detectar_pieza(self):
        """
        Toma una foto, procesa la imagen y retorna una tupla (Color, Forma)
        Ejemplo de retorno: ("Rojo", "Cuadrado")
        """
        if not self.cap.isOpened():
            return "Desconocido", "Desconocido"

        # Leemos 5 frames rápidos antes de procesar. 
        # Esto le da tiempo al sensor de la cámara para auto-ajustar el brillo y enfoque.
        for _ in range(5):
            ret, frame = self.cap.read()
            time.sleep(0.05)

        if not ret:
            return "Error", "Error"

        # Convertir la imagen de BGR (estándar) a HSV (Mejor para detectar colores)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 1. DEFINIR RANGOS DE COLOR (Estos valores dependen de la luz de tu cuarto)
        # El color rojo en HSV está en dos extremos del espectro (0-10 y 170-180)
        bajo_rojo1 = np.array([0, 100, 100])
        alto_rojo1 = np.array([10, 255, 255])
        bajo_rojo2 = np.array([170, 100, 100])
        alto_rojo2 = np.array([180, 255, 255])
        
        # Rango para el color Verde
        bajo_verde = np.array([40, 100, 100])
        alto_verde = np.array([80, 255, 255])

        # Crear máscaras (imágenes en blanco y negro donde lo blanco es el color detectado)
        mascara_rojo = cv2.bitwise_or(cv2.inRange(hsv, bajo_rojo1, alto_rojo1), 
                                      cv2.inRange(hsv, bajo_rojo2, alto_rojo2))
        mascara_verde = cv2.inRange(hsv, bajo_verde, alto_verde)

        color_final = "Ninguno"
        forma_final = "Ninguna"
        area_maxima = 500 # Filtro: Ignorar manchas pequeñas menores a 500 píxeles

        # 2. BUSCAR LA FORMA DENTRO DE LAS MÁSCARAS
        for nombre_color, mascara in [("Rojo", mascara_rojo), ("Verde", mascara_verde)]:
            # Encontrar los contornos de los objetos blancos en la máscara
            contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                
                # Si el objeto es lo suficientemente grande
                if area > area_maxima:
                    area_maxima = area
                    color_final = nombre_color
                    
                    # Calcular el perímetro y aproximar la figura a un polígono
                    perimetro = cv2.arcLength(contorno, True)
                    aprox = cv2.approxPolyDP(contorno, 0.04 * perimetro, True)
                    cantidad_vertices = len(aprox)
                    
                    # Clasificar por cantidad de vértices
                    if cantidad_vertices == 3:
                        forma_final = "Triangulo"
                    elif cantidad_vertices == 4:
                        # Diferenciar entre cuadrado y rectángulo usando proporciones
                        x, y, w, h = cv2.boundingRect(aprox)
                        relacion_aspecto = float(w) / h
                        if 0.95 <= relacion_aspecto <= 1.05:
                            forma_final = "Cuadrado"
                        else:
                            forma_final = "Rectangulo"
                    elif cantidad_vertices > 5:
                        forma_final = "Circulo"

        # Opcional: Mostrar lo que ve la cámara (Quitar el comentario para pruebas en PC)
        # cv2.imshow("Camara Robot", frame)
        # cv2.waitKey(1)

        print(f"[Visión] Pieza detectada: {color_final} - {forma_final}")
        return color_final, forma_final

    def apagar_camara(self):
        """Libera el hardware cuando el programa se cierra"""
        self.cap.release()
        cv2.destroyAllWindows()