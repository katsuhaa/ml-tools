#!/usr/bin/python3
# 機械学習の結果からオブジェクトを検出します。
import os,sys
import cv2
import checkobjects


#show cascaded image
def get_cascaded_data(img_path):
    # カスケードの読み込み
    cascade = cv2.CascadeClassifier('classifier/cascade.xml')
    
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        print("img is empty", img_path)
        return []
    grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    objs = cascade.detectMultiScale(grayed, minNeighbors = 3, minSize=(80,80)) #コンデンサ minSize=(70,70) スルーホール minSize=(8,8) maxSize=(30,30)
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

def default_detect():
    items = get_cascaded_dirimage("target-image")
    checkobjects.saveposifile("detectposi.info", items)

if __name__ == "__main__":
    default_detect()
    print("save detectposi.info")


