#!/usr/bin/python3

import os,sys,subprocess
import makenegadat
import checkobjects

def runsh(cmd):
    print(cmd)
    return subprocess.run(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def makecascade():
    
    print("checkobject.pyで作成したposi.info target_image negativeを使ってcascade.xmlを作成します。")
    ret = runsh("cp posi.info positive.dat")
    print("positive情報を作成 ret{}".format(ret))
    posiitems = checkobjects.readposifile("positive.dat")
    posinum = 0
    for pitem in posiitems:
        posinum += len(pitem[1])
    print("positiveデータの作成　ポジティブデータ数 {}".format(posinum))
    neganum = makenegadat.makenegadat()
    print("negative情報を作成 ネガティブデータ数 {}".format(neganum))

    # ./opencv_createsamples -info holes_positive.dat -vec vec/positive.vec -num 正解画像の枚数) 
    print("ベクターファイル作成")
    ret = runsh("opencv_createsamples -info {} -vec vec/positive.vec -num {}".format("positive.dat", posinum))
    print("ret {}".format(ret))

    if os.path.isdir("classifier") is True:
        print("古いデータファイルをバックアップ")
        if os.path.isdir("classifier.bak") is True:
            runsh("rm -rf classifier.bak");
        runsh("mv classifier classifier.bak")
    os.makedirs("classifier", exist_ok=True)
    # ./opencv_traincascade -data classifier -vec vec/positive.vec -bg holes_negative.dat -numPos 正解画像の枚数 -numNeg 不正解画像の枚数
    print("トレーニング実行")
    ret = runsh("opencv_traincascade -data classifier -vec vec/positive.vec -bg negative.dat -numPos {} -numNeg {}".format(int(posinum*0.9), neganum))
    print(" ret {}".format(ret)) 
          
if __name__ == "__main__":
    makecascade()

