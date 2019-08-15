"""
Reference:
https://github.com/APMonitor/arduino/blob/master/4_PID_Control/Python/test_PID.py

"""
import time

class PID:
    def __init__(self, Sp = 0.0, Kc = 0.0, Ki = 0.0, Kd = 0.0):

        self._set_point = Sp
        self._Kc = Kc
        self._Ki = Ki
        self._Kd = Kd
        self._curr_time = time.time()
        self._prev_time = self._curr_time

        #clearing data from the last stop
        self._p_error = 0.0
        self._i_error = 0.0
        self._pv_last = 0.0
        self._output = 0.0


    def update(self, process_value):
        self._error = self._set_point - process_value
        self._curr_time = time.time()
        self._dt = self._curr_time - self._prev_time


        # upper and lower bounds on heater level
        self._ophi = 100
        self._oplo = 0

        # ubias for controller (initial heater)
        self._output0 = 0.0

        # calculate the integral error
        self._i_error = self._i_error + self._Ki * self._error * self._dt

        # calculate the measurement derivative
        self.der_on_pv = (process_value - self._pv_last) / self._dt

        # calculate the PID output
        self._output = self._output0+self._Kc * self._error + \
                      self._i_error - self._Kd * self.der_on_pv

        # implement anti-reset windup
        if self._output < self._oplo or self._output > self._ophi:
            self._i_error = self._i_error - self._Ki * self._error * self._dt
        # clip output
            self._output = max(self._oplo, min(self._ophi, self._output))

        self._pv_last = process_value
        self._p_error = self._error
        self._prev_time = self._prev_time - self._curr_time


    #beware using this set function,
    #make sure to determine in consecutive manner

    def set_tunning(self, kc, taui, taud):
        self._Kc = kc
        self._Ki = kc/taui
        self._Kd = kc*taud

    def set_setpoint(self, setpoint):
        self._set_point = setpoint

    @property
    def get_setpoint(self):
        return self._set_point

    @property
    def get_parameters(self):
        return [self._Kc, self._Ki, self._Kd, self._p_error]

    @property
    def get_output(self):
        return self._output