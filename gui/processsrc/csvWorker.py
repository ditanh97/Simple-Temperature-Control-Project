"""
modified from :
https://github.com/ssepulveda/RTGraph/blob/master/rtgraph/processors/Csv.py
"""

import multiprocessing
from multiprocessing import Process, Queue
from time import sleep, strftime, gmtime
import csv
import os


timeout = 1

SAVE_TITLES_AUTOMATIC = [
        'time(s)',
        'Temperature (in)',
        'isHeaterOn1(in)',
        'isHeaterOn2(in)',
        'Duty cycle(in)'
        'Controller output % (out)',
        'Set point (internal)',
        'Derivative (internal)',
        'Integral (internal)',
        'Proportional (internal)',
        'Last error (internal)',
    ]


SAVE_TITLES_MANUAL = [
        'time(s)',
        'Temperature (in)',
        'Heater 1 %(in)',
        'Heater 2 %(in)'
    ]

app_export_path = "data"
csv_default_filename = "%Y-%m-%d_%H-%M-%S"

class CSVProcess(Process):
    def __init__(self,manmode, path= app_export_path, filename = None):
        Process.__init__(self)
        self._exit = multiprocessing.Event()
        self._out_int_queue = Queue()
        self._in_queue = Queue()
        self._csv = None
        self._file = None

        if filename is None:
            filename = strftime(csv_default_filename, gmtime())
        self._file = self._create_file(filename, path=path)


        self._timeout = timeout
        self._manmode = manmode
        if manmode:
            self._col_names_for_save = SAVE_TITLES_MANUAL
        else:
            self._col_names_for_save = SAVE_TITLES_AUTOMATIC

        self.in_data = []
        self.out_int_data = []

    def add(self, time, data):
        array = [time]
        print("data rcv in csv: {}".format(data))
        array.extend(data)
        self._in_queue.put(array)


    def addinter(self, output, set_point, pid_data):
        array = [output, set_point]
        array.extend(pid_data)
        self._out_int_queue.put(array)


    def run(self):
        self._csv = csv.writer(self._file, delimiter = ",", quoting=csv.QUOTE_MINIMAL)
        self._csv.writerow(self._col_names_for_save)
        while not self._exit.is_set():
            self._consume_queue()
            sleep(self._timeout)
        self._consume_queue()
        self._file.close()


    def _consume_queue(self):
        if not self._in_queue.empty():
            self.in_data = self._in_queue.get()
        else:
            self.in_data = []
        if not self._out_int_queue.empty():
            self.out_int_data = self._out_int_queue.get()
        else:
            self.out_int_data = []
        lst_data =[]
        lst_data.extend(self.in_data)
        print("lst_data in: {}".format(self.in_data))
        lst_data.extend(self.out_int_data)
        self._csv.writerow(lst_data)


    def stop(self):
        self._exit.set()
        print("csv process stop")



    def _create_file(self, filename, path=None, extension="csv"):
        """
        Creates the file to export the data.
        :param filename: Name of the file where data will be exported.
        :type filename: str.
        :param path: Path where data file will be saved.
        :type path: str.
        :param extension: Extension to give to the export file.
        :type extension: str.
        :return: Reference to the export file.
        """
        self._create_dir(path)
        full_path = self._createfile(filename, extension=extension, path=path)
        if not self._file_exists(full_path):
            return open(full_path, "a", newline='')
        return None


    @staticmethod
    def _create_dir(path=None):
        """
        Creates a directory if the specified doesn't exists.
        :param path: Directory name or full path.
        :type path: str.
        :return: True if the specified directory exists.
        :rtype: bool.
        """
        if path is not None:
            if not os.path.isdir(path):
                os.makedirs(path)
        return os.path.isdir(path)

    @staticmethod
    def _createfile(filename, extension="txt", path=None):
        """
        Creates a file full path based on parameters.
        :param filename: Name for the file.
        :type filename: str.
        :param extension: Extension for the file.
        :type extension: str.
        :param path: Path for the file, if needed.
        :type path: str.
        :return: Full path for the specified file.
        :rtype: str.
        """
        if path is None:
            full_path = str("{}.{}".format(filename, extension))
        else:
            full_path = str("{}/{}.{}".format(path, filename, extension))
        return full_path


    @staticmethod
    def _file_exists(filename):
        """
        Checks if a file exists.
        :param filename: Name of the file, including path.
        :type filename: str.
        :return: True if the file exists.
        :rtype: bool.
        """
        if filename is not None:
            return os.path.isfile(filename)