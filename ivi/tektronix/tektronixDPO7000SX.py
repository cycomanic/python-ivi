"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2016 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import numpy as np
from .tektronixBaseScope import *

class tektronixDPO7000SX(tektronixBaseScope):
    "Tektronix DPO7000SX series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'DPO7000')

        super(tektronixDPO7000SX, self).__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 0
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._bandwidth = 70e9

        self._identity_description = "Tektronix DPO7000SX series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DPO72304SX', 'DPO73304SX',
                'DPO75002SX', 'DPO77002SX', 'DPS73308SX', 'DPS75004SX', 'DPS77004SX']

        self._init_channels()

    def _measurement_fetch_waveform(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return list()

        self._write(":wfmoutpre:encdg binary")
        if sys.byteorder == 'little':
            self._write(":wfmoutpre:byt_or lsb")
        else:
            self._write(":wfmoutpre:byt_or msb")
        acq_type = self._ask(":acquire:mode:actual?").lower()
        # if the scope is in sampling acquisition mode we should only use 8 bit
        # resolution (see manual)
        if acq_type == 'sample':
            self._write(":wfmoutpre:byt_nr 1")
        else:
            self._write(":wfmoutpre:byt_nr 2")
        self._write(":wfmoutpre:bn_fmt rp")
        self._write(":wfmoutpre:pt_fmt y")
        self._write(":data:source %s" % self._channel_name[index])
        self._write(":data:start 1")
        self._write(":data:stop 1e10")

        # Read preamble

        pre = self._ask(":wfmoutpre?").split(';')

        format = pre[7].strip()
        points = int(pre[6])
        xincr = float(pre[9])
        xzero = float(pre[10])
        ymult = float(pre[13])
        yoff = float(pre[14])
        yzero = int(float(pre[15]))

        if type == 1:
            raise scope.InvalidAcquisitionTypeException()

        if format != 'Y':
            raise UnexpectedResponseException()

        raw_data = self._ask_for_ieee_block(":curve?")
        self._read_raw() # flush buffer # Split out points and convert to time and voltage pairs
        if acq_type == 'sample':
            y_data_raw = array.array('B', raw_data)
        else:
            y_data_raw = array.array('H', raw_data)

        x_data = np.arange(len(y_data_raw)) * xincr + xzero
        y_data = (y_data_raw - np.asarray(yoff)) * ymult + yzero


        return x_data, y_data, y_data_raw

