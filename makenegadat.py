#!/usr/bin/python3
import os
import sys
import cv2

# definition
args = sys.argv

negative_dir = 'negative/'
negative_dat = 'negative.dat'

########################################################################################
# main
negafilenum = 0
dat_path = None
dir_path = None

def makenegadat():
    global negafilenum, dat_path, dir_path
    negafilenum = 0
    dat_path = negative_dat
    dir_path = negative_dir

    dat_file = open(dat_path, 'w')
    for path, subdirs, files in os.walk(dir_path):
        for filename in files:
            img_path = os.path.join(path, filename)
            dat_file.write(str(img_path) + os.linesep)
            negafilenum = negafilenum + 1
    return negafilenum

if __name__ == "__main__":
    num = makenegadat()
    print(num)
