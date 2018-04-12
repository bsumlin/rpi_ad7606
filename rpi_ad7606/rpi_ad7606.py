import pigpio as pio
from time import sleep

class AD7606(chans):
    def __init__(self,communicationMode,inputRange,conversionABmode,pins):
        # pins should be a dict mapping pin names to RPi numbers. If using SPI, only need to specify CE channel. Unwrap pins to individual self.whatevers
        # inputRange should be 5 or 10, nothing else. Default it to 5.
        # ABmode should be 'simultaneous' or 'grouped'
        # communicationMode should be 'SPI', 'parallel', or 'parallelByte'. Default to SPI.
        self.communicationMode = communicationMode
        self.inputRange = inputRange
        self.xferFactor = inputRange/(2**15) # hardcoded for now, but in the future range could change dynamically
        self.ABmode = ABmode
        self.p_standby = pins['standby']
        self.p_convsta = pins['convsta']
        self.p_dataA = pins['DoutA']
        if conversionABmode == 'simultaneous': # all on one line
            self.p_convstb = None
            self.p_dataB = None
        else conversionABmode == 'grouped': # all on A and B lines - update later to separate conversion and reading
            self.p_convstb = pins['convstb']
            self.p_dataB = pins['DoutB']
        self.p_reset = pins['reset']
        self.p_busy = pins['busy']
        self.p_1stData = pins['1stData']

        self.io = pio.pi() # initialize pigpio
        # initialize pins as appropriate
        for _p in [self.p_standby, self.p_convsta, self.p_convstb, self.p_reset]:
            if _p is not None:
                self.io.set_mode(_p,OUTPUT)
        for _p in [self.p_dataA,self.p_dataB,self.p_busy,self.p_1stData]:
            if _p is not None:
                self.io.set_mode(_p,INPUT)
        for _p in [self.p_convsta,self.p_convstb]:
            if _p is not None:
                self.io.set_pull_up_down(_p,io.PUD_UP)
        for _p in [self.p_reset,self.p_busy]:
            if _p is not None:
                self.io.set_pull_up_down(_p,io.PUD_DOWN)
        self.adc = io.spi_open(0,1000000,0) # initialize spi on channel 0 at 1mhz. self.adc is now the "handle"

    def transferFunction(self,reading):
        def _twosComp(_val):
            if (_val & (1 << 15)) != 0:
                _val = _val - (1 << 16)
            return _val
        return self.xferFactor*_twosComp(int(reading,2)) # returns the voltage of the sensor

    def ADCreset(self):
        self.io.write(self.p_reset,1)
        self.io.write(self.p_reset,0)

    #def standby(self):
        # do this later, mine's never in standby

    def ADCread(self):
        self.io.write(self.p_convsta,0)
        self.io.write(self.p_convsta,1)
        while self.io.read(self.p_busy) == 1:
            pass
        _c, _d = self.io.spi_read(self.adc,12) # two bytes per each of the 6 channels. _c is number of bytes read back and _d is a bytearray of said bytes.
        if _c == 12:
            _channel1 = transferFunction(_d[0] << 8 | _d[1])
            _channel2 = transferFunction(_d[2] << 8 | _d[3])
            _channel3 = transferFunction(_d[4] << 8 | _d[5])
            _channel4 = transferFunction(_d[6] << 8 | _d[7])
            _channel5 = transferFunction(_d[8] << 8 | _d[9])
            _channel6 = transferFunction(_d[10] << 8 | _d[11])

    return [_channel1,_channel2,_channel3,_channel4,_channel5,_channel6]
