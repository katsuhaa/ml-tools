#!/usr/bin/python3
# posiファイルから画像を表示して、位置の確認をします。

import cv2
import annotationwindow as aw
import copy

def readposifile(fname):
    posiitems = None
    with open(fname) as posif:
        posiitems = []
        for line in posif:
            item = []
            linesplit = line.split()
            item.append(linesplit[0])
            item.append([])
            for i in range(0, int(linesplit[1]), 4):
                item[1].append( [int(linesplit[i2+2]) for i2 in range(i, i+4)] )
            posiitems.append(item)
    return posiitems;

def drawhole(img, rect, color, thickness=1, lineType=cv2.LINE_8, shift=0):
    radius = int(rect[3]/2)
    center = (rect[0]+radius, rect[1]+radius)
    cv2.circle(img, center, radius, color, thickness, lineType, shift)

def mainloop():
    
    posiname = 'posi.info'

    posiitems = readposifile('posi.info')

    for posiitem in posiitems:
        posiitem = makeanno(posiitem)

    

