
"""
MicroPython INA219 I2C Module
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""

from machine import Pin, I2C
import ustruct

class INA219():
    def __init__(self,i2c,Rsh=0.1,BRNG=1,PG=3,BADC=3,SADC=3,MODE=7, addr=64):
        self._i2c = i2c
        self._address = addr
        calstr = ((BRNG&0x01)<<13)+((PG&0x03)<<11)+((BADC&0x0F)<<7)+((SADC&0x0F)<<3)+(MODE&0x07)
        self.i2c_write_u16(0, calstr)
        self.LSB=2/32768 #MAX(A)/2^15
        self.i2c_write_u16(5, int(0.04096/(Rsh*self.LSB)) )

    def i2c_write_u16(self,addr=0,word=0):
        self._i2c.writeto_mem(self._address, addr, ustruct.pack('>H',word))

    def i2c_read_u16(self,addr=0):
        return ustruct.unpack('>H',self._i2c.readfrom_mem(self._address, addr,2) )[0]

    def i2c_read_16(self,addr=0):
        return ustruct.unpack('>h',self._i2c.readfrom_mem(self._address, addr,2) )[0]

    def get_voltage(self):
        return (self.i2c_read_u16( 0x02) >> 3) * 0.004

    def get_current(self):
        return self.i2c_read_16( 0x04) * self.LSB

    def get_power(self):
        return self.i2c_read_u16( 0x03) * 0.00125

