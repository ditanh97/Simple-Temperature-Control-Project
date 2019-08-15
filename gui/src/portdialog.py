from PyQt5.QtWidgets import QGridLayout, QLabel, QGroupBox, \
    QDialog, QComboBox, QDialogButtonBox, QFormLayout
from PyQt5.QtGui import QIcon
from serial.tools import list_ports

from src import util

speed = [str(v) for v in [9600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]]

class portWindow(QDialog):

    def __init__(self, app, parent=None):
        super(portWindow, self).__init__(parent)
        self.app = app

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.setWindowTitle("Port Setting")
        self.setWindowIcon(QIcon(util.resource_path('../icon/port.png')))

        self.buttons = QGroupBox()

        grid = QGridLayout()
        self.setLayout(grid)

        portCbox = QComboBox()
        found_ports = []
        for port in list(list_ports.comports()):
            found_ports.append(port.device)
        portCbox.addItems(found_ports)
        grid.addWidget(QLabel("Port: "), 1, 0, 1, 2)
        grid.addWidget(portCbox, 1, 2, 1, 2)

        speedCbox =QComboBox()
        speedCbox.addItems(speed)
        grid.addWidget(QLabel("Baud Rate: "), 3, 0, 1, 2)
        grid.addWidget(speedCbox, 3, 2, 1, 2)

        #need to debug
        self.port = portCbox.currentText()
        self.speed = float(speedCbox.currentText())

        layout = QFormLayout()
        layout.addWidget(button_box)
        self.buttons.setLayout(layout)
        grid.addWidget(self.buttons,4,0,1,4)



