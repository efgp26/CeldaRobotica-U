# cinematica.py
import math

class CinematicaRobot:
    def __init__(self):
        # Longitudes de eslabones en cm (Deben medirlas físicamente)
        self.L1 = 10.0 # Base a Hombro
        self.L2 = 12.0 # Hombro a Codo
        self.L3 = 12.0 # Codo a Muñeca
        self.L4 = 5.0  # Muñeca a TCP (Gripper)

    def calcular_inversa(self, x, y, z):
        """
        Calcula q1, q2, q3, q4.
        RECUERDA: El eje Z del TCP está orientado hacia abajo en su diseño.
        """
        # --- Ejemplo de cálculo de q1 (Base) ---
        q1 = math.degrees(math.atan2(y, x))
        
        # --- Marcador para cinemática inversa de 3 DoF + Muñeca orientada ---
        # Aquí deberán resolver el desacoplo cinemático o la geometría del brazo.
        q2 = 45.0 # Placeholder
        q3 = 45.0 # Placeholder
        q4 = 90.0 # Muñeca (suele compensar q2 y q3 para mirar abajo)
        
        return q1, q2, q3, q4