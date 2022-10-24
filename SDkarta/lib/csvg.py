"""
MicroPython csv2svg Module
The MIT License (MIT)
Copyright © 2022 ALEKRA https://github.com/androidalekra/gysol
"""
rx=1200
ry=800
rx1=48
ry2=ry-rx1
popy=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]
pozic=0
yl=12
popx=[x for x in range(0,yl*2,2)]

def vytvor(gsx,gsy):
    pozice=1-pozic
    if(pozice<0):pozice=0
    xl=len(popy)
    stream='<svg viewBox="0 0 {} {}" class="chart">\r'.format(rx,ry)
    #rx1=40
    #ry2=ry-rx1
    stream+='<rect x="{}" y="0" width="{}" height="{}"'.format(rx1,rx-rx1,ry2)
    stream+=' style="fill:blue;stroke:black;stroke-width:2;fill-opacity:0.1;stroke-opacity:0.1" />\r'
    roztec=ry2/xl
    for rsy in range(xl-1):
        sy=int(roztec*(rsy+1))
        stream+='<line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:rgb(100,100,50);stroke-width:1" />'.format(rx1,sy,rx,sy)
        stream+='<text font-size="20" x="0" y="{}" fill="black" >{:.{p}f}</text>'.format(sy,popy[xl-1-rsy],p=pozice)
    stream+='<text font-size="20" x="0" y="{}" fill="black" >{:.{p}f}</text>\r'.format(ry2,popy[0],p=pozice)
    roztec=(rx-rx1)/yl
    stream+='<text font-size="20" x="{}" y="{}" fill="black"  >{}</text>'.format(rx1,ry2+25,popx[0])
    for rsx in range(yl-1):
        sx=int(roztec*(rsx+1))+rx1
        stream+='<line x1="{}" y1="0" x2="{}" y2="{}" style="stroke:rgb(100,50,100);stroke-width:1" />'.format(sx,sx,ry2)
        stream+='<text font-size="20" x="{}" y="{}" fill="black"  >{}</text>\r'.format(sx-5,ry2+25,popx[rsx+1])
    stream+='<polyline fill="none" stroke="red" stroke-width="2" points=" ' #"#0074d9"

    for cyk,sx in enumerate(gsx):
        stream+='{},{}\r'.format(rx1+sx,gsy[cyk])

    stream+='"/>\r</svg>'
    return stream

def tofile(nazev,stream):
    with open(nazev,'w') as filesvg:
        filesvg.write(stream)

def readata(soubor,sloupec=3):
    with open(soubor) as fdata:
        #ramdata=fdata.read()
        ramdata=fdata.readlines()
        px=[]
        py=[]
        for rd in ramdata[1:]:
            a=rd.split()
            b=a[0].split(';')
            px.append(int(b[0]))
            py.append(float(b[sloupec]))
    return px,py

def priprava(px,py):
    import time
    cas0=list(time.localtime(px[0]))
    cas0[3]=0
    cas0[4]=0
    x0=time.mktime(tuple(cas0))
    maxx=3600*24
    maxy=(popy[-1]-popy[-2])+popy[-1]#max(py)
    miny=popy[0]#min(py)
    rozy=maxy-miny
    grx=rx-rx1
    rozlisenix=maxx/grx
    sx=[]
    for cyk in px:
        sx.append(int((cyk-x0)//rozlisenix))
    rozliseniy=rozy/ry2    
    sy=[]
    for cyk in py:
        sy.append(ry2-int((cyk-miny)//rozliseniy))
    return sx,sy

def autocal(hmin,hmax):
    global popy,pozic
    import math
    rozdil=hmax-hmin
    pozic=round(math.log10(rozdil))
    rad=math.pow(10,pozic)
    posun=10/rad
    krok=round((rozdil/6)*posun)/posun
    rozsah=rozdil//krok+3
    #print(rozsah)
    zaklad=round((krok+hmin)*posun)/posun-(2*krok)
    popy=[]
    for x in range(int(rozsah)):
        popy.append(zaklad+krok*x)
    #print(krok,zaklad,popy)

def svgenlist(data,sloupec):
    px=[]
    py=[]
    for rd in data[1:]:
        a=rd.split()
        b=a[0].split(';')
        px.append(int(b[0]))
        py.append(float(b[sloupec]))
    autocal(min(py),max(py))
    gsx,gsy=priprava(px,py)
    return vytvor(gsx,gsy)

def svgenfile(csfile,sloupec):
    dsx,dsy=readata(csfile,sloupec)
    #print(min(dsy),max(dsy))
    autocal(min(dsy),max(dsy))
    gsx,gsy=priprava(dsx,dsy)
    return vytvor(gsx,gsy)

#tofile('obr.svg',svgenfile('/SDlog/datalog/2022/10/08.csv',3))
#tofile('obr156.svg',svgenfile('15.csv',9))
