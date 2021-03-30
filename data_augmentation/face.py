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

class FaceDA(object):

    def __init__(self):
        # Set face alignment model
        self.fa = fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)
        # Set glasses styles
        self.working_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
                           # decide alpha threshold for copying glasses area
        self.glasses_collect = {'circle_glasses.png': 50,\
                           'black_glasses.png': 100}

    def wearGlasses(self, image, labels=None):
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
        if labels is None:
            labels = [[0, 0, 0, image.shape[1]-1, image.shape[0]-1]]

        # For each face, get landmarks and compute appropriate glasses of random styles
        for label in labels:
            # crop the face
            box = label[1:].copy()
            box_w = box[2] - box[0]
            box_h = box[3] - box[1]
            img_crop = image[box[1]:box[1]+box_h, box[0]:box[0]+box_w, :]
            # get landmarks of the face
            preds = self.fa.get_landmarks(img_crop)
            if preds is None:
                print("No landmarks can be found!")
                continue
            Landmarks_set = Landmarks(preds)

            # Vectors collected
            h_vector = Landmarks_set[18, 27]
            # Check landmarks quality
            if h_vector.x < 1:
                continue
            eyebrow_eye_vector = Landmarks_set[19, 38]# TEMP:
            v_vector = eyebrow_eye_vector.perpendicular(h_vector)
            eyebrow_nose_vector = Landmarks_set[19, 30]
            l_vector = eyebrow_nose_vector.perpendicular(h_vector)
            # Check landmarks quality
            if l_vector.length() < 1 or h_vector.length() < 1:
                continue

            # 1. glasses height
            glasses_height_ratio = random.uniform(0, 0.12)
            glasses_height = l_vector.length()
            glasses_height *= 1. + glasses_height_ratio
            # 2. glasses length
            glasses_length = h_vector.length()
            glasses_length_ratio = random.uniform(0, 0.4)
            glasses_length *= 1. + glasses_length_ratio

            # Get glasses
            glasses_name = random.choice(list(self.glasses_collect.keys()))
            glasses_img = cv2.imread(self.working_dir+"/../glasses_images/"+glasses_name, cv2.IMREAD_UNCHANGED)
            glasses_color = [random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)]
            # Before rotate
            for i in range(glasses_img.shape[0]):
                for j in range(glasses_img.shape[1]):
                    if glasses_img[i][j][3] == 0:
                        for k in range(3):
                            glasses_img[i][j][k] = 255
                    else:
                        for k in range(3):
                            glasses_img[i][j][k] = glasses_color[k]
            # Resize glasses image and blur
            glasses_img = cv2.resize(glasses_img, (int(glasses_length), int(glasses_height)))
            glasses_img = cv2.GaussianBlur(glasses_img, (3,3), 0)

            # Compute warp matrix, code ref: https://github.com/ultralytics/yolov5
            ## Center
            C = np.eye(3)
            C[0, 2] = - int(glasses_length) / 2  # x translation (pixels)
            C[1, 2] = - int(glasses_height) / 2  # y translation (pixels)
            ## Rotation
            rotate = math.atan(h_vector.y / h_vector.x)
            rotate = rotate / math.pi * 180 * (-1)
            rotate_matrix = cv2.getRotationMatrix2D((0, 0), rotate, scale = 1)
            R = np.eye(3)
            R[:2] = rotate_matrix
            ## New width and height: (from (glasses_length, glasses_height) to (glasses_img_w, glasses_img_h))
            pre_M_1 = rotate_matrix @ np.array([[int(glasses_length)],[int(glasses_height)],[1]])
            pre_M_2 = rotate_matrix @ np.array([[0],[0],[1]])
            glasses_img_w = int(abs(pre_M_1[0,0] - pre_M_2[0,0]))
            glasses_img_h = int(abs(pre_M_1[1,0] - pre_M_2[1,0]))
            pre_M_1 = rotate_matrix @ np.array([[0],[int(glasses_height)],[1]])
            pre_M_2 = rotate_matrix @ np.array([[int(glasses_length)],[0],[1]])
            glasses_img_w = max( abs(int(pre_M_1[0,0] - pre_M_2[0,0])), glasses_img_w)
            glasses_img_h = max( abs(int(pre_M_1[1,0] - pre_M_2[1,0])), glasses_img_h)
            ## Translation
            T = np.eye(3)
            T[0, 2] = 0.5 * glasses_img_w  # x translation (pixels)
            T[1, 2] = 0.5 * glasses_img_h  # y translation (pixels)
            ## Apply this matrix
            glasses_img = cv2.warpAffine(glasses_img, (T @ R @ C)[:2], (glasses_img_w, glasses_img_h))

            # Find top-left coordinates in input image we can paste glasses
            ## Glasses mid point
            glass_midpt = T @ R @ C @ np.array([[int(glasses_length/2)],[0],[1]])
            s = float(glass_midpt[1] / v_vector.y)
            glass_left_shift = glass_midpt[0] - s * v_vector.x
            ## Nose mid point
            nose_mid = Landmarks_set[28] # np.array(preds[0][28 - 1])
            glasses_position_ratio = random.uniform(0.8, 0.95)
            nose_mid = nose_mid - (glasses_position_ratio / 2 * l_vector +  s * v_vector)
            ## Glasses paste point
            top_left = [nose_mid.x - glass_left_shift, nose_mid.y]

            # Paste glasses
            for i in range(min(int(box[1] + top_left[1]), int(image.shape[0]-1)), min(int(box[1] + top_left[1])+glasses_img_h, int(image.shape[0]-1))):
                for j in range(min(int(box[0] + top_left[0]), int(image.shape[1]-1)), min(int(box[0] + top_left[0])+glasses_img_w, int(image.shape[1]-1))):
                    if glasses_img[i-int(box[1] + top_left[1])][j - int(box[0] + top_left[0])][3] > self.glasses_collect[glasses_name]:
                        for k in range(3):
                            image[i,j,k] = glasses_img[i-int(box[1] + top_left[1])][j - int(box[0] + top_left[0])][k]
        return image


    def CutLowerPartFace(self, img):
        """
        Args:
            img: aligned face image

        randomly
        """
        if img.shape[0] != 112:
            img = cv2.resize(img, (112,112))

        color = random.uniform(0, 255)
        # Cut out the lower part of a given face
        mid = 112/2
        covered_h = int(random.uniform(mid, mid+20))
        for i in range(covered_h, img.shape[0]):
            for j in range(img.shape[1]):
                for k in range(3):
                    img[i,j,k] = color # OR randomly pick color at this place ?!

        return img



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
