from serial import Serial, SerialException
from serial.tools import list_ports
from multiprocessing import Process, Queue
from struct import unpack_from, pack
from time import time, sleep
import multiprocessing

pid_byte = {
    'T' : 4,
    'Q1' : 4,
    'Q2' :4,
    'pC' : 4
}

man_byte = {
    'T' : 4,
    'Q1' : 4,
    'Q2' :4
}

# pid_types = ['<f', '<?', '<?', '<l']

pid_types = ['<f', '<f', '<f', '<l']
man_types = ['<f', '<f', '<f']


class SerialProcess(Process):
    """
    Wrapper for Serial Read from Arduino in bytes and Write data in
    String to Arduino
    """

    def __init__(self, parser_process, display_process, mode_process):
        """
        Initialises values for processes
        :param parser_process: Reference to parser instance
        :type parser_process: ParserProcess
        """
        Process.__init__(self)
        self._exit = multiprocessing.Event()
        self._parser = parser_process
        self._display = display_process
        self._ispid = mode_process
        self._ser = Serial()
        self._out_queue = Queue()
        self._numbytedict = None
        self._typedata = None



    def open(self, port, speed, timeout=None):
        """
        :param port: Serial port name
        :param speed: baud rate in bps
        :param timeout: general connection time out, 0 == nonblocking mode
        :return: True if the port is available
        """
        try:
            self._ser.port = port
            self._ser.baudrate = speed
            self._ser.timeout = timeout

            print("open serial port")



        except SerialException:
            print("error in opening port")
        return self._is_port_available(self._ser.port)


    def _is_port_available(self, port):
        for p in self._find_ports():
            if p == port:
                return True
        return False

    @staticmethod
    def _find_ports():
        ports = []
        for port in list(list_ports.comports()):
            ports.append(port.device)

        return ports


    def run(self):
        print("serial process begin")
        if self._ispid:
            self._numbytedict = pid_byte
            self._typedata = pid_types
        else:
            self._numbytedict = man_byte
            self._typedata = man_types
        print("type data: {}".format(self._typedata))

        if self._is_port_available(self._ser.port):
            if not self._ser.isOpen():
                self._ser.open()
                tstamp = time()
                while not self._exit.is_set():
                    self._send_read(tstamp)
                self._ser.close()



    def _send_read(self, tstamp):

        if not self._out_queue.empty():
            outval = self._out_queue.get()
            self._ser.reset_output_buffer() # Clear output buffer
            self._ser.write(outval)

        self._ser.reset_input_buffer()
        SIZES = [val for val in self._numbytedict.values()]
        nBufferLen = sum(SIZES)
        buffer = bytearray(nBufferLen)
        try:
            lstSerialData = []
            stime = float("{0:.3f}".format(time() - tstamp))
            self._ser.readinto(buffer)
            print("serial time: {}".format(stime))
            step = 0
            for i, fmt in zip(range(len(self._numbytedict)), self._typedata):
                s = SIZES[i]
                step += s
                dataItem = unpack_from(fmt, buffer[step - s:step]) # unpack_from ini menghasilkan dua tuple
                lstSerialData.append(dataItem[0])

            print("value from Arduino : {}".format(lstSerialData))
            self._parser.add([stime, lstSerialData])
            self._display.add(lstSerialData)
        except SerialException as e:
            pass

    def add(self, valtoard: list):
        print("val to Arduino: {}".format(valtoard))
        send_buf = bytes()
        for val in valtoard:
            send_buf += pack('f', float(val))
        self._out_queue.put(send_buf)
        sleep(1.15)

    def stop(self):
        self._exit.set()
        print("serial process stop")



class DisplayProcess(Process):
    def __init__(self, label, template):
        Process.__init__(self)
        self._in_queue = Queue()
        self._label = label
        self._template = template
        self._exit = multiprocessing.Event()

    def add(self, disp_data):
        self._in_queue.put(disp_data)

    def run(self):
        print("display run")
        while not self._exit.is_set():
            pass


    def update(self):
        while not self._in_queue.empty():
            disp_data = self._in_queue.get()
            if len(disp_data) == 3:
                disp_data.append(0.0)
            for i, template in zip(range(len(self._label)), self._template):
                self._label[i].setText(template.format(disp_data[i]))


    def stop(self):
        self._exit.set()
        if not self._in_queue.empty():
            self._in_queue.get()
        print("display process stop")
