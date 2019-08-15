
from PyQt5.QtWidgets import QWidget,QGridLayout, QPushButton, QStyle, QHBoxLayout, QSpinBox,\
    QGroupBox, QVBoxLayout
from PyQt5.QtGui import QIcon

from src import util

class SettingGroupBox(QGroupBox):

    def __init__(self, label: str, unit: str, minval, maxval, step, parent = None):
        super(SettingGroupBox, self).__init__(parent)
        self.label = label
        self.unit = unit
        self.minval = minval
        self.maxval = maxval
        self.step = step

        self.gBox = QGroupBox(self.label)
        VBox = QVBoxLayout()
        self.gBox.setLayout(VBox)

        hBox = QHBoxLayout()
        self.sBox = QSpinBox()
        self.sBox.setSuffix(self.unit)
        self.sBox.setMinimum(self.minval)

        self.sBox.setMaximum(self.maxval)
        self.sBox.setSingleStep(self.step)

        self.setButton = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton)), 'Send')
        hBox.addWidget(self.sBox)
        hBox.addWidget(self.setButton)

        self.resetButton = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_BrowserReload)), "Reset to defaults")
        VBox.addLayout(hBox)
        VBox.addWidget(self.resetButton)


class DcycleWindow(QWidget):
    def __init__(self, app, parent=None):
        super(DcycleWindow, self).__init__(parent)
        self.app = app
        self.setWindowTitle("Additional setting")
        self.setWindowIcon(QIcon(util.resource_path('../icon/error.png')))

        grid = QGridLayout()
        self.setLayout(grid)

        self.cycleBox = SettingGroupBox("Duty cycle periode", "min", 1, 30, 1)
        self.tspanBox = SettingGroupBox("Sample point", "points", 20, 30000, 1)

        grid.addWidget(self.cycleBox.gBox)
        grid.addWidget(self.tspanBox.gBox)

        self.cycleBox.setButton.clicked.connect(self.setCycle)
        self.cycleBox.resetButton.clicked.connect(self.resetCycle)
        self.tspanBox.setButton.clicked.connect(self.setSpan)
        self.tspanBox.resetButton.clicked.connect(self.resetSpan)

    def setCycle(self):
        cyctime = self.cycleBox.sBox.value()
        self.app.worker.set_winsize(cyctime)

    def resetCycle(self):
        self.cycleBox.sBox.setValue(4)
        self.app.worker.set_winsize(self.cycleBox.sBox.value())

    def setSpan(self):
        samples = self.tspanBox.sBox.value()
        self.app.worker.set_samples(samples)


    def resetSpan(self):
        self.tspanBox.sBox.setValue(300)
        self.app.worker.set_samples(self.tspanBox.sBox.value())