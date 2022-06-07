#!/usr/bin/python3
# 機械学習の結果からオブジェクトを検出します。
import os,sys
import cv2
import checkobjects as cobjs


# 指定ファイル名が含まれているインデックスを返す
# 無い場合はNone
def search_targetindex(posiobj, targetname):
    for i in range(len(posiobj)):
        if posiobj[i][0] == targetname:
            return i
    return None

def compobj(pobj, dobj):
    sx = max(pobj[0], dobj[0])
    sy = max(pobj[1], dobj[1])
    ex = min(pobj[0]+pobj[2], dobj[0]+dobj[2])
    ey = min(pobj[1]+pobj[3], dobj[1]+dobj[3])
    interarea = (ex-sx)*(ey-sy)/(pobj[2]*pobj[3])
    sizediff = (dobj[2]*dobj[3])/(pobj[2]*pobj[3])

    ret = None
    if interarea > 0.7 and abs(sizediff - 1.0) < 0.3:
        ret = interarea
    return ret, interarea, sizediff

def compitem(posi, detect):
    cantdetect = 0    # 検出できていない
    toomuch = 0 # 余分に検出
    for name, objs in posi:
        idx = search_targetindex(detect, name)
        if idx is not None:
            dobjs = detect[idx][1].copy()
            cant = len(objs)
            for obj in objs:
                for didx in range(len(dobjs)):
                    ret,_,_ = compobj(obj, dobjs[didx])
                    if ret is not None:
                        del dobjs[didx]
                        cant = cant - 1
                        break
            # print( name, len(objs), cant, len(detect[idx][1]), len(dobjs))
            cantdetect = cantdetect + cant
            toomuch = toomuch + len(dobjs)
    return cantdetect, toomuch

def compobject(posiname = 'posi.info', detectname = 'detectposi.info'):
    posiobj = cobjs.readposifile(posiname)
    detectobj = cobjs.readposifile(detectname)

    return compitem(posiobj, detectobj)
    
    
if __name__ == "__main__":
    cantdetect, toomuch = compobject()
    print("検出不可", cantdetect, "誤検出", toomuch)

