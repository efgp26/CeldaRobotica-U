# interfaz.py
from PyQt5 import QtCore, QtGui, QtWidgets
import logo_ecci_rc # Tu archivo de recursos compilado

class RobotControlGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prototipo Celda Robótica - Robot de 3 DoF")
        self.resize(850, 650)
        self.initUI()

    def initUI(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        title_label = QtWidgets.QLabel("Prototipo Celda Robotica")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title_label)

        grid_layout = QtWidgets.QGridLayout()
        main_layout.addLayout(grid_layout)

        # Panel Automático y Estado (El que usaremos ahora)
        bottom_left_layout = QtWidgets.QVBoxLayout()
        group_auto = QtWidgets.QGroupBox("Panel Automático")
        auto_layout = QtWidgets.QVBoxLayout()
        
        self.lbl_estado = QtWidgets.QLabel("Estado: Listo")
        self.lbl_estado.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_estado.setStyleSheet("font-size: 16px; color: blue;")
        auto_layout.addWidget(self.lbl_estado)
        
        # Este botón es la clave
        self.btn_start = QtWidgets.QPushButton("¡ Start Auto !")
        self.btn_start.setMinimumHeight(40)
        auto_layout.addWidget(self.btn_start)
        
        group_auto.setLayout(auto_layout)
        bottom_left_layout.addWidget(group_auto)
        
        # Logo
        self.label_logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/luc/LOGO_ECCI.jpg") 
        self.label_logo.setPixmap(pixmap)
        self.label_logo.setScaledContents(True) 
        self.label_logo.setMaximumSize(200, 100) 
        bottom_left_layout.addWidget(self.label_logo, alignment=QtCore.Qt.AlignCenter)
        
        grid_layout.addLayout(bottom_left_layout, 1, 0)
        
        # Placeholder para URDF
        self.urdf_placeholder = QtWidgets.QFrame()
        self.urdf_placeholder.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.urdf_placeholder.setStyleSheet("background-color: #ffffff; border: 1px dashed #aaa;")
        urdf_layout = QtWidgets.QVBoxLayout(self.urdf_placeholder)
        urdf_label = QtWidgets.QLabel("Espacio para el modelo URDF")
        urdf_label.setAlignment(QtCore.Qt.AlignCenter)
        urdf_layout.addWidget(urdf_label)
        grid_layout.addWidget(self.urdf_placeholder, 1, 1)

    def actualizar_estado(self, mensaje):
        """Permite cambiar el texto desde el hilo automático"""
        self.lbl_estado.setText(f"Estado: {mensaje}")