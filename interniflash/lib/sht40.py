"""
MicroPython SHT40  I2C Module
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""
class SHT4x:
    
    CMD_MEASURE_HP = 0xFD
    CMD_MEASURE_MP = 0xF6
    CMD_MEASURE_LP = 0xE0
    CMD_SERIALNUM  = 0x89
    CMD_RESET      = 0x94
    CMD_M_H200mW1S = 0x39
    CMD_M_H200mW01S = 0x32
    CMD_M_H110mW1S = 0x2F
    CMD_M_H110mW01S = 0x24
    CMD_M_H20mW1S = 0x1E
    CMD_M_H20mW01S = 0x15

    def __init__(self, _i2c,_shtadr=68):
        self.i2c = _i2c
        self.shtadr = _shtadr

    def shtcmd(self,cmd):
        buf = bytearray(1)
        buf[0] = cmd
        return self.i2c.writeto(self.shtadr,buf)

    def shtread(self):
        return self.i2c.readfrom(self.shtadr,6)

    def toTemperature(self, buf):
        return -45 + 175 * ((buf[0] << 8) + buf[1]) / ( 2**16 -1) 

    def toHumidity(self, buf):
        return -6 + 125.0 * ((buf[3] << 8) + buf[4]) / (2**16 - 1)

    def shtTH(self):
        buf = self.shtread()
        return self.toTemperature(buf), self.toHumidity(buf)
