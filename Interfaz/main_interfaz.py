from PyQt5 import QtWidgets
from Vistas.controlador_inicio import ControladorInicio

import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    inicio = ControladorInicio()
    inicio.show()
    sys.exit(app.exec_())