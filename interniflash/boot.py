# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import esp32s2hw,uos
if(esp32s2hw.sdkarta()==1):
    uos.chdir('/SDCard')