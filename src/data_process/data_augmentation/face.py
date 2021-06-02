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
import time
from .landmarks import *
from data_process.label_utils.ops import LabelCoordinateTransform
from data_process.label_utils.label_io import ReadLandmarkFile


class FaceDA(object):
    """
    Face-oriented data augmentation techniques class
        1. wearGlasses
        2. CutLowerPartFace
        3. grayPatch: gray-rectangle patch
    """
    def __init__(self, landmark_source='file'):
        """
        landmark_source has 2 types:
            1. 'file'
            2. 'model'
        According to self.landmark_source, we decide to set up self.fa or not
        """
        self.landmark_source = landmark_source
        self.fa = None
        if self.landmark_source == 'model':
            # Set face alignment model
            self.fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)
        # Set glasses styles
        self.working_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
                           # decide alpha threshold for copying glasses area
        self.glasses_collect = {'circle_glasses.png': 50,\
                           'black_glasses.png': 100}

    def getLandmarks(self, image, labels=None, node_num=5):
        """
        Return landmarks

        Args:
            image
            node_num : landmarks = 68 or only 5
            labels : [n x 5] ,

        Returns:
            labels_with_landmarks: [n x (5 + 68*2)]
        """
        if self.fa is None:
            raise Exception("self.fa hasn't been set so we can't get landmarks.")

        if labels is None:
            labels = [[0, 0, 0, image.shape[1]-1, image.shape[0]-1]]

        new_labels = np.zeros((labels.shape[0], 5 + node_num * 2))
        new_labels[:,:5] = labels
        count = -1
        # print("%d faces in this image labeled"%(labels.shape[0]))
        # For each face, get landmarks and compute appropriate glasses of random styles
        for label in labels:
            # crop the face
            count += 1
            box = label[1:].copy()
            box = [int(b) for b in box]
            # print("face box:", box, image.shape)
            box_w = box[2] - box[0]
            box_h = box[3] - box[1]
            img_crop = image[box[1]:box[1]+box_h, box[0]:box[0]+box_w, :]
            try:
                img_crop_scaled = cv2.resize(img_crop, (112,112))
            except:
                print("Fail to crop and resize the face", box)
                continue
            # cv2.imwrite("./img_val_face.jpg", img_crop)
            # get landmarks of the face
            preds = self.fa.get_landmarks(img_crop_scaled)
            if preds is None:
                print("No landmarks can be found!")
                continue
            preds = LabelCoordinateTransform(preds, (112,112), (img_crop.shape[1], img_crop.shape[0]))
            Landmarks_set = Landmarks(preds)

            # Check landmarks quality
            h_vector = Landmarks_set[18, 27]
            if h_vector.x < 1:
                continue
            eyebrow_eye_vector = Landmarks_set[19, 38]# TEMP:
            v_vector = eyebrow_eye_vector.perpendicular(h_vector)
            eyebrow_nose_vector = Landmarks_set[19, 30]
            l_vector = eyebrow_nose_vector.perpendicular(h_vector)
            # Check landmarks quality
            if l_vector.length() < 1 or h_vector.length() < 1:
                continue

            if node_num == 68:
                for i in range(68):
                    one_pt = Landmarks_set[i+1]
                    new_labels[count][5 + i*2] = int(box[0] + one_pt.x)
                    new_labels[count][5 + i*2 + 1] = int(box[1] + one_pt.y)
                # image = cv2.circle(image, (int(box[0] + one_pt.x), int(box[1] + one_pt.y)), 1, (255,0,255), -1)
            else: # node_num = 5
                # left eye
                x = (Landmarks_set[37].x + Landmarks_set[40].x) / 2
                y = (Landmarks_set[37].y + Landmarks_set[40].y) / 2
                new_labels[count][5 + 0] = int(box[0] + x)
                new_labels[count][5 + 1] = int(box[1] + y)
                # right eye
                x = (Landmarks_set[43].x + Landmarks_set[46].x) / 2
                y = (Landmarks_set[43].y + Landmarks_set[46].y) / 2
                new_labels[count][5 + 2] = int(box[0] + x)
                new_labels[count][5 + 3] = int(box[1] + y)
                # nose
                x = Landmarks_set[31].x
                y = Landmarks_set[31].y
                new_labels[count][5 + 4] = int(box[0] + x)
                new_labels[count][5 + 5] = int(box[1] + y)
                # mouth left end
                x = Landmarks_set[49].x
                y = Landmarks_set[49].y
                new_labels[count][5 + 6] = int(box[0] + x)
                new_labels[count][5 + 7] = int(box[1] + y)
                # mouth right end
                x = Landmarks_set[55].x
                y = Landmarks_set[55].y
                new_labels[count][5 + 8] = int(box[0] + x)
                new_labels[count][5 + 9] = int(box[1] + y)
            # cv2.imwrite("./img_val.jpg", image)
        # print(labels[10000000])
        # for l in new_labels:
        #     print("label length:", l.shape)
        return new_labels


    def wearGlasses(self, image, labels=None, landmark_path=None):
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
            if self.landmark_source == 'model':
                # get landmarks of the face
                preds = self.fa.get_landmarks(img_crop)
            elif self.landmark_source == 'file':
                preds = ReadLandmarkFile(landmark_path, img_crop.shape[1], img_crop.shape[0])
            else:
                preds = None

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
            glasses_color = np.array([random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)]).reshape(1,1,3)
            # Before rotate
            glasses_img[:,:,:3] = glasses_color
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
            top_bound = max(0, min(int(box[1] + top_left[1]), int(image.shape[0]-1)))
            bottom_bound = min(int(box[1] + top_left[1])+glasses_img_h, int(image.shape[0]-1))
            left_bound = max(0, min(int(box[0] + top_left[0]), int(image.shape[1]-1)))
            right_bound = min(int(box[0] + top_left[0])+glasses_img_w, int(image.shape[1]-1))
            #print(top_bound, bottom_bound, left_bound, right_bound, glasses_img.shape)
            target_shape = image[top_bound:bottom_bound, left_bound:right_bound,:][glasses_img[:bottom_bound-top_bound,:right_bound-left_bound,3] > self.glasses_collect[glasses_name]].shape
            #print(target_shape)
            #print(glasses_img[glasses_img[:,:,3] > self.glasses_collect[glasses_name]][:,:3].shape)
            image[top_bound:bottom_bound, left_bound:right_bound,:][glasses_img[:bottom_bound-top_bound,:right_bound-left_bound,3] > self.glasses_collect[glasses_name]] = glasses_img[glasses_img[:,:,3] > self.glasses_collect[glasses_name]][:target_shape[0],:3]
        return image

    def CutLowerPartFace(self, img):
        """
        Cut eye and eyebrow area :
            top-left corner : 14, 33
            box : 83 (w), 32 (h)

        Args:
            img: aligned face image

        height: int(112/2)+20
        """
        if img.shape[0] != 112:
            img = cv2.resize(img, (112,112))

        #color = random.uniform(0, 255)
        # Cut out the lower part of a given face
        #mid = int(112/2)
        #covered_h = int(random.uniform(mid, mid+20))
        img = img[33:65, 14:97, :]
        #start = time.time()
        #img[covered_h:img.shape[0], :, :3] = color
        #for i in range(covered_h, img.shape[0]):
        #    for j in range(img.shape[1]):
        #        for k in range(3):
        #            img[i,j,k] = color # OR randomly pick color at this place ?!
        #end = time.time()
        #print("CutLowerPartFace:", end-start)
        #cv2.imwrite('test_face.jpg', img)
        return img

    def grayPatch(self, img):
        """
        img : BGR

        minimal patch size = 10, 10

        RGB to gray according to https://docs.opencv.org/3.4/de/d25/imgproc_color_conversions.html
        """
        left = random.randint(0, 112-1-10)
        top = random.randint(0, int(112/2)-1-10)
        h = random.randint(10, 90)
        w = random.randint(10, 70)
        #start = time.time()
        img[left:min(left+w, img.shape[1]), top:min(top+h, img.shape[0]), :] = \
              np.tile((0.114 * img[left:min(left+w, img.shape[1]), top:min(top+h, img.shape[0]), 0] \
                     + 0.587 * img[left:min(left+w, img.shape[1]), top:min(top+h, img.shape[0]), 1] \
                     + 0.299 * img[left:min(left+w, img.shape[1]), top:min(top+h, img.shape[0]), 2])[:,:,None], (1,1,3))
        #for i in range(left, min(left+w, img.shape[1])):
        #    for j in range(top, min(top+h, img.shape[0])):
        #        Y = 0.114*img[j][i][0] + 0.587 * img[j][i][1] + 0.299 * img[j][i][2]
        #        img[j][i][:] = Y
        #end = time.time()
        #print("grayPatch:", end-start)
        #cv2.imwrite('gray_test_face.jpg', img)
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
    img_bbox = []
    conf = 1.
    for box in bboxes_list:
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        box[2] = x + w - 1
        box[3] = y + h - 1
        bbox = {}
        bbox['x1'] = box[0]
        bbox['y1'] = box[1]
        bbox['x2'] = box[2]
        bbox['y2'] = box[3]
        bbox['conf'] = conf
        img_bbox.append(bbox)
        conf -= 0.001
    return img_bbox
