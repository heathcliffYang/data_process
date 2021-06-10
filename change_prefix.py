"""
used to merge dataset, change identity folder prefix
"""
from data_process.file_utils.basic import *
from data_process.label_utils.label_io import WriteLandmarkFile, ReadLandmarkFile, WriteLandmarkFile
from data_process.data_augmentation.landmarks import *
import argparse
import face_alignment
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sourceImgDir", type=str)
    args = parser.parse_args()

    src_img_dir = args.sourceImgDir

    for fn in os.listdir(src_img_dir):
        if not os.path.isdir(os.path.join(src_img_dir, fn)):
            continue
        os.rename(os.path.join(src_img_dir, fn),
            os.path.join(src_img_dir, 'white_' + fn))
