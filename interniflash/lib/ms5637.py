
"""
MicroPython MS5637 I2C Module
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""

class MS5637:
    
    CMD_ConvertD1_8192 = 0x4A
    CMD_ConvertD2_8192 = 0x5A

    def __init__(self, _i2c,_adr=118):
        self.i2c = _i2c
        self.adr = _adr
        self.coef = [0]*7
        self.readcoef()
        
    def cmd(self,cmd):
        buf = bytearray(1)
        buf[0] = cmd
        return self.i2c.writeto(self.adr,buf)

    def promread(self,padr=0):
        _padr = 0xA0 + padr * 2
        buf = self.i2c.readfrom_mem(self.adr,_padr,2)
        return (buf[0] << 8) + buf[1]

    def readcoef(self):
        for x in range(7):
            self.coef[x]=self.promread(x)

    def readAD(self):
        buf = self.i2c.readfrom_mem(self.adr,0,3)
        return buf[0] * 65536 + buf[1] * 256 + buf[2]
    
    def conversion(self,D1,D2):
        dT = D2 - self.coef[5] * 256
        TEMP = 2000 + dT * self.coef[6] / 8388608
        OFF = self.coef[2] * 131072 + (self.coef[4] * dT) / 64
        SENS = self.coef[1] * 65536 + (self.coef[3] * dT ) / 128
        T2 = 0
        OFF2 = 0
        SENS2 = 0
        if TEMP > 2000 :
            T2 = 5 * dT * dT / 274877906944
            OFF2 = 0
            SENS2 = 0
        elif TEMP < 2000 :
            T2 = 3 * (dT * dT) / 8589934592
            OFF2 = 61 * ((TEMP - 2000) * (TEMP - 2000)) / 16
            SENS2 = 29 * ((TEMP - 2000) * (TEMP - 2000)) / 16
            if TEMP < -1500:
                OFF2 = OFF2 + 17 * ((TEMP + 1500) * (TEMP + 1500))
                SENS2 = SENS2 + 9 * ((TEMP + 1500) * (TEMP +1500))
        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
        cTemp = TEMP / 100.0
        return pressure,cTemp
    
    def measure(self):
        import time
        self.cmd(self.CMD_ConvertD1_8192)
        time.sleep_ms(20)
        D1=self.readAD()
        self.cmd(self.CMD_ConvertD2_8192)
        time.sleep_ms(20)
        D2=self.readAD()
        return self.conversion(D1,D2)
