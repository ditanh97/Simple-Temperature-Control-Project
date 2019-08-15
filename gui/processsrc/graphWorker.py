from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph
import numpy as np
import multiprocessing
from multiprocessing import Process, Queue
from processsrc.ringBuffer import RingBuffer


PLOT_COLORS = ['r', 'g', 'k', 'b']
DEFAULT_SAMPLES = 5
MANUAL_LEGEND = ['Temperatur Proses', '%Heater Utama']
PID_LEGEND = ['Temperatur Proses', 'Setpoint', '%Heater Utama', '% Output PID']

GRAPH_TIME_SPAN_SEC = 60  # Length of the steps in seconds
GRAPH_TEMP_MAX = 70
GRAPH_TEMP_MIN = -130

class CustomGraphicsLayoutWidget(GraphicsLayoutWidget):

    def __init__(self, nName: tuple = ("Temperature", "Heater Power"),
                 nUnit: tuple = ("degC", "%P"), parent=None):

        assert len(nName) == len(nUnit)
        pyqtgraph.setConfigOption('background', 'w')
        pyqtgraph.setConfigOption('foreground', 'k')

        super(CustomGraphicsLayoutWidget, self).__init__(parent)

        self.nName = nName
        self.nUnit = nUnit
        self.curves = []
        self.graphs = []
        self.legends = []
        self._samples = DEFAULT_SAMPLES
        self._plt = GraphicsLayoutWidget()




    def set_mode(self, mode):
        if mode == "Manual":
            self.is_manmode = True
        else:
            self.is_manmode = False
        self._clear_plot()
        self._configure_plot()

    def _clear_plot(self):

        self.clear() #this is crucial fiuhh
        self.curves = []
        self.graphs = []


    def _configure_plot(self):
        n = len(self.nName)
        npos = np.linspace(1, n, n)
        if self.is_manmode:
            self.nLine = 1
            self.legend = MANUAL_LEGEND
        else:
            self.nLine = 2
            self.legend = PID_LEGEND


        for name, ypos, unit in zip(self.nName, npos, self.nUnit):
            self._plt.setBackground(background=None)
            self._plt.setAntialiasing(True)
            if name == self.nName[-1]:
                graph = self.addPlot(labels={'right': name, 'bottom': "Waktu (detik)"})
            else:
                graph = self.addPlot(labels={'right': name})
            for i in range(self.nLine):
                curve = [graph.plot()]
                self.curves.extend(curve)
            graph.setLabel('right', name, unit)
            self.graphs.append(graph)
            self.nextRow()


    def get_curves(self):
        print("original curves: {}".format(self.curves))
        return self.curves

    def get_graphs(self):
        print("original graphs: {}".format(self.graphs))
        return self.graphs

    def get_legend(self):
        return self.legends




class GraphProcess(Process):
    def __init__(self, graphs, curves, legends):

        Process.__init__(self)

        self._time_buffer = None
        self._data_buffers = None
        self._int_queue = Queue()
        self._calc_queue = Queue()

        self._exit = multiprocessing.Event()

        self.graphs = graphs
        self.curves = curves
        self.legends = legends
        self.nLine = len(curves)
        self.colors = PLOT_COLORS[:self.nLine]


        self.datain = None
        self.datacalc = None



    def add(self, time, data):
        self._int_queue.put([time, data])


    def addinter(self, sp, outval):
        self._calc_queue.put([sp, outval])


    def run(self) -> None:
        while not self._exit.is_set():
            pass


    def update(self):
        self._consume_queue()
        for data_buffer, curve, color in zip(self._data_buffers, self.curves, self.colors):
            curve.setData(x=self._time_buffer.get_all(), y=data_buffer.get_all(), pen=color)


    def _consume_queue(self):
        if not self._int_queue.empty():
            datain = self._int_queue.get(block=False)
            self._time_buffer.append(datain[0])
            data = datain[1]
            print("serial to graph data = {}".format(data))
            if self.nLine == 4:
                self._data_buffers[0].append(data[0])
                self._data_buffers[2].append(data[1])
            else:
                for idx, d in zip(range(2), data):
                    self._data_buffers[idx].append(d)

        if not self._calc_queue.empty():
            self.datacalc = self._calc_queue.get(block=False)
        else:
            self.datacalc = [0, 0]

        if self.nLine == 4:
            self._data_buffers[1].append(self.datacalc[0])
            self._data_buffers[3].append(self.datacalc[1])



    def reset_buffers(self, samples):
        self._data_buffers = []
        for i in PLOT_COLORS:
            self._data_buffers.append(RingBuffer(samples))
        self._time_buffer = RingBuffer(samples)



    def stop(self):
        self._exit.set()
        while not self._int_queue.empty():
            self._int_queue.get()
        while not self._calc_queue.empty():
            self._calc_queue.get()
        print("graph process stop")















