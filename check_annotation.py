"""
This file is used to test if label files and images are correct or not

Usage:
    python3 check_annotation.py <test_img_dir>

We assume that images and labels are pair and organize in this format:
    <path to target dir>/images/ or /JPEGImages/
    <path to target dir>/labels/ or /labelsJSON/

The label plotted images will be stored in <path to target dir>/results/
"""
from file_utils.basic import *
from label_utils.tools import *
import argparse
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("targetImgDir", type=str)
    args = parser.parse_args()


    img_dir = args.targetImgDir
    img_file_list = TraverseDir(img_dir, '.jpg', check_exist='txt', skip='test')

    for img_path in img_file_list:
        print(img_path)
        label_path = PathHandler(img_path, 'find_txt')
        img = cv2.imread(img_path)
        PlotLabelFile(img, label_path)
        result_path = PathHandler(label_path, 'plot')
        # print(result_path)
        cv2.imwrite(result_path, img)
