"""

"""

from multiprocessing import Queue
from processsrc.acqWorker import SerialProcess, DisplayProcess
from processsrc.graphWorker import GraphProcess
from processsrc.csvWorker import CSVProcess
from processsrc.parserWorker import ParserProcess


process_join_timeout_ms = 1000
DEFAULT_SAMPLES = 10

class MainWorker:
    def __init__(self, pidobj, is_manmode = True, export=False, port=None, speed=None):
        self._is_manmode = is_manmode
        self._is_play = False
        self._is_q1_on = False
        self._is_q2_on = False
        self._export = export
        self._port = port
        self._speed = speed
        self._graphs = None
        self._curves = None
        self._pid = pidobj
        self._temp_queue = Queue()
        self._parameters = None
        self._setpoint = None
        self._output = 0.0
        self._label = []
        self._template = []
        self._spoints = DEFAULT_SAMPLES

        self._winsize = 5
        self._dist = 0
        self._mode = 0

        self._disp_process = None
        self._acq_contr_process = None
        self._parser_process = None
        self._csv_process = None
        self._graphic_process = None

    def set_lines(self, graphs, curves, legends):
        self._graphs = graphs
        self._curves = curves
        self._legends = legends


    def set_mode(self, mode):
        if mode == "Manual":
            self._is_manmode = True
            self._mode = 0
        else:
            self._is_manmode = False
            self._mode = 1


    def set_arduino(self, port, brate):
        self._port = port
        self._speed = brate

    def set_save(self, enable: bool):
        self._export = enable


    def set_winsize(self, mintime):
        self._winsize = mintime
        print("duty cycle: {}".format(mintime))


    def  set_label(self, label, template):
        self._label = label
        self._template = template

    def set_samples(self, points):
        self._spoints = points
        print("point buffer : {}".format(points))


    def toggleplay(self):
        if self._is_play:
            self._stop()
            return False
        else:
            if self._start():
                return True
            else:
                return False


    def _start(self):
        self._graphic_process = GraphProcess(self._graphs, self._curves, self._legends)
        self._graphic_process.reset_buffers(self._spoints)
        print("Spoint: {}".format(self._spoints))
        self._disp_process = DisplayProcess(self._label, self._template)
        if self._export:
            self._csv_process =CSVProcess(manmode=self._is_manmode)
            self._parser_process = ParserProcess(self._temp_queue,self._graphic_process, store_reference=self._csv_process)
        else:
            self._parser_process = ParserProcess(self._temp_queue, self._graphic_process)
        self._acq_contr_process = SerialProcess(parser_process=self._parser_process, display_process=self._disp_process, mode_process= self._mode)
        if self._acq_contr_process.open(self._port, self._speed):
            self._parser_process.start()
            if self._export:
                self._csv_process.start()
            self._acq_contr_process.add([0.0, self._winsize, self._mode, 0])  # initial value
            self._acq_contr_process.start()
            self._disp_process.start()
            self._graphic_process.start()
            self._is_play = True
            return True
        else:
            return False

    def update(self):
        if self._is_manmode:
            self._calc_manual()
        else:
            self._calc_pid()
            print("pid calculate")
        self._graphic_process.update()
        self._disp_process.update()
        print("update")


    def _calc_pid(self):
        while not self._temp_queue.empty() and self._is_play:
            temp = self._temp_queue.get()
            self._pid.update(temp)
            self._output = self._pid.get_output
            print("pid calculation: {}".format(self._output))
            self._parameters = self._pid.get_parameters
            self._setpoint = self._pid.get_setpoint
            self._acq_contr_process.add([self._output, self._winsize, self._mode, self._dist])
            if self._export:
                self._csv_process.addinter(self._output, self._setpoint, self._parameters)
            self._graphic_process.addinter(self._setpoint, self._output)



    def _calc_manual(self):
        self._consume_queue()
        self._winsize = 0.0
        self._acq_contr_process.add([self._output, self._winsize, self._mode, self._dist])

    def togglemain(self):
        if self._is_q1_on:
            self._stop_main()
            return False
        else:
            self._start_main()
            return True

    def _start_main(self):
        self._output = 100.0
        self._is_q1_on = True

    def _stop_main(self):
        self._output = 0.0
        self._is_q1_on = False

    def toggledist(self):
        if self._is_q2_on:
            self._stop_dist()
            return False
        else:
            self._start_dist()
            return True

    def _start_dist(self):
        self._dist = 1
        self._is_q2_on = True

    def _stop_dist(self):
        self._dist = 0
        self._is_q2_on = False


    def _stop(self):
        self._consume_queue()
        for process in [self._acq_contr_process, self._parser_process, self._graphic_process, self._csv_process, self._disp_process]:
            if process is not None and process.is_alive():
                process.stop()
                process.join(process_join_timeout_ms)
        self._clear_value()
        self._is_play = False


    def force_stop(self):
        self._stop()
        self._stop_dist()
        if self._is_manmode:
            self._stop_main()



    def _consume_queue(self):
        if not self._temp_queue.empty():
            self._temp_queue.get()


    def _clear_value(self):
        self._export = False
        self._parameters = None
        self._setpoint = None
        self._output = None
        self._winsize = 11
        self._main = 0
        self._dist = 0


    def disp(self, label):
        param = self._pid.get_parameters
        if label == 'Setpoint':
            return self._pid.get_setpoint
        elif label == 'kC':
            return param[0]
        elif label == 'tauI':
            return param[1]
        else:
            return param[2]



