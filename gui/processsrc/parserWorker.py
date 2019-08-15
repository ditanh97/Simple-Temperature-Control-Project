"""
modified from :
https://github.com/ssepulveda/RTGraph/blob/master/rtgraph/processors/Parser.py
"""


from multiprocessing import Process, Queue
import multiprocessing

csv_delimiter = ","
parser_timeout_ms = 0.5

class ParserProcess(Process):
    def __init__(self, temp_queue, graph_reference, store_reference=None,
                 split=csv_delimiter, consumer_timeout=parser_timeout_ms):
        Process.__init__(self)
        self._exit = multiprocessing.Event()
        self._int_queue  = Queue()
        self._out_queue = temp_queue
        self._graph_reference = graph_reference
        self._store_reference = store_reference
        self._split = split
        self._consumer_timeout = consumer_timeout


    def add(self, data):
        self._int_queue.put(data)


    def run(self):
        while not self._exit.is_set():
            self._consume_queue()
            # sleep(self._consumer_timeout)
        self._consume_queue()


    def _consume_queue(self):
        while not self._int_queue.empty():
            queue = self._int_queue.get()
            # queue = self._int_queue.get(timeout=self._consumer_timeout)
            print("data rcv by queue : {}".format(queue[1]))
            self._parse_data(queue[0], queue[1])


    def _parse_data(self, time, data):
        if len(data)>0:
            try:
                self._out_queue.put(data[0])
                self._graph_reference.add(time, data[0:2])
                if self._store_reference is not None:
                    self._store_reference.add(time, data)
            except AttributeError:
                print("Attribute error on type ({}). Raw: {}".format(type(data), data.strip()))


    def stop(self):
        self._exit.set()
        print("parser process stop")

