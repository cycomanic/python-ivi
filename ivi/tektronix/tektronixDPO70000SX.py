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

HorizontalModeMapping = {
    "auto" : "auto",
    "constant" : "constant",
    "manual" : "manual"
    }

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


    def _get_horizontal_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":horizontal:mode?").lower()
            self._horizontal_mode = [k for k,v in HorizontalModeMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._acquisition_type

    def _set_horizontal_mode(self, value):
        if value not in HorizontalModeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":horizontal:mode %s" % AcquisitionTypeMapping[value])
        self._horizontal_mode = vlaue
        self._set_cache_valid()
        


