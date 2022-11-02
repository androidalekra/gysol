
"""
*** ALEKRA *** micropython pro ESP32S2
"""
debug=True
if(debug):print('START interni main.py')
import esp32s2hw

if(debug):print('zapnuti wifi AP')
import wifi
wifi.zapniAP()

if(debug):print('zapnuti DNS')
from microDNSSrv import MicroDNSSrv
MicroDNSSrv.Create( {"*.*" : "192.168.4.1" , "*" : "192.168.4.1"} )

if(debug):print('inicializace periferiji')
import sht40,ms5637,ina219,ds3231,time
"""
I2C adresy
64 (0x) INA219 napeti,proud,vykon - solar
65 (0x) INA219 napeti,proud,vykon - baterie
68 (0x44) SHT40 teplota,vlhkost
87 (0x) AT24C32 EEPROM
104 (0x68) DS3231 RTC
118 (0x76) MS5637 teplota,tlak
"""
try:
    sht=sht40.SHT4x(esp32s2hw.IIC)
    ms=ms5637.MS5637(esp32s2hw.IIC)
    ds=ds3231.DS3231(esp32s2hw.IIC)
    inasol=ina219.INA219(esp32s2hw.IIC,Rsh=0.1,addr=64)
    inabat=ina219.INA219(esp32s2hw.IIC,Rsh=0.1,addr=65)
except:
    esp32s2hw.LEDR.value(1)
    esp32s2hw.PER.value(0)
    from machine import deepsleep
    import time
    time.sleep(10)
    esp32s2hw.LEDZ.value(0)
    time.sleep(10)
    esp32s2hw.LEDR.value(0)
    deepsleep(900000)

teplotaSHT=0
vlhkost=0
teplotaMS=0
tlak=0
Usol=0
Isol=0
Psol=0
Ubat=0
Ibat=0
Pbat=0

def casrtc():
    from machine import RTC
    rtc=RTC()
    tm=ds.datetime()
    #rtc.init(list(ds.datetime()[:6])+[0,1])
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    if(debug):print('serizeni hodin ESP {}'.format(time.localtime()[:6]))

casrtc()

import uasyncio as asyncio
loop = asyncio.get_event_loop()

async def syncrtc():
    await asyncio.sleep(1200)
    while(True):
        casrtc()
        await asyncio.sleep(1200)

loop.create_task(syncrtc())

async def dog():
    await asyncio.sleep(5)
    from machine import WDT
    wdt=WDT(timeout=30000)
    if(debug):print('start WDT')
    while(True):
        wdt.feed()
        await asyncio.sleep(10)

if(esp32s2hw.TL21.value()):loop.create_task(dog())

async def sporic():
    await asyncio.sleep(30)
    from machine import deepsleep
    if(debug):print('start sporic baterie')
    while(True):
        if(Ubat<3.5):
            if(debug):print('baterie je temer vybita. uspavam')
            esp32s2hw.PER.value(0)
            esp32s2hw.LEDR.value(1)
            await asyncio.sleep(1)
            esp32s2hw.LEDZ.value(0)
            esp32s2hw.LEDR.value(0)
            deepsleep(900000)
        await asyncio.sleep(300)

loop.create_task(sporic())


async def senzory():
    global teplotaSHT,vlhkost,teplotaMS,tlak,Usol,Isol,Psol,Ubat,Ibat,Pbat
    await asyncio.sleep(5)
    while(True):
        sht.shtcmd(sht.CMD_MEASURE_HP)
        await asyncio.sleep(1)
        esp32s2hw.LEDZ.value(1)
        esp32s2hw.LEDR.value(1)
        teplotaSHT,vlhkost=sht.shtTH()
        tlak,teplotaMS=ms.measure()
        Usol=inasol.get_voltage()
        Isol=inasol.get_current()
        Psol=inasol.get_power()
        Ubat=inabat.get_voltage()
        Ibat=inabat.get_current()
        Pbat=inabat.get_power()
        cas=ds.datetime()
        if(debug):print('{} {:02d}.{:02d}. {}:{:02d}:{:02d}'.format(cas[0],cas[2],cas[1],cas[3],cas[4],cas[5]))
        if(debug):print(' MS t = {:.2f}°C   {:.2f}hPa'.format(teplotaMS,tlak))
        if(debug):print(' SHT t = {:.2f}°C   {:.1f}%'.format(teplotaSHT,vlhkost))
        if(debug):print(' solar U = {:.3f}V  I = {:.3f}A  P = {:.3f}W'.format(Usol,Isol,Psol))
        if(debug):print(' bat   U = {:.3f}V  I = {:.3f}A  P = {:.3f}W'.format(Ubat,Ibat,Pbat))
        esp32s2hw.LEDZ.value(0)
        esp32s2hw.LEDR.value(0)
        await asyncio.sleep(9)

loop.create_task(senzory())

if(debug):print('inicializace WWW')
from MicroWebSrv2  import *

@WebRoute(GET, '/')
def RequestHandler3(microWebSrv2, request) :
    cas=ds.datetime()
    casstr='{} {:02d}.{:02d}. {}:{:02d}:{:02d}'.format(cas[0],cas[2],cas[1],cas[3],cas[4],cas[5])
    content = """
    <!DOCTYPE html>
    <html lang=cz>
        <head>
            <meta charset="UTF-8" />
            <title>SOLAR METEO</title>
            <link rel="stylesheet" href="style.css" />
            <meta http-equiv="refresh" content="30">
        </head>
        <body style="padding: 0 70px;">
            <h1>SOLAR METEO STANICE </h1>
            <h2>Hodnoty senzorů</h2>
            <h3>Teplota  {:.2f}°C</h3>
            <h3>Vlhkost  {:.1f}%</h3>
            <h3>Tlak {:.2f}hPa</h3>
            <h3>Solární panel - U={:.3f}V I={:.3f}A P={:.3f}W</h3>
            <h3>Baterie - U={:.3f}V I={:.3f}A P={:.3f}W</h3>
            <h3>interní čas {}</h3>
            <ul>
                <li><a href="webrepl.html">WEBREPL - webová kozole micropythonu</a></li>
            </ul>
        </body>
    </html>
    """.format(teplotaSHT,vlhkost,tlak,Usol,Isol,Psol,Ubat,Ibat,Pbat,casstr)
    request.Response.ReturnOk(content)    

mws2 = MicroWebSrv2()
mws2.BindAddress = ('0.0.0.0', 80)
mws2.SetEmbeddedConfig()
mws2.RootPath = '/www'
mws2.NotFoundURL = '/'
mws2.StartManaged()

def systemstart():
    if(debug):print("start loop")
    loop.run_forever()
    if(debug):print("stop loop")


if(debug):print('startuji vlakno')
import _thread,time
_thread.stack_size(1024*10)
time.sleep(1)
_thread.start_new_thread(systemstart, ())
time.sleep(2)
if(debug):print('vlakno bezi')
#systemstart()
import webrepl
webrepl.start()
