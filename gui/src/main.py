"""
ui and function for control widget
run the application from here

"""


from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox,\
    QApplication, QGroupBox, QVBoxLayout, QCheckBox, QLabel,\
    QMainWindow, QPushButton, QAction, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication, QTimer
from PyQt5.QtGui import QIcon
import string
from multiprocessing import freeze_support

from src import util
from src import miscgraphic
from src import portdialog
from src import cycledialog
import processsrc.mainWorker as worker
import processsrc.graphWorker as graph
from processsrc.pid import PID


class Central(QWidget):
    def __init__(self, app: QApplication, tool: QMainWindow, parent=None):

        super(Central, self).__init__(parent)
        self.app = app
        self.tool = tool
        self.createUI()
        self.connectHandler()

    def createUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("Mode")
        self.modeComboBox.addItem("Manual")
        self.modeComboBox.addItem("PID Control")

        self.valtoControllerBox = [
            miscgraphic.ValueGroupBox('Setpoint', unit='C', worker=self.app.worker),
            miscgraphic.ValueGroupBox('kC', unit='C/kW', worker=self.app.worker),
            miscgraphic.ValueGroupBox('tauI', unit='menit', worker=self.app.worker),
            miscgraphic.ValueGroupBox('tauD', unit='menit', worker=self.app.worker)
         ]

        self.sendPID = QPushButton("Simpan Parameter")
        self.sendPID.setEnabled(False)

        self.graphs = graph.CustomGraphicsLayoutWidget()

        self.outputGroupBox = QGroupBox()
        self.outputGroupBox.setTitle("Data Sistem")
        vBox = QVBoxLayout()

        tempLabelTemplate = string.Template(f"Temperature (C): <b>{'{:.2f}'}</b>").safe_substitute()
        tempLabel = QLabel()
        self.app.lstLabelsForData.append(tempLabel)
        self.app.lstTemplates.append(tempLabelTemplate)
        tempLabel.setText(tempLabelTemplate.format(self.app.lstSerData[0]))
        vBox.addWidget(tempLabel)

        q1LabelTemplate = string.Template(f"Heater 1 (%): <b>{'{:.1f}'}</b>").safe_substitute()
        q1Label = QLabel()
        self.app.lstLabelsForData.append(q1Label)
        self.app.lstTemplates.append(q1LabelTemplate)
        q1Label.setText(q1LabelTemplate.format(self.app.lstSerData[1]))
        vBox.addWidget(q1Label)

        q2LabelTemplate = string.Template(f"Heater 2 (%): <b>{'{:.1f}'}</b>").safe_substitute()
        q2Label = QLabel()
        self.app.lstLabelsForData.append(q2Label)
        self.app.lstTemplates.append(q2LabelTemplate)
        q2Label.setText(q2LabelTemplate.format(self.app.lstSerData[2]))
        vBox.addWidget(q2Label)

        cycleLabelTemplate = string.Template(f"Duty Cycle (min): <b>{'{:.1f}'}</b>").safe_substitute()
        dcLabel = QLabel()
        self.app.lstLabelsForData.append(dcLabel)
        self.app.lstTemplates.append(cycleLabelTemplate)
        dcLabel.setText(cycleLabelTemplate.format(self.app.lstSerData[3]))
        vBox.addWidget(dcLabel)

        self.chBox_export = QCheckBox()
        self.chBox_export.setEnabled(True)
        self.chBox_export.setText("Export to CSV")

        self.app.worker.set_label(self.app.lstLabelsForData, self.app.lstTemplates)
        self.outputGroupBox.setLayout(vBox)

        grid.addWidget(self.modeComboBox, 0, 0, 1, 2)
        for parameterBox, yPosition in zip(self.valtoControllerBox,[1,4,7,10]):
            grid.addWidget(parameterBox, yPosition, 0, 3, 2)
        grid.addWidget(self.sendPID, 13,0,1,2)
        grid.addWidget(self.outputGroupBox, 14,0,5,2)
        grid.addWidget(self.chBox_export, 20, 0, 1, 2)
        grid.addWidget(self.graphs,0,2,21,6)


    def connectHandler(self):
        self.modeComboBox.activated.connect(self.mode)
        self.sendPID.clicked.connect(self.sendPIDButton)
        self.chBox_export.stateChanged.connect(self.export)

    #slot function
    def mode(self):
        mod = self.modeComboBox.currentText()
        if mod == "Manual":
            self.app.manual = True
            self.tool.enableq1 = True

        if mod == "PID Control":
            self.app.manual = False
            self.tool.enableq1 = False

        self.sendPID.setEnabled(not self.app.manual)

        for var in self.valtoControllerBox:
                var.enable_pid(not self.app.manual)

        QMessageBox.information(self, 'Info', "Mode {} diterapkan, lanjutkan dengan menekan tombol play untuk memulai".format(mod))

        # graph setting
        self.graphs.set_mode(mod)
        ngraph = self.graphs.get_graphs()
        ncurve = self.graphs.get_curves()
        legend = self.graphs.get_legend()
        self.app.worker.set_lines(ngraph, ncurve, legend)
        self.app.worker.set_mode(mod)

    def sendPIDButton(self):
        fsp = float(self.valtoControllerBox[0].writeLine.text())
        fKc = float(self.valtoControllerBox[1].writeLine.text())
        ftauI = float(self.valtoControllerBox[2].writeLine.text())
        ftauD = float(self.valtoControllerBox[3].writeLine.text())
        self.app.pid.set_tunning(fKc,ftauI, ftauD)
        self.app.pid.set_setpoint(fsp)
        for par in self.valtoControllerBox:
            par.refresh_val()

    def export(self, state):
        if state == Qt.Checked:
            print("mode saving is set")
            self.app.worker.set_save(True)
        else:
            self.app.worker.set_save(False)



