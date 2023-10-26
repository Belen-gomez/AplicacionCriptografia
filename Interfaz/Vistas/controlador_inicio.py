from Vistas.inicio import Ui_Dialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget

class ControladorInicio(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.InicializarGui()

    def InicializarGui(self):
        print("Inicializando GUI")
        ''' self.ui.pushButton.clicked.connect(self.IniciarSesion)
        self.ui.pushButton_2.clicked.connect(self.Registrarse) '''