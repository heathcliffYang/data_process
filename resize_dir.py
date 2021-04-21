from data_process.file_utils.basic import *
from data_process.label_utils.tools import *
from data_process.label_utils.label_io import WriteYoloLabel
from data_process.data_augmentation.background import random_crop_rectangle
import argparse
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sourceImgDir", type=str)
    args = parser.parse_args()

    src_img_dir = args.sourceImgDir
    src_img_file_list = TraverseDir(src_img_dir, ['.jpg', '.JPG', '.jpeg'])

    for img_path in src_img_file_list:
        print(img_path)
        img = cv2.imread(img_path)
        img = cv2.resize(img, (192,96))
        cv2.imwrite(img_path, img)
