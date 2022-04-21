all: makeposiinfo

makeposiinfo:	makeposiinfo.cpp
	g++ `pkg-config --cflags opencv4` -Wall -g $^ -o $@ -ldl `pkg-config --libs opencv4` -pthread


