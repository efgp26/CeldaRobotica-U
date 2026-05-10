# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
import logo_ecci_rc 

class RobotControlGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Celda Robótica ECCI - 4 GDL")
        self.resize(1100, 800)
        self.setStyleSheet("QMainWindow { background-color: #f5f6fa; }")
        self.initUI()

    def initUI(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Encabezado Industrial
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("background-color: #2c3e50; border-radius: 5px;")
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        
        title_label = QtWidgets.QLabel("ESTACIÓN DE CONTROL - ROBOT 4 GDL")
        title_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addWidget(header_frame)

        # Layout Principal en Cuadrícula
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(15)
        main_layout.addLayout(grid_layout)

        # Estilo común para los GroupBoxes
        group_style = """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 1ex;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
                color: #2c3e50;
            }
        """

        # ============================================================
        # 1. PANEL MODO MANUAL (4 SLIDERS)
        # ============================================================
        self.group_manual = QtWidgets.QGroupBox("CONTROL MANUAL")
        self.group_manual.setStyleSheet(group_style)
        manual_layout = QtWidgets.QVBoxLayout()
        
        # Sliders para las 4 articulaciones (Base, Hombro, Codo, Muñeca)
        self.sliders = []
        nombres_art = ["Base (q1)", "Hombro (q2)", "Codo (q3)", "Muñeca (q4)"]
        
        for nombre in nombres_art:
            s_container = QtWidgets.QVBoxLayout()
            lbl = QtWidgets.QLabel(nombre)
            lbl.setStyleSheet("font-weight: normal; color: #34495e;")
            
            sld_layout = QtWidgets.QHBoxLayout()
            sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            sld.setRange(0, 180)
            sld.setValue(90)
            
            val_lbl = QtWidgets.QLabel("90°")
            val_lbl.setMinimumWidth(30)
            # Conexión simple para actualizar el texto del ángulo
            sld.valueChanged.connect(lambda v, l=val_lbl: l.setText(f"{v}°"))
            
            sld_layout.addWidget(sld)
            sld_layout.addWidget(val_lbl)
            
            s_container.addWidget(lbl)
            s_container.addLayout(sld_layout)
            manual_layout.addLayout(s_container)
            self.sliders.append(sld)

        # Gripper
        manual_layout.addSpacing(10)
        grip_btn_layout = QtWidgets.QHBoxLayout()
        self.btn_pick = QtWidgets.QPushButton("CERRAR GRIPPER")
        self.btn_place = QtWidgets.QPushButton("ABRIR GRIPPER")
        self.btn_pick.setStyleSheet("background-color: #34495e; color: white; height: 30px;")
        self.btn_place.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; height: 30px;")
        grip_btn_layout.addWidget(self.btn_pick)
        grip_btn_layout.addWidget(self.btn_place)
        manual_layout.addLayout(grip_btn_layout)
        
        self.group_manual.setLayout(manual_layout)
        grid_layout.addWidget(self.group_manual, 0, 0)

        # ============================================================
        # 2. PANEL MODO SEMIAUTOMÁTICO
        # ============================================================
        self.group_semi = QtWidgets.QGroupBox("POSICIONAMIENTO CARTESIANO")
        self.group_semi.setStyleSheet(group_style)
        semi_layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()
        self.input_x = QtWidgets.QLineEdit()
        self.input_y = QtWidgets.QLineEdit()
        self.input_z = QtWidgets.QLineEdit()
        
        # Nota: Recordar que en el main procesaremos el eje Z invertido según el diseño
        for inp in [self.input_x, self.input_y, self.input_z]:
            inp.setFixedWidth(80)
            inp.setAlignment(QtCore.Qt.AlignCenter)

        form_layout.addRow("Coordenada X (cm):", self.input_x)
        form_layout.addRow("Coordenada Y (cm):", self.input_y)
        form_layout.addRow("Coordenada Z (cm):", self.input_z)
        semi_layout.addLayout(form_layout)
        
        self.btn_go = QtWidgets.QPushButton("EJECUTAR MOVIMIENTO")
        self.btn_go.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; height: 40px;")
        semi_layout.addWidget(self.btn_go)
        
        self.group_semi.setLayout(semi_layout)
        grid_layout.addWidget(self.group_semi, 0, 1)

        # ============================================================
        # 3. PANEL MODO AUTOMÁTICO Y LOGO
        # ============================================================
        self.group_auto = QtWidgets.QGroupBox("SISTEMA AUTOMÁTICO")
        self.group_auto.setStyleSheet(group_style)
        auto_layout = QtWidgets.QVBoxLayout()
        
        self.lbl_estado = QtWidgets.QLabel("SISTEMA LISTO")
        self.lbl_estado.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_estado.setStyleSheet("color: #27ae60; font-size: 14px; font-weight: bold; background: #ebf5fb; padding: 10px; border-radius: 5px;")
        auto_layout.addWidget(self.lbl_estado)
        
        self.btn_start = QtWidgets.QPushButton("INICIAR CICLO (8 PIEZAS)")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setStyleSheet("background-color: #27ae60; color: white; font-size: 14px; font-weight: bold;")
        auto_layout.addWidget(self.btn_start)
        
        # Logo y Créditos integrados
        auto_layout.addSpacing(20)
        self.label_logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/luc/LOGO_ECCI.jpg")
        self.label_logo.setPixmap(pixmap)
        self.label_logo.setScaledContents(True)
        self.label_logo.setMaximumSize(220, 100)
        auto_layout.addWidget(self.label_logo, alignment=QtCore.Qt.AlignCenter)
        
        cred_lbl = QtWidgets.QLabel("Ingeniería Mecatrónica\nDavid Fernando Monroy Moya")
        cred_lbl.setAlignment(QtCore.Qt.AlignCenter)
        cred_lbl.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        auto_layout.addWidget(cred_lbl)
        
        self.group_auto.setLayout(auto_layout)
        grid_layout.addWidget(self.group_auto, 1, 0)

        # ============================================================
        # 4. VISUALIZACIÓN URDF
        # ============================================================
        self.urdf_placeholder = QtWidgets.QFrame()
        self.urdf_placeholder.setStyleSheet("background-color: #ffffff; border: 2px solid #34495e; border-radius: 8px;")
        urdf_layout = QtWidgets.QVBoxLayout(self.urdf_placeholder)
        
        # Aquí se integrará el canvas del robot
        self.lbl_urdf_info = QtWidgets.QLabel("VISUALIZADOR DEL MODELO URDF")
        self.lbl_urdf_info.setStyleSheet("color: #bdc3c7; font-weight: bold;")
        self.lbl_urdf_info.setAlignment(QtCore.Qt.AlignCenter)
        urdf_layout.addWidget(self.lbl_urdf_info)

        grid_layout.addWidget(self.urdf_placeholder, 1, 1)

        # Proporciones
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 2)
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

    def actualizar_estado(self, mensaje, color="#2980b9"):
        self.lbl_estado.setText(mensaje.upper())
        self.lbl_estado.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; background: #ebf5fb; padding: 10px; border-radius: 5px;")