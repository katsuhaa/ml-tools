#!/usr/bin/python3
# 機械学習の結果からオブジェクトを検出します。
import os,sys
import cv2
import checkobjects

# カスケードの読み込み
cascade = cv2.CascadeClassifier('classifier/cascade.xml')

#show cascaded image
def get_cascaded_data(img_path):
    global cascade
    
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    objs = cascade.detectMultiScale(grayed, minNeighbors = 5, minSize = (70,70) )
    print("image {} detect {}".format(img_path, objs))
    if len(objs) > 0:
        objs = objs.tolist()
    else:
        objs = []
    return objs

def get_cascaded_dirimage(dir_path):
    items = []
    for path, subdirs, files in os.walk(dir_path):
        for filename in files:
            img_path = os.path.join(path, filename)
            if img_path.endswith(('jpg','png')) is True:
                objs = get_cascaded_data(img_path)
                items.append([img_path, objs])
                print("Image file {} object num {}".format(img_path, len(objs)))
    return items

if __name__ == "__main__":
    items = get_cascaded_dirimage("target-image")
    checkobjects.saveposifile("detectposi.info", items)
    print("save detectposi.info")


