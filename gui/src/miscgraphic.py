"""
miscgraphic.py - contain ValueGroupBox

ValueGroupBox
    QGroupBox widget centered around a single numerical variable

modified from https://github.com/ussserrr/pid-controller-gui/blob/master/pid-controller-gui/miscgraphics.py
"""


import string
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox, QLabel, \
    QLineEdit

# local imports
import processsrc.mainWorker as worker


class ValueGroupBox(QGroupBox):
    """
    QGroupBox widget centered around a single numerical variable. It combines a QLabel to show the current value.
    """

    def __init__(self, label: str, unit: str, float_fmt: str='{:.1f}', worker: worker.MainWorker=None, parent=None):
        """
        ValueGroupBox constructor

        :param label: name of the GroupBox
        :param unit: unit of the respective label
        :param worker: processsrc.MainWorker instance to connect to
        :param parent: [optional] parent class
        """

        super(ValueGroupBox, self).__init__(parent)


        self.setTitle(f"Parameter {label.capitalize()}")

        self.label = label

        self.worker = worker

        # prepare a template string using another template string :)
        self.valLabelTemplate = string.Template(f"Current $label: <b>{float_fmt}</b>").safe_substitute(label=label)
        self.valLabel = QLabel()



        self.unitLabel = QLabel(unit)

        self.writeLine = QLineEdit()
        self.writeLine.setPlaceholderText(f"Masukkan nilai '{label}'")
        self.writeLine.setValidator(QDoubleValidator())  # we can set a Locale() to correctly process floats
        self.writeLine.setToolTip("Float value")
        self.writeLine.setEnabled(True)


        hBox1 = QHBoxLayout()
        hBox1.addWidget(self.valLabel)
        hBox1.addStretch()  # need to not distort the button when resizing
        hBox1.addSpacing(25)
        hBox1.addWidget(self.unitLabel)

        vBox1 = QVBoxLayout()
        vBox1.addWidget(self.writeLine)
        vBox1.addLayout(hBox1)

        self.setLayout(vBox1)
        self.enable_pid(False)


    def enable_pid(self, bool):
        self.valLabel.setEnabled(bool)
        self.writeLine.setEnabled(bool)

    def refresh_val(self) -> None:
        """
        Read a value from the worker

        :return: None
        """

        if self.worker is not None:
            self.valLabel.setText(self.valLabelTemplate.format(self.worker.disp(self.label)))
        else:
            self.valLabel.setText(self.valLabelTemplate.format(0.000))




