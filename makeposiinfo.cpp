#include <iostream>
#include <cstdlib>
#include <vector>
#include <fstream>
#include <dirent.h>
#include <limits.h>
#include <sys/stat.h>
#include <opencv2/opencv.hpp>


// 基盤画像からcascade_holeを利用して穴画像を取得、ファイル名で仕分けするプログラム
#define HOLES_CLASSIFIER_FILE "cascade_hole.xml"
/* 穴検出用 */
static cv::CascadeClassifier hole_cascade;

int detect_hole(cv::Mat& img_gray, std::vector<cv::Rect>& holes, cv::Size minsz = cv::Size(8,8), cv::Size maxsz = cv::Size(30,30), double factor = 1.1, int minNeighbors = 3, double scale = 1.0)
{
	if (hole_cascade.empty()) {
		if (!hole_cascade.load(HOLES_CLASSIFIER_FILE)) {
			fprintf(stderr, "Error at loading hole cascade: %s\n", HOLES_CLASSIFIER_FILE);
			return -1;
		}
	}

	if (scale != 1.0) {
		cv::resize(img_gray, img_gray, cv::Size(), scale, scale);
		minsz = cv::Size(minsz.width *= scale, minsz.height *= scale);
		maxsz = cv::Size(maxsz.width *= scale, maxsz.height *= scale);
		printf("scale!! width%d hegit%d\n", minsz.width, minsz.height);
	}
	cv::equalizeHist(img_gray, img_gray);
	hole_cascade.detectMultiScale(img_gray, holes, factor, minNeighbors, 0, minsz, maxsz);
	if (scale != 1.0) {
		for (std::vector<cv::Rect>::iterator it = holes.begin(), e = holes.end(); it != e; it++) {
			it->x = (double)it->x / scale;
			it->y = (double)it->y / scale;
			it->width = (double)it->width / scale;
			it->height = (double)it->height /scale;
		}
	}
	//printf("holes num: %d\n", holes.size());
	return holes.size();
}

int detect_hole_draw(cv::Mat& img, std::vector<cv::Rect>& holes, cv::Size minsz = cv::Size(8,8), cv::Size maxsz = cv::Size(30,30), double factor = 1.1, int minNeighbors = 3, double scale = 1.0)
{
	cv::Mat img_gray;
	cv::cvtColor(img, img_gray, cv::COLOR_RGB2GRAY);

	int hcnt = detect_hole(img_gray, holes, minsz, maxsz, factor, minNeighbors, scale);
	cv::Mat holes_img = img.clone();
	for (std::vector<cv::Rect>::const_iterator it = holes.begin(), e = holes.end(); it != e; it++) {
		cv::rectangle(holes_img, *it, cv::Scalar(0, 0, 255), 4);
		
	}

	cv::String title;
	title = cv::format("holes%d-min(%d,%d)-max(%d,%d)-f%1.3lf-neighbor%d-scale%1.3lf", hcnt, minsz.width, minsz.height, maxsz.width, maxsz.height, factor, minNeighbors, scale);
	cv::resize(holes_img, holes_img, cv::Size(), 0.3, 0.3);
	cv::imshow(title,holes_img);
	return hcnt;
}

#define MKDIR_MODE777 (S_IRUSR|S_IWUSR|S_IXUSR|S_IRGRP|S_IWGRP|S_IXGRP|S_IROTH|S_IXOTH|S_IXOTH)

int check_file_exists(const char* filename)
{
    struct stat buffer;
    return stat(filename,&buffer);
}

int main(int argc, const char* argv[])
{
	cv::String dirpath = "target-image/";
	int imgcnt = 1;
	std::ofstream write_file;
	cv::String posiinfoname;
	int	i;

	DIR *dp = opendir(dirpath.c_str());
	if (dp==NULL) {
		exit(1);
	}

	posiinfoname = "posi.info";
	std::ifstream pif(posiinfoname);
	if (pif) {
		for (i = 0; ;i++) {
			cv::String posibackup = cv::format("posi%d.info", i);
			std::ifstream pifb(posibackup);
			if (!pifb) {
				rename(posiinfoname.c_str(), posibackup.c_str());
				break;
			}
		}
	}
	write_file.open(posiinfoname, std::ios::out);
	for (dirent* entry = readdir(dp); entry != NULL; entry = readdir(dp) ){
		cv::String fname = entry->d_name;
		cv::String scene1_path = dirpath + fname;

		printf("%s\n", scene1_path.c_str());
		int npos = scene1_path.rfind(".png");
		if (npos == (int)cv::String::npos || npos != ((int)scene1_path.size())-4) {
			continue;
		}

		printf("Image %s\n",scene1_path.c_str());
		cv::Mat scene1 = cv::imread(scene1_path, cv::IMREAD_COLOR);
		std::vector<cv::Rect> holes;
		
		//detect_hole_draw(scene1, holes, cv::Size(20,20), cv::Size(255,255), 1.005, 5);
		cv::Mat img_gray;
		cv::cvtColor(scene1, img_gray, cv::COLOR_RGB2GRAY);
		detect_hole(img_gray, holes, cv::Size(20,20), cv::Size(255,255), 1.005, 5);
	
		if (check_file_exists("objects")!=0) {
			mkdir("objects", MKDIR_MODE777);
			mkdir("objects/valid", MKDIR_MODE777);
			mkdir("objects/invalid", MKDIR_MODE777);
		}

		if (holes.size() > 0) {
			write_file << cv::format("%s %ld ", fname.c_str(), holes.size());
			// 検出したイメージを１ファイルづつごとに仕分けして、ポジデータのフォーマットで記録
			for (std::vector<cv::Rect>::const_iterator it = holes.begin(), e = holes.end(); it != e; it++) {
				cv::Mat cliphole = scene1(*it);
				cv::String dirname = cv::format("objects/valid");
				cv::String fullname = cv::format("%s/hole%05d-%s_x%d-y%d-w%d-h%d.png", dirname.c_str(), imgcnt, fname.c_str(), it->x, it->y, it->width, it->height);
				cv::imwrite(fullname, cliphole);
				imgcnt++;

				write_file << cv::format("%d %d %d %d ",it->x, it->y, it->width, it->height);
			}
			write_file << std::endl;
		}
	}
	write_file.close();
}

