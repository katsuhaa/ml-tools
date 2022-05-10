#!/usr/bin/python3
# posiファイルから画像を表示して、位置の確認をします。
import os
import cv2
import annotationwindow as aw
import copy

def initposifile(fname):
    with open(fname, mode='w') as posif:
        for path, subdirs, files in os.walk("target-image"):
            for filename in files:
                img_path = os.path.join(path, filename)
                posif.write(str(img_path) + " 0 " +  os.linesep)

def readposifile(fname):
    posiitems = None
    with open(fname) as posif:
        posiitems = []
        for line in posif:
            item = []
            linesplit = line.split()
            if os.path.exists(linesplit[0]) is False:
                continue
            item.append(linesplit[0])
            item.append([])
            for i in range(0, int(linesplit[1])*4, 4):
                item[1].append( [int(linesplit[i2+2]) for i2 in range(i, i+4)] )
            posiitems.append(item)
    return posiitems;

def saveposifile(fname, posiitem):
    with open(fname, mode='w') as posif:
        for pitem in posiitem:
            outs = '{} {} '.format(pitem[0], len(pitem[1]))
            for rc in pitem[1]:
                rcs = '{} {} {} {} '.format(rc[0], rc[1], rc[2], rc[3])
                outs += rcs
            posif.write(outs + '\n')

def safe_saveposifile(fname, posiitem):
    bnamefmt = "{}.bak{}"
    
    for i in range(9,0,-1):
        bname = bnamefmt.format(fname,i)
        if os.path.isfile(bname):
            os.rename(bname, bnamefmt.format(fname,i+1))

    if os.path.isfile(bnamefmt.format(fname,"")):
        os.rename(bnamefmt.format(fname,""), bnamefmt.format(fname,1))
        
    os.rename(fname, bnamefmt.format(fname,""))
    saveposifile(fname, posiitem)

def drawhole(img, rect, color, thickness=1, lineType=cv2.LINE_8, shift=0):
    radius = int(rect[3]/2)
    center = (rect[0]+radius, rect[1]+radius)
    cv2.circle(img, center, radius, color, thickness, lineType, shift)

def mainloop():

    posifilename = 'posi.info'

    if os.path.exists(posifilename) is False:
        initposifile(posifilename)
        
    posiitems = readposifile(posifilename)
    i = 0
    while True:
        ret, posiitems[i] = aw.makeanno(posiitems[i], i)
        if ret == ord('q') or ret == ord('e'):
            #保存して終了
            break
        elif ret == ord('n'):
            #次
            if i < len(posiitems)-1:
                i = i + 1
        elif ret == ord('p'):
            #前
            if i > 0:
                i = i - 1
        elif ret == ord('s'):
            #保存
            safe_saveposifile(posifilename, posiitems)
        elif ret == ord('!'):
            #強制終了
            cv2.destroyAllWindows()
            return
    safe_saveposifile(posifilename, posiitems)
    objsum = 0
    for pitem in posiitems:
        objsum += len(pitem[1])
    print(objsum)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    mainloop()
    

                
                

    

