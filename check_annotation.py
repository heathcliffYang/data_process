"""
This file is used to test if label files and images are correct or not
"""
from file_utils.basic import *
from label_utils.tools import *

import cv2


img_dir = '/home/ginny/Projects/dataset/masked_face_dataset/MAFA_TEST/images/'
img_file_list = TraverseDir(img_dir, '.jpg', check_exist=True, skip='test')

for img_path in img_file_list:
    label_path = PathHandler(img_path, 'find')
    img = cv2.imread(img_path)
    PlotLabelFile(img, label_path)
    result_path = PathHandler(label_path, 'plot')
    cv2.imwrite(result_path, img)
