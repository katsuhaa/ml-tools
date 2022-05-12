#!/usr/bin/python3
# posiファイルから画像を表示して、位置の確認をします。
import os,sys
import cv2
import annotationwindow 
import detectobjects

default_posifilename = 'posi.info'

def initposiitems():
    filelists = []
    for path, subdirs, files in os.walk("target-image"):
        for filename in files:
            img_path = os.path.join(path, filename)
            filelists.append(str(img_path))
    filelists.sort()
    return [ [ filename, [] ] for filename in filelists ]

def readposifile(fname):
    with open(fname) as posif:
        posiitems = initposiitems()
        for line in posif:
            linesplit = line.split()
            for idx in range(len(posiitems)):
                if posiitems[idx][0] == linesplit[0]:
                    for i in range(0, int(linesplit[1])*4, 4):
                        posiitems[idx][1].append( [int(linesplit[i2+2]) for i2 in range(i, i+4)] )
                    break
    return posiitems

def saveposifile(fname, posiitem):
    with open(fname, mode='w') as posif:
        for pitem in posiitem:
            outs = '{} {} '.format(pitem[0], len(pitem[1]))
            for rc in pitem[1]:
                rcs = '{} {} {} {} '.format(rc[0], rc[1], rc[2], rc[3])
                outs += rcs
            posif.write(outs + '\n')

def initposifile(fname):
    posiitems = initposiitems()
    saveposifile(fname, posiitems)


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

def posiinfosum(posiitems):
    #総数
    resultsum = {}
    objsum = 0
    for pitem in posiitems:
        objsum += len(pitem[1])
    resultsum['posifilenum'] = len(posiitems)
    resultsum['posinum'] = objsum
    
    # min max
    wmin = 999999
    wmax = 0
    hmin = 999999
    hmax = 0
    for item in posiitems:
        for rect in item[1]:
            wmin = min(wmin, rect[2])
            wmax = max(wmax, rect[2])
            hmin = min(hmin, rect[3])
            hmax = max(hmax, rect[3])
    resultsum['widthmin'] = wmin
    resultsum['widthmax'] = wmax
    resultsum['heightmin'] = hmin
    resultsum['heightmax'] = hmax

    return resultsum

def mainloop(posifilename):

    if os.path.exists(posifilename) is False:
        initposifile(posifilename)
        
    posiitems = readposifile(posifilename)
    i = 0
    while True:
        ret, posiitems[i] = annotationwindow.makeanno(posiitems[i], i)
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
        elif ret == ord('r'):
            #認識実行
            posiitems[i][1] = detectobjects.get_cascaded_data(posiitems[i][0])
            
    safe_saveposifile(posifilename, posiitems)
    cv2.destroyAllWindows()
    return posiinfosum(posiitems)


if __name__ == "__main__":
    global defalut_posifilename

    posifilename = default_posifilename
    if len(sys.argv) > 1:
        posifilename = sys.argv[1]
        
    print( "posi filename {}".format(posifilename))
    ret = mainloop(posifilename)
    print(ret)

                
                

    

