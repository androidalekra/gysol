
"""
MicroPython TinyRTC I2C Module DS3231 RTC
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""

from micropython import const

DATETIME_REG = const(0) # 0x00-0x06
CHIP_HALT    = const(128)
CONTROL_REG  = const(7) # 0x07
RAM_REG      = const(8) # 0x08-0x3F

class DS3231(object):
    """Driver for the DS3231 RTC."""
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.weekday_start = 1

    def _dec2bcd(self, value):
        """Convert decimal to binary coded decimal (BCD) format"""
        return (value // 10) << 4 | (value % 10)

    def _bcd2dec(self, value):
        """Convert binary coded decimal (BCD) format to decimal"""
        return ((value >> 4) * 10) + (value & 0x0F)

    #(year, month, mday, hour, minute, second, weekday, yearday)
    def datetime(self, datetime=None):
        """Get or set datetime"""
        if datetime is None:
            buf = self.i2c.readfrom_mem(self.addr, DATETIME_REG, 7)
            return (
                self._bcd2dec(buf[6]) + 2000, # year
                self._bcd2dec(buf[5]), # month
                self._bcd2dec(buf[4]), # day
                self._bcd2dec(buf[2]), # hour
                self._bcd2dec(buf[1]), # minute
                self._bcd2dec(buf[0]), # second
                self._bcd2dec(buf[3] - self.weekday_start),# weekday
                0
            )
        buf = bytearray(7)
        buf[0] = self._dec2bcd(datetime[5])
        buf[1] = self._dec2bcd(datetime[4]) # minute
        buf[2] = self._dec2bcd(datetime[3]) # hour
        buf[3] = self._dec2bcd(datetime[6] + self.weekday_start) # weekday
        buf[4] = self._dec2bcd(datetime[2]) # day
        buf[5] = self._dec2bcd(datetime[1]) # month
        buf[6] = self._dec2bcd(datetime[0] - 2000) # year
        self.i2c.writeto_mem(self.addr, DATETIME_REG, buf)
  
