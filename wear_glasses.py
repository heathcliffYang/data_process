"""
Paste glasses on all faces in a given image

images/
glasses/

"""
from file_utils.basic import TraverseDir
from ctypes import CDLL, POINTER, c_int, byref, c_char_p
import xml.etree.ElementTree as ET
import cv2
import face_alignment
import math
import random
import numpy as np

# def distance():

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
    # print(bboxes_list)
    return bboxes_list



if __name__ == "__main__":
    src_dir = "/home/ginny/Projects/dataset/FD_source/MAFA_TEST/simple"
    dst_dir = "/home/ginny/Projects/dataset/FD_source/MAFA_TEST/glasses/"

    glasses_img = cv2.imread("./circle_glasses.png", cv2.IMREAD_UNCHANGED)
    print(glasses_img.shape)
    # for i in range(glasses_img.shape[0]):
    #     for j in range(glasses_img.shape[1]):
    #         print(glasses_img[i][j][:])

    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)
    # Example usage : preds = fa.get_landmarks(input)

    img_file_list = TraverseDir(src_dir, '.jpg')
    for img_path in img_file_list:
        img = cv2.imread(img_path)
        print(img_path)
        h, w, c = img.shape
        bbox_list = fd_get_bboxes(img_path)
        """
        Wear glasses!
        """
        count = 0
        for box in bbox_list:
            box_w = box[2] - box[0]
            box_h = box[3] - box[1]
            img_crop = img[box[1]:box[1]+box_h, box[0]:box[0]+box_w, :]
            preds = fa.get_landmarks(img_crop)
            if preds is None:
                continue

            # Vectors collected
            h_vector = (preds[0][27 - 1][0] - preds[0][18 - 1][0], preds[0][27 - 1][1] - preds[0][18 - 1][1])
            eyebrow_eye_vector = (preds[0][38 - 1][0] - preds[0][19 - 1][0], preds[0][38 - 1][1] - preds[0][19 - 1][1])

            s = (h_vector[0]*eyebrow_eye_vector[0] + h_vector[1]*eyebrow_eye_vector[1])/(h_vector[0]**2+h_vector[1]**2)
            v_vector = (eyebrow_eye_vector[0] - s * h_vector[0], eyebrow_eye_vector[1] - s * h_vector[1])

            eyebrow_nose_vector = (preds[0][30 - 1][0] - preds[0][19 - 1][0], preds[0][30 - 1][1] - preds[0][19 - 1][1])
            s = (h_vector[0]*eyebrow_nose_vector[0] + h_vector[1]*eyebrow_nose_vector[1])/(h_vector[0]**2+h_vector[1]**2)
            l_vector = (eyebrow_nose_vector[0] - s * h_vector[0], eyebrow_nose_vector[1] - s * h_vector[1])

            # 1. glasses height
            glasses_height_ratio = random.uniform(0, 0.23)
            glasses_height = math.sqrt(l_vector[0]**2 + l_vector[1]**2)
            glasses_height *= 1. + glasses_height_ratio

            # 2. glasses length
            glasses_length = math.sqrt((preds[0][27 - 1][0] - preds[0][18 - 1][0])**2 + (preds[0][27 - 1][1] - preds[0][18 - 1][1])**2)
            glasses_length_ratio = random.uniform(0, 0.4)
            glasses_length *= 1. + glasses_length_ratio

            tmp_glasses = glasses_img.copy()

            glasses_color = [random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)]

            # Before rotate
            for i in range(tmp_glasses.shape[0]):
                for j in range(tmp_glasses.shape[1]):
                    if tmp_glasses[i][j][3] == 0:
                        for k in range(3):
                            tmp_glasses[i][j][k] = 255
                    else:
                        for k in range(3):
                            tmp_glasses[i][j][k] = glasses_color[k]

            ## Resize glasses image
            tmp_glasses = cv2.resize(tmp_glasses, (int(glasses_length), int(glasses_height)))#, cv2.INTER_AREA)

            # Center
            C = np.eye(3)
            C[0, 2] = - int(glasses_length) / 2  # x translation (pixels)
            C[1, 2] = - int(glasses_height) / 2  # y translation (pixels)

            # 3. glasses rotation degree
            rotate = math.atan((preds[0][27 - 1][1] - preds[0][18 - 1][1]) / (preds[0][27-1][0] - preds[0][18 - 1][0]))
            rotate = rotate / math.pi * 180 * (-1)

            rotate_matrix = cv2.getRotationMatrix2D((0, 0), rotate, scale = 1)

            R = np.eye(3)
            R[:2] = rotate_matrix

            pre_M_1 = rotate_matrix @ np.array([[int(glasses_length)],[int(glasses_height)],[1]])
            pre_M_2 = rotate_matrix @ np.array([[0],[0],[1]])
            glasses_img_w = int(abs(pre_M_1[0,0] - pre_M_2[0,0]))
            glasses_img_h = int(abs(pre_M_1[1,0] - pre_M_2[1,0]))

            pre_M_1 = rotate_matrix @ np.array([[0],[int(glasses_height)],[1]])
            pre_M_2 = rotate_matrix @ np.array([[int(glasses_length)],[0],[1]])

            glasses_img_w = max( abs(int(pre_M_1[0,0] - pre_M_2[0,0])), glasses_img_w)
            glasses_img_h = max( abs(int(pre_M_1[1,0] - pre_M_2[1,0])), glasses_img_h)

            # Translation
            T = np.eye(3)
            T[0, 2] = 0.5 * glasses_img_w  # x translation (pixels)
            T[1, 2] = 0.5 * glasses_img_h  # y translation (pixels)

            tmp_glasses = cv2.GaussianBlur(tmp_glasses, (3,3), 0)
            tmp_glasses = cv2.warpAffine(tmp_glasses, (T @ R @ C)[:2], (glasses_img_w, glasses_img_h))

            # Glasses mid point
            glass_midpt = T @ R @ C @ np.array([[int(glasses_length/2)],[0],[1]])
            s = glass_midpt[1] / v_vector[1]
            glass_left_shift = glass_midpt[0] - s * v_vector[0]

            # Nose mid point
            nose_mid = np.array(preds[0][28 - 1])
            glasses_position_ratio = random.uniform(0.8, 0.95)
            nose_mid[0] -= glasses_position_ratio / 2 * l_vector[0]
            nose_mid[0] -= s * v_vector[0]
            nose_mid[1] -= glasses_position_ratio / 2 * l_vector[1]
            nose_mid[1] -= s * v_vector[1]
            img = cv2.circle(img, (int(box[0] + nose_mid[0]), int(box[1] + nose_mid[1])), 1, (255,0,255), -1)
            # Glasses paste point
            top_left = [nose_mid[0] - glass_left_shift, nose_mid[1]]
            img = cv2.circle(img, (int(box[0] + top_left[0]), int(box[1] + top_left[1])), 1, (255,0,255), -1)

            # Paste glasses
            for i in range(int(box[1] + top_left[1]), int(box[1] + top_left[1])+glasses_img_h):
                for j in range(int(box[0] + top_left[0]), int(box[0] + top_left[0])+glasses_img_w):
                    if tmp_glasses[i-int(box[1] + top_left[1])][j - int(box[0] + top_left[0])][3] > 50:#120:
                        for k in range(3):
                            img[i,j,k] = tmp_glasses[i-int(box[1] + top_left[1])][j - int(box[0] + top_left[0])][k]
                    else:
                        for k in range(3):
                            tmp_glasses[i-int(box[1] + top_left[1])][j - int(box[0] + top_left[0])][k] = 255

            cv2.imwrite(dst_dir+img_path.split('/')[-1]+"glasses.jpg", tmp_glasses)
            print("Glass info:\n  r = %.2f, length = %.1f\n  r = %.2f, height = %.1f "%(glasses_length_ratio, glasses_length, glasses_height_ratio, glasses_height))


            # for i in range(68):
            pt = preds[0][28 - 1]
            img = cv2.circle(img, (int(box[0] + pt[0]), int(box[1] + pt[1])), 1, (0,255,255), -1)
            count += 1
            # pt = preds[0][18 - 1]
            # img = cv2.circle(img, (int(box[0] + pt[0]), int(box[1] + pt[1])), 1, (0,255,255), -1)
        cv2.imwrite(dst_dir+img_path.split('/')[-1], img)
