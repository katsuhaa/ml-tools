#!/usr/bin/python3
# holes/validのディレクトリからcreatesample用のposiファイルを作成します。

import os
import cv2


#基盤イメージファイルディレクトリ
imgpath = "holeimg"
#検出した穴画像ディレクトリ
holespath = "holes/valid"   

#holespath = "holestest/valid"
files = os.listdir(holespath)
files_file = [f for f in files if os.path.isfile(os.path.join(holespath, f))]

posilist = []
for posiname in files_file:

    pngidx = posiname.find('.png_')+4
    posn = posiname[10:pngidx]
    posstr = posiname[pngidx:]
    posl = [
        int(posstr[posstr.find('_x')+2:posstr.find('-y')]),
        int(posstr[posstr.find('-y')+2:posstr.find('-w')]),
        int(posstr[posstr.find('-w')+2:posstr.find('-h')]),
        int(posstr[posstr.find('-h')+2:posstr.rfind('.png')])
        ]

    pio = None
    for pi in posilist:
        if pi[0] == posn:
            pio = pi
    if pio:
        pio[1].append(posl)
    else:
        posilist.append([posn,[posl]])

for pitem in posilist:
    outs = '{} {} '.format(os.path.join(imgpath, pitem[0]), len(pitem[1]))
    for rc in pitem[1]:
        rcs = '{} {} {} {} '.format(rc[0], rc[1], rc[2], rc[3])
        outs += rcs
    print(outs)
    
    #012345678901234567890123456789012345678901234567890123456789
    #hole03649-20220307120015_00_00_insp.png_x1281-y768-w29-h29.png
#print(files_file)   # ['file1', 'file2.txt', 'file3.jpg']
