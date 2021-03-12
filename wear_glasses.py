"""
Paste glasses on all faces in a given image

images/
glasses/

"""
from file_utils.basic import TraverseDir
from ctypes import CDLL, POINTER, c_int, byref, c_char_p
import xml.etree.ElementTree as ET
import cv2

def fd_get_bboxes(file_path):
    """
    fd send a list of bboxes in list int format

    <x, y, w, h> <x, y, w, h> ... <-1>
        face 1      face 2         end
    """
    dll = CDLL('/home/ginny/Projects/FR_feature_check_draw_ROI/face_bbox.so')
    get_bbox = dll.get_bbox
    get_bbox.restype = POINTER(c_int)
    get_bbox.argtypes = [c_char_p]
    c_file_path = file_path.encode('utf-8')

    bboxes = get_bbox(c_file_path)
    """
    Usage example
    """
    bboxes_list = []
    bbox = []
    for i in bboxes:
        if len(bbox) == 4:
            bboxes_list.append(bbox.copy())
            bbox = []
        if i == -1:
            break
        bbox.append(i)
    for box in bboxes_list:
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        box[2] = x + w - 1
        box[3] = y + h - 1
    # print(bboxes_list)
    return bboxes_list

def fd_get_features(file_path):
    """
    fd send a list of bboxes in list int format

    <x, y, w, h> <x, y, w, h> ... <-1>
        face 1      face 2         end
    """
    dll = CDLL('/home/ginny/Projects/FR_feature_check_draw_ROI/face_bbox.so')
    get_features = dll.get_features
    get_features.restype = POINTER(c_int)
    get_features.argtypes = [c_char_p]
    c_file_path = file_path.encode('utf-8')

    features = get_features(c_file_path)
    """
    Usage example
    """
    features_list = []
    feature = []
    for i in features:
        if len(feature) == 4:
            features_list.append(feature.copy())
            feature = []
        if i == -1:
            break
        feature.append(i)
    return features_list

if __name__ == "__main__":
    src_dir = "/home/ginny/Projects/dataset/FD_source/MAFA_TEST/simple"
    dst_dir = "/home/ginny/Projects/dataset/FD_source/MAFA_TEST/glasses"

    img_file_list = TraverseDir(src_dir, '.jpg')
    for img_path in img_file_list:
        print(img_path)
        img = cv2.imread(img_path)
        bbox_list = fd_get_bboxes(img_path)
        features_list = fd_get_features(img_path)
        """
        Wear glasses!
        """
        for box, feature in zip(bbox_list, features_list):
            print(box, feature)
