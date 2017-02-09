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

from .tektronixBaseScope import *
from timeit import default_timer as timer

class tektronixDPO70000SX(tektronixBaseScope):
    "Tektronix DPO70000SX series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'DPO70000')

        super(tektronixDPO70000SX, self).__init__(*args, **kwargs)

        self._analog_channel_count = 4
        self._digital_channel_count = 0
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._bandwidth = 70e9

        self._identity_description = "Tektronix DPO70000SX series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['DPO72304SX', 'DPO73304SX',
                'DPO750002SX', 'DPO77002SX', 'DPS73308SX', 'DPS75004SX', 'DPS77004SX']

        self._init_channels()

    def _measurement_fetch_waveform(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return ivi.TraceYT()

        self._write(":data:source %s" % self._channel_name[index])
        self._write(":data:encdg fastest")
        self._write(":data:width 2")
        self._write(":data:start 1")
        self._write(":data:stop 1e10")

        trace = ivi.TraceYT()

        # Read preamble
        pre = self._ask(":wfmoutpre?").split(';')
        print(pre)

        acq_format = pre[7].strip().upper()
        points = int(pre[6])
        point_size = int(pre[0])
        point_enc = pre[2].strip().upper()
        point_fmt = pre[3].strip().upper()
        byte_order = pre[4].strip().upper()
        trace.x_increment = float(pre[9])
        trace.x_origin = float(pre[10])
        trace.x_reference = int(float(pre[11]))
        trace.y_increment = float(pre[13])
        trace.y_reference = int(float(pre[14]))
        trace.y_origin = float(pre[15])

        if acq_format != 'Y':
            raise UnexpectedResponseException()

        if point_enc != 'BINARY':
            raise UnexpectedResponseException()

        # Read waveform data
        raw_data = self._ask_for_ieee_block(":curve?")
        self._read_raw() # flush buffer


        # Store in trace object
        t1 = timer()
        if point_fmt == 'RP' and point_size == 1:
            trace.y_raw = array.array('B', raw_data[0:points*2])
        elif point_fmt == 'RP' and point_size == 2:
            trace.y_raw = array.array('H', raw_data[0:points*2])
        elif point_fmt == 'RI' and point_size == 1:
            trace.y_raw = array.array('b', raw_data[0:points*2])
        elif point_fmt == 'RI' and point_size == 2:
            trace.y_raw = array.array('h', raw_data[0:points*2])
        elif point_fmt == 'FP' and point_size == 4:
            trace.y_increment = 1
            trace.y_reference = 0
            trace.y_origin = 0
            trace.y_raw = array.array('f', raw_data[0:points*4])
        else:
            raise UnexpectedResponseException()
        print("convert %f"%(timer()-t1))

        if (byte_order == 'LSB') != (sys.byteorder == 'little'):
            trace.y_raw.byteswap()

        return trace

