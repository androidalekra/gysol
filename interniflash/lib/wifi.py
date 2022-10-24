
"""
MicroPython WIFI module
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""

def pripoj():
    import konfig
    import network
    import time

    station = network.WLAN(network.STA_IF)
    if station.active() == False:
        station.active(True)
    if station.isconnected() == True:
        print("uz pripojeno - status %s" % station.status())
        return 1
    print("nepripojeno")
    station.config(dhcp_hostname=konfig.mdns)
    try:
        station.connect(konfig.ap[0], konfig.ap[1])
    except:
        station.active(False)
        return 0
    while not station.isconnected():
        time.sleep(0.05)
    ip = station.ifconfig()
    print(ip)
    return 1


def zapniAP():
    import network
    import konfig

    apecko = network.WLAN(network.AP_IF)
    apecko.config(essid=konfig.mdns, dhcp_hostname=konfig.mdns, max_clients=5)
    # apecko.config(essid=konfig.mdns,authmode=3, password='heslo',dhcp_hostname=konfig.mdns,max_clients=5)
    apecko.active(True)
    # ip 192.168.4.1
