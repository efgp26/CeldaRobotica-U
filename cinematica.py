# cinematica.py
import math

class CinematicaRobot:
    def __init__(self):
        # Aquí guardaremos las longitudes de tus eslabones (L1, L2, L3)
        self.L1 = 10.0 
        self.L2 = 10.0
        
    def calcular_inversa(self, x, y, z):
        """
        Calcula los ángulos q1, q2, q3 para el punto (x, y, z).
        Recuerda que el eje Z del TCP está invertido en tu montaje.
        """
        # TODO: Implementar fórmulas matemáticas finales.
        # Por ahora, retornamos 90 grados para todos como prueba.
        q1 = 90
        q2 = 90
        q3 = 90
        return q1, q2, q3