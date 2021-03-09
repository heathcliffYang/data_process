# modify according to which directory the image in
#   for example:
#     images/
#     labels/ (source)
#
#     new_dir/
#       class_1/
#             images/image_01.jpg
#             labels/ (destination)
#       class_2/
#             images/image_03.jpg
#             labels/ (destination)
#       class_3/
#             images/image_02.jpg
#             labels/ (destination)
#                                class_dir_name   class_idx
# We need to modify label by dict : {class_1:         0,
#                                    class_2:         1,
#                                    class_3:         2}
# label files are all in /labels/
                                         # cannot see the whole face
                                         # but we know it didn't wear a mask
from file_utils.basic import *
from label_utils.tools import *
from label_utils.label_io import WriteYoloLabel

import cv2

class_dir_idx = {'full': 0, 'masked': 1, 'part': 2}

img_dir =  '/home/ginny/Projects/dataset/masked_face_dataset/MAFA_TEST/new_dir/'
img_file_list = TraverseDir(img_dir, '.jpg')

for img_path in img_file_list:
    # Get source label
    class_dir = img_path.split('/')[-3]
    src_label_path = PathHandler(img_path.replace('new_dir/'+class_dir+'/', ''), 'find_txt')

    dst_label_path = PathHandler(img_path, 'create_txt')
    bbox_list = ReadYoloLabel(src_label_path, 'xywh')
    for bbox in bbox_list:
        # Rewrite label according to the class directory the image is at
        bbox['label'] = class_dir_idx[class_dir]
    WriteYoloLabel(dst_label_path, bbox_list)
    print('img_path: %s, dest label path: %s'%(img_path, dst_label_path))
