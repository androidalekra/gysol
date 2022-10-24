
"""
MicroPython HW konfigurace ESP32S2 TTGO T8
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""
from machine import SPI, Pin, I2C
import time
#tlačítko červené
TL0=Pin(0,Pin.IN,Pin.PULL_UP)

#tlačítko modré
TL21=Pin(21,Pin.IN)

#spínač priférie V3V
PER=Pin(14,Pin.OUT,value=0)

# sbernice I2C
IIC=I2C(1, scl=Pin(5), sda=Pin(4), freq=400000)

LEDZ=Pin(1,Pin.OUT,value=1)
LEDR=Pin(2,Pin.OUT,value=0)

# AD=  #9 BAT/2
# pin 19,20 USB
# pin 15,16 krystal 32kHz

#volne
# 17,18 pro DAC
# 3,6,7,8 

def sdkarta():
    try:
        sdspi = SPI(1, 10000000, sck=Pin(12), mosi=Pin(11), miso=Pin(13))
    except:
        print('SPI pro SD se nepovedlo nastavit')
        return -3
    try:
        import sdcard
        sd = sdcard.SDCard(sdspi, Pin(10),10000000)#CS=Pin(10)
    except:
        print('Nezdařilo se inicializovat SD kartu')
        return -2
    import uos
    try:
        uos.mount(sd, '/SDCard')
    except:
        print('SD karta nemá spravný formát')
        # formatovani SD uos.VfsFat.mkfs(sd)
        return -1
    finally:
        import sys
        sys.path.append('/SDCard/lib')
        print('SD připojeno v /SDCard')
        return 1
    return 0

time.sleep(1)
PER.value(1)
