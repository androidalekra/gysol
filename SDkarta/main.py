
"""
*** ALEKRA *** micropython pro ESP32S2
"""
debug=True
zamek=True
net=False
#debug=False
if(debug):print('START SD main.py')
import esp32s2hw

if(debug):print('zapnuti wifi AP')
import wifi,time,konfig
if(konfig.ap is None):
    try:
        wifi.zapniAP()
    except:
        if(debug):print('AP se nepovedlo zapnout')
        esp32s2hw.LEDR.value(1)
    if(debug):print('zapnuti DNS')
    from microDNSSrv import MicroDNSSrv
    MicroDNSSrv.Create( {"*.*" : "192.168.4.1" , "*" : "192.168.4.1"} )
else:
    if(wifi.pripoj()):
        net=True
    else:
        esp32s2hw.LEDR.value(1)
        

if(debug):print('inicializace periferiji')
import sht40,ms5637,ina219,ds3231,time,sys
"""
I2C adresy
64 (0x40) INA219 napeti,proud,vykon - solar
65 (0x41) INA219 napeti,proud,vykon - baterie
68 (0x44) SHT40 teplota,vlhkost
87 (0x57) AT24C32 EEPROM
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

def nazamek(hodnota):
    global zamek
    if(hodnota):
        esp32s2hw.LEDR.value(1)
        zamek=False
    else:
        esp32s2hw.LEDR.value(0)
        zamek=True

def cettime():
    import ntptime
    try:
        ntptime.settime()
    except:
        print("NTP selhalo")
        return None
    if(debug):print("NTP seřízeno")
    year = time.localtime()[0]  # get current year
    HHMarch = time.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0)
    )  # Time of March change to CEST
    HHOctober = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0)
    )  # Time of October change to CET
    now = time.time()
    if now < HHMarch:  # we are before last sunday of march
        cet = time.localtime(now + 3600)  # CET:  UTC+1H
    elif now < HHOctober:  # we are before last sunday of october
        cet = time.localtime(now + 7200)  # CEST: UTC+2H
    else:  # we are after last sunday of october
        cet = time.localtime(now + 3600)  # CET:  UTC+1H
    return cet

def casrtc(pripojeno):
    from machine import RTC
    rtc=RTC()
    if(pripojeno):
        tm=cettime()
        if(not tm is None):
            ds.datetime(tm)
            if(debug): print("DS RTC seřízen")
    tm=ds.datetime()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    if(debug):print('serizeni hodin ESP {}'.format(time.localtime()[:6]))

casrtc(net)

import uasyncio as asyncio
loop = asyncio.get_event_loop()

async def syncrtc():
    await asyncio.sleep(3)
    while(True):
        casrtc(False)
        await asyncio.sleep(1200)

loop.create_task(syncrtc())

async def dog():
    await asyncio.sleep(5)
    from machine import WDT
    wdt=WDT(timeout=60000)
    if(debug):print('start WDT')
    while(True):
        wdt.feed()
        await asyncio.sleep(20)

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
        if(zamek):
            esp32s2hw.LEDZ.value(1)
            try:
                sht.shtcmd(sht.CMD_MEASURE_HP)
            except:
                if(debug):print('chyba cmd sht40') 
            esp32s2hw.LEDZ.value(0)
        await asyncio.sleep(1)
        if(zamek):
            esp32s2hw.LEDZ.value(1)
            try:
                teplotaSHT,vlhkost=sht.shtTH()
            except:
                if(debug):print('chyba čtení sht40')
        await asyncio.sleep_ms(10)
        if(zamek):
            try:
                tlak,teplotaMS=ms.measure()
            except:
                if(debug):print('chyba MS') 
        await asyncio.sleep_ms(10)
        if(zamek):
            try:
                Usol=inasol.get_voltage()
                Isol=inasol.get_current()
                Psol=inasol.get_power()
            except:
                if(debug):print('chyba INA solar')
        await asyncio.sleep_ms(10)
        if(zamek):
            try:
                Ubat=inabat.get_voltage()
                Ibat=inabat.get_current()
                Pbat=inabat.get_power()
            except:
                if(debug):print('chyba INA baterie')
            cas=time.localtime()
            if(debug):print('{} {:02d}.{:02d}. {}:{:02d}:{:02d}'.format(cas[0],cas[2],cas[1],cas[3],cas[4],cas[5]))
            if(debug):print(' SHT t = {:.2f}°C   {:.1f}%'.format(teplotaSHT,vlhkost))
            if(debug):print(' MS t = {:.2f}°C   {:.2f}hPa'.format(teplotaMS,tlak))
            if(debug):print(' solar U = {:.3f}V  I = {:.3f}A  P = {:.3f}W'.format(Usol,Isol,Psol))
            if(debug):print(' bat   U = {:.3f}V  I = {:.3f}A  P = {:.3f}W'.format(Ubat,Ibat,Pbat))
        esp32s2hw.LEDZ.value(0)
        await asyncio.sleep(9-time.localtime()[5]%10)

loop.create_task(senzory())

def pathcreate(path='/'):
    if( not pathexist(path)):
        #print('cesta neexistuje')
        filepathdir=path.split('/')
        mkpath=''
        for num in range(len(filepathdir)-1):
            mkpath+=filepathdir[num]
            if( not pathexist(mkpath)):
                #print('  mkdir '+mkpath)
                uos.mkdir(mkpath)
            mkpath+='/'
        return False
    else:
        return True

def pathexist(path='/'):
    try:
        ret=uos.stat(path)
        return True
    except OSError:
        return False

async def zapisovac():
    nadpis='UTC;cas;teplota;vlhkost;tlak;Usol;Isol;Psol;Ubat;Ibat;Pbat;\n'
    await asyncio.sleep(17)
    while(True):
        cas=time.localtime()[:6]
        soubor='/SDCard/datalog/{}/{:02}/{:02}.csv'.format(cas[0],cas[1],cas[2])
        veta='{};{:02}:{:02};'.format(time.time(),cas[3],cas[4])
        veta+='{:.2f};{:.1f};{:.2f};'.format(teplotaSHT,vlhkost,tlak)
        veta+='{:.3f};{:.3f};{:.3f};'.format(Usol,Isol,Psol)
        veta+='{:.3f};{:.3f};{:.3f};\n'.format(Ubat,Ibat,Pbat)
        if(debug):print(veta)
        if(not pathcreate(soubor)):
            with open(soubor,'w') as file:
                file.write(nadpis)
                file.write(veta)
        else:
            with open(soubor,'a') as file:
                file.write(veta)
        await asyncio.sleep(300-((cas[4]%5)*60+cas[5]))

loop.create_task(zapisovac())

def csvread(soubor):
    if(pathexist(soubor)):
        try:
            data=[]
            with open(soubor,'r') as file:
                for x in file:
                    data.append(x.strip())
        except:
            data=None
        return data
    else:
        return None

nadpis='UTC;cas;teplota;vlhkost;tlak;Usol;Isol;Psol;Ubat;Ibat;Pbat;\n'

if(debug):print('inicializace WWW')
from MicroWebSrv2  import *

zaklad= """
    <!DOCTYPE html>
    <html lang=cz>
        <head>
            <meta charset="UTF-8" />
            <title>SOLAR METEO</title>
            <link rel="stylesheet" href="/style.css" />
        </head>
        <body style="padding: 0 70px;">
            <h1>SOLAR METEO STANICE </h1>
            <h2>záznamy senzorů</h2>
            <button onclick="history.back()">krok zpět</button>

    """
konec="""
        </body>
    </html>
    """


@WebRoute(GET, '/')
def RequestHandler(microWebSrv2, request) :
    cas=time.localtime()
    casstr='{} {:02d}.{:02d}. {}:{:02d}:{:02d}'.format(cas[0],cas[2],cas[1],cas[3],cas[4],cas[5])
    #            <meta http-equiv="refresh" content="30">
    content = """
    <!DOCTYPE html>
    <html lang=cz>
        <head>
            <meta charset="UTF-8" />
            <title>SOLAR METEO</title>
            <link rel="stylesheet" href="/style.css" />
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
                <li><a href="/data/rok">Historie</a></li>
            </ul>
        </body>
    </html>
    """.format(teplotaSHT,vlhkost,tlak,Usol,Isol,Psol,Ubat,Ibat,Pbat,casstr)
    request.Response.ReturnOk(content)    

bazecesty='/SDCard/datalog'

@WebRoute(GET, '/data/rok')
def RequestDatarok(microWebSrv2, request):
    content = zaklad
    content+='<h3>Rok</h3>'
    for adresar in uos.ilistdir(bazecesty):
        if(adresar[1]==16384):
            content+='<a href="/data/mesic/{}">{}</a>\n'.format(adresar[0],adresar[0])
    content+=konec
    request.Response.ReturnOk(content)    

@WebRoute(GET, '/data/mesic/<cesta>')
def RequestDatamesic(microWebSrv2, request, args):
    content = zaklad
    content+='<h3>Měsíc {}</h3>'.format(args['cesta'])
    cesta=bazecesty+'/{}'.format(args['cesta'])
    if(pathexist(cesta)):
        for adresar in uos.ilistdir(cesta):
            if(adresar[1]==16384):
                content+='<a href="/data/den/{}/{}">{}</a>\n'.format(args['cesta'],adresar[0],adresar[0])
    else:
        content+='<h3>nespravné datum, nebo neexistují záznamy</h3>'
    content+=konec
    request.Response.ReturnOk(content)    

@WebRoute(GET, '/data/den/<cesta>')
def RequestDataden(microWebSrv2, request, args):
    content = """
    <!DOCTYPE html>
    <html lang=cz>
        <head>
            <meta charset="UTF-8" />
            <title>SOLAR METEO</title>
            <link rel="stylesheet" href="/style.css" />
        </head>
        <style> table, th, td {border:2px solid black;} </style>
        <body style="padding: 0 70px;">
            <h1>SOLAR METEO STANICE </h1>
            <button onclick="history.back()">krok zpět</button>
            <table>
              <tr>
                <th>tabulka</th>
                <th>graf</th>
                <th>soubor</th>
              </tr>
    """
    cesta=bazecesty+'/'+args['cesta'] #str(args['cesta'])
    if(pathexist(cesta)):
        #print(cesta)
        for adresar in uos.ilistdir(cesta):
            jmeno=adresar[0].split('.')
            #print(jmeno)
            if(jmeno[1]=='csv'):
                content+='<tr>\n'
                content+='<td><a href="/data/tabulka/{}/{}">{}</a></td>\n'.format(args['cesta'],adresar[0],jmeno[0])
                content+='<td><a href="/data/senzor/{}/{}">{}</a></td>\n'.format(args['cesta'],adresar[0],jmeno[0])
                content+='<td><a href="/data/soubor/{}/{}">{}</a></td>\n'.format(args['cesta'],adresar[0],jmeno[0])
                content+='</tr>\n'
    content+='</table>\n'
    content+='<p>{}</p>'.format(args['cesta'])
    content+=konec
    request.Response.ReturnOk(content)    

@WebRoute(GET, '/data/tabulka/<cesta>')
def RequestDataTabulka(microWebSrv2, request, args):
    nazamek(True)
    content = """
    <!DOCTYPE html>
    <html lang=cz>
        <head>
            <meta charset="UTF-8" />
            <title>SOLAR METEO</title>
            <link rel="stylesheet" href="/style.css" />
        </head>
        <style> table, th, td {border:2px solid black;} </style>
        <body style="padding: 0 70px;">
            <h1>SOLAR METEO STANICE </h1>
            <button onclick="history.back()">krok zpět</button>
            <table>
    """
    cesta=bazecesty+'/'+args['cesta']
    if(pathexist(cesta)):
        datacsv=csvread(cesta)
        if(not datacsv is None):
            prvky=datacsv[0].split(';')
            content+='<tr>\n'
            for segment in prvky[1:-1]:
                content+='<th>{}</th>\n'.format(segment)
            content+='</tr>\n'
            for radek in datacsv[1:]:
                prvky=radek.split(';')
                content+='<tr>\n'
                for segment in prvky[1:-1]:
                    content+='<td>{}</td>\n'.format(segment)
                content+='</tr>\n'
    content+='</table>\n'
    content+='<p>{}</p>'.format(args['cesta'])
    content+=konec
    nazamek(False)
    request.Response.ReturnOk(content)    

@WebRoute(GET, '/data/senzor/<cesta>')
def RequestDatasenzor(microWebSrv2, request, args):
    listnadpis=nadpis.split(';')[2:-1]
    content = zaklad
    content+='<h3>grafy {}</h3>'.format(args['cesta'])
    cesta=bazecesty+'/{}'.format(args['cesta'])
    if(pathexist(cesta)):
        for senzor in listnadpis:
            content+='<a href="/data/graf/{}/{}">{}</a>\n'.format(args['cesta'],senzor,senzor)
    else:
        content+='<h3>nespravné datum, nebo neexistují záznamy</h3>'
    content+=konec
    request.Response.ReturnOk(content)    

import csvg
@WebRoute(GET, '/data/graf/<cesta>')
def RequestDatagraf(microWebSrv2, request, args):
    nazamek(True)
    #listnadpis=nadpis.split(';')[2:-1]
    content = zaklad
    content+='<h3>graf {}</h3>'.format(args['cesta'])
    senzor=args['cesta'].split('/')[-1]
    cestabez=args['cesta'].replace('/'+senzor,'')
    cesta=bazecesty+'/{}'.format(cestabez)
    if(pathexist(cesta)):
        datacsv=csvread(cesta)
        print('datacsv')
        if(not datacsv is None):
            print('senzory')
            senzory=datacsv[0].split(';')[2:]
            senzoryl=[x.lower() for x in senzory]
            if(senzor in senzoryl):
                senindex=senzoryl.index(senzor)+2
                #content+='<h3> graf {} index {} soubor {}</h3>'.format(senzor,senindex,cesta)
                #content+=csvg.svgenfile(cesta,senindex)
                content+=csvg.svgenlist(datacsv,senindex)
            else:
                content+='<h3>senzor neexistuje</h3>'
        else:
            content+='<h3>žádné záznamy</h3>'
    else:
        content+='<h3>nespravné datum, nebo neexistují záznamy</h3>'
    content+=konec
    nazamek(False)
    request.Response.ReturnOk(content)    

@WebRoute(GET, '/data/soubor/<cesta>')
def RequestDataSoubor(microWebSrv2, request, args):
    request.Response.ReturnFile(bazecesty+'/'+args['cesta'])

mws2 = MicroWebSrv2()
mws2.BindAddress = ('0.0.0.0', 80)
mws2.SetEmbeddedConfig()
mws2.RootPath = '/SDCard/www'
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
