"""
functions for face-related data augmentation
"""
from ctypes import CDLL, POINTER, c_int, byref, c_char_p
import xml.etree.ElementTree as ET
import cv2
import face_alignment
import math
import random
import numpy as np
import os


def fd_get_bboxes(file_path):
    """
    fd send a list of bboxes in list int format

    <x, y, w, h> <x, y, w, h> ... <-1>
        face 1      face 2         end

    and we ture them into xyxy format
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
    return bboxes_list


class landmark_vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __sub__(self, other):
        return landmark_vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return landmark_vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """
        Only for mulitply by a scalar, NOT dot product
        """
        if isinstance(scalar, landmark_vector):
            raise BaseException("This is not dot product")
        else:
            return landmark_vector(scalar*self.x, scalar*self.y)

    def __rmul__(self, scalar):
        """
        Only for mulitply by a scalar, NOT dot product
        """
        if isinstance(scalar, landmark_vector):
            raise BaseException("This is not dot product")
        else:
            print("hi", type(landmark_vector(scalar*self.x, scalar*self.y)))
            return landmark_vector(scalar*self.x, scalar*self.y)

    def __str__(self):
        return "(%.2f, %.2f)"%(self.x, self.y)

    def perpendicular(self, horizontal):
        """
        Returns:
            a projection vector of self vector on the direction perpendicular to the horizontal vector
        """
        scalar = (self.x*horizontal.x + self.y*horizontal.y)/(horizontal.x**2+horizontal.y**2)
        return self - horizontal * scalar

class landmark(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        if isinstance(other, landmark_vector):
            return landmark(self.x - other.x, self.y - other.y)
        else:
            raise BaseException("Illegal operation")

class Landmarks(object):
    def __init__(self, landmarks):
        """
        landmarks from face_alignment"
            [pt index][2]
                       -> [x, y]

            Warning:
                pt index in the landmark figure counts from 1; however, pt index in a list counts from 0
        """
        if landmarks is not None:
            self.landmarks = landmarks[0]
        else:
            raise BaseException("No landmarks are created")

    def __getitem__(self, idx_pair):
        """
        Returns:
            landmark vector from 1st node to 2nd node specified in idx_pair
        """
        if isinstance(idx_pair, int):
            return landmark(self.landmarks[idx_pair-1][0], self.landmarks[idx_pair-1][1])
        else:
            from_idx, to_idx = idx_pair
            return landmark_vector(self.landmarks[to_idx-1][0] - self.landmarks[from_idx-1][0],\
                                   self.landmarks[to_idx-1][1] - self.landmarks[from_idx-1][1])


def wear_glasses(image, labels):
    """
    Randomly make faces wear glasses

    Note that only faces which the face alignment model can find landmarks on are possible to wear glasses
    and faces in an image are randomly picked to apply this work.

    TODO: enable this function can be feed an image instead of image path

    Args:
        image
        labels : [n x 5] , [class, x1, y1, x2, y2] or None
                 None means that this image is a cropped out face already

    Returns:
        image
    """
    # Set glasses styles
    working_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
                       # decide alpha threshold for copying glasses area
    glasses_collect = {'circle_glasses.png': 50,\
                       'black_glasses.png': 120}

    # Set face alignment model
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)

    # For each face, get landmarks and compute appropriate glasses of random styles
    for label in labels:
        # crop the face
        box = label[1:].copy()
        box_w = box[2] - box[0]
        box_h = box[3] - box[1]
        img_crop = image[box[1]:box[1]+box_h, box[0]:box[0]+box_w, :]
        # get landmarks of the face
        landmarks = fa.get_landmarks(img_crop)
        if landmarks is None:
            continue
        # horizontal vector of the face (along with eyebrow direction)
        h_vector = (preds[0][27 - 1][0] - preds[0][18 - 1][0], preds[0][27 - 1][1] - preds[0][18 - 1][1])




    glasses_img = cv2.imread(working_dir+"/../glasses_images/"+"circle_glasses.png", cv2.IMREAD_UNCHANGED)
    return None
