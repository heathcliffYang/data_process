"""
This file is used to test if label files and images are correct or not

Usage:
    python3 check_annotation.py <test_img_dir>

We assume that images and labels are pair and organize in this format:
    <path to target dir>/images/ or /JPEGImages/
    <path to target dir>/labels/ or /labelsJSON/

The label plotted images will be stored in <path to target dir>/results/
"""
from data_process.file_utils.basic import *
from data_process.label_utils.tools import *
from data_process.label_utils.label_io import WriteYoloLabel
import argparse
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("targetImgDir", type=str)
    args = parser.parse_args()


    img_dir = args.targetImgDir
    print("Checkout image directory:", img_dir)
    img_file_list = TraverseDir(img_dir, '.jpg', check_exist='txt')

    for img_path in img_file_list:
        print(img_path)
        label_path = PathHandler(img_path, 'find_txt')
        img = cv2.imread(img_path)
        bbox_list = CheckLabelNorm(img, label_path)
        if bbox_list != None:
            # need to modify
            print("Modify bbox:", bbox_list)
            dst_label_path = PathHandler(img_path, 'create_txt')
            WriteYoloLabel(dst_label_path, bbox_list)
        state = PlotLabelFile(img, label_path)
        if state is False:
            print("Fail to plot")
            break
        result_path = PathHandler(label_path, 'plot')
        # print(result_path)
        cv2.imwrite(result_path, img)
