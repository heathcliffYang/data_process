"""
Generate randomly cropped images as background images
"""
from data_process.file_utils.basic import *
from data_process.label_utils.tools import *
from data_process.label_utils.label_io import WriteYoloLabel
from data_process.data_augmentation.background import random_crop_rectangle
import argparse
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sourceImgDir", type=str)
    parser.add_argument("targetImgDir", type=str)
    args = parser.parse_args()

    src_img_dir = args.sourceImgDir
    target_img_dir = args.targetImgDir
    print("Source image directory: %s, target: %s"%(src_img_dir, target_img_dir))
    src_img_file_list = TraverseDir(src_img_dir, ['.jpg', '.jpeg'])

    f = open(src_img_dir.replace('/source_image/','')+'/training_list.txt', 'w')

    """
    1. Crop random shape rectangles and reshape it into 96x192
    2. For each image, we can crop 5 rectangles
    """
    idx = 0
    for img_path in src_img_file_list:
        img = cv2.imread(img_path)
        print("src: %s"%(img_path))
        # crop random rectangles
        for i in range(20):
            rectangle_image = random_crop_rectangle(img)
            if rectangle_image is None:
                continue
            h, w, _ = rectangle_image.shape
            print("   i=%d, cropped rect: %d x %d"%(i, h, w))
            rectangle_image = cv2.resize(rectangle_image, (192, 96))
            cv2.imwrite(target_img_dir+"/bg_%d.jpg"%(idx), rectangle_image)
            target_label_path = target_img_dir.replace('/JPEGImages/', '/labels/')+'/bg_%d.txt'%(idx)
            WriteYoloLabel(target_label_path, [])
            f.write(target_img_dir+"/bg_%d.jpg\n"%(idx))
            idx += 1
    f.close()