class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, parent=None):

        super(MainWindow, self).__init__(parent)
        self.updateTimer = None
        self.app = app
        self.setWindowTitle(QCoreApplication.applicationName())
        self.setWindowIcon(QIcon(util.resource_path('../icon/logo.png')))
        self.enableq1 = False
        self.centralWidget = Central(app=app, tool=self)
        self.setCentralWidget(self.centralWidget)
        self.toolUI()
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self._update)


    def _update(self):
        print("timer is updated")
        self.app.worker.update()


        # toolBar
    def toolUI(self):
        portAction = QAction(QIcon(util.resource_path('../icon/port.png')), 'Port Setting', self)
        portAction.setStatusTip("Set the port to Arduino")

        dcycleAction = QAction(QIcon(util.resource_path('../icon/error.png')), 'More Setting', self)
        dcycleAction.setStatusTip("reset time period for duty cycle")
        self.dcycleWindow = cycledialog.DcycleWindow(app=self.app)

        rqrdToolBar = self.addToolBar('required setting')
        rqrdToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        rqrdToolBar.addAction(portAction)
        rqrdToolBar.addAction(dcycleAction)

        startstopAction = QAction(QIcon(util.resource_path('../icon/play.png')), 'Start/Stop', self)
        startstopAction.setStatusTip("Click to play/stop the DAQ system")


        startstopToolBar = self.addToolBar('play pause')
        startstopToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        startstopToolBar.addAction(startstopAction)
        self.startstopButton = startstopToolBar.widgetForAction(startstopAction)
        self.startstopButton.setEnabled(False)
        self.startstopButton.setCheckable(True)
        self.startstopButton.setChecked(False)

        mainAction = QAction(QIcon(util.resource_path('../icon/main.png')), 'On/Off Heater 1', self)
        mainAction.setStatusTip("Click to on/off main heater")

        mainToolBar = self.addToolBar('Q1 heater')
        mainToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        mainToolBar.addAction(mainAction)
        self.mainButton = mainToolBar.widgetForAction(mainAction)
        self.mainButton.setEnabled(False)
        self.mainButton.setCheckable(True)
        self.mainButton.setChecked(False)

        distAction = QAction(QIcon(util.resource_path('../icon/dist.png')), 'On/Off Heater 2', self)
        distAction.setStatusTip("click to on/off disturbance heater")


        distToolBar = self.addToolBar('Q2 heater')
        distToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        distToolBar.addAction(distAction)
        self.distButton = distToolBar.widgetForAction(distAction)
        self.distButton.setEnabled(False)
        self.distButton.setCheckable(True)
        self.distButton.setChecked(False)

        forceAction = QAction(QIcon(util.resource_path('../icon/stop.png')), 'Force Stop', self )
        forceAction.setStatusTip("Apply emergency stop")
        forceAction.setEnabled(False)

        forceToolBar = self.addToolBar("Emergency")
        forceToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        forceToolBar.addAction(forceAction)
        self.forceButton = forceToolBar.widgetForAction(forceAction)
        self.forceButton.setEnabled(False)
        self.forceButton.setCheckable(True)
        self.forceButton.setChecked(False)

        self.statusBar().show()

        portAction.triggered.connect(self.setport)
        dcycleAction.triggered.connect(self.dcycleWindow.show)
        startstopAction.triggered.connect(self.startstop)
        mainAction.triggered.connect(self.setmain)
        distAction.triggered.connect(self.setdist)
        forceAction.triggered.connect(self.forcestop)


    def setport(self):
        connection = portdialog.portWindow(app=self.app)
        if connection.exec_():
            portname = str(connection.port)
            bdrate = connection.speed
            self.app.worker.set_arduino(portname, bdrate)
            self.startstopButton.setEnabled(True)
            print("Sistem DAQ tersambung pada port: {}; bd rate : {}".format(portname,bdrate))

    def startstop(self):
        if self.app.worker.toggleplay():
            self.updateTimer.start(1000)
            self.centralWidget.chBox_export.setEnabled(False)
            self.startstopButton.setChecked(True)
            self.distButton.setEnabled(True)
            self.forceButton.setEnabled(True)
            if self.enableq1:
                self.mainButton.setEnabled(True)
        else:
            self.updateTimer.stop()
            self.centralWidget.chBox_export.setEnabled(True)
            self.startstopButton.setChecked(False)
            self.distButton.setEnabled(False)
            self.forceButton.setEnabled(False)
            if self.enableq1:
                self.mainButton.setEnabled(False)

    def setmain(self):
        if self.app.worker.togglemain():
            self.mainButton.setChecked(True)
        else:
            self.mainButton.setChecked(False)

    def setdist(self):
        if self.app.worker.toggledist():
            self.distButton.setChecked(True)
        else:
            self.distButton.setChecked(False)

    def forcestop(self):
        mbResult = QMessageBox.question(self, 'Extract',
                                            "Are you sure to stop?",
                                            QMessageBox.Yes | QMessageBox.No)
        if mbResult == QMessageBox.Yes:
            print("Successful Closed Application")
            QCoreApplication.instance().quit()
            self.updateTimer.stop()
            self.app.worker.force_stop()


    def hideEvent(self, *args, **kwargs):
        super(MainWindow, self).hideEvent(*args, **kwargs)




class MainApplication(QApplication):
    def __init__(self,argv:list):
        super(MainApplication, self).__init__(argv)

        self.manual: bool = False
        self.pid = PID()
        self.worker = worker.MainWorker(self.pid, is_manmode=self.manual)

        #for storing parameter
        self.lstLabelsForData = []
        self.lstTemplates = []
        self.lstSerData = [0, 0, 0, 0]

        self.mainWindow = MainWindow(app=self)
        self.mainWindow.show()



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget
    freeze_support()
    QCoreApplication.setApplicationName("Sistem DAQ LABTEK v1")
    app = MainApplication(sys.argv)
    sys.exit(app.exec_())

