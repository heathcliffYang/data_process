import numpy as np
import cv2
import random
import math

"""
Reference: https://github.com/ultralytics/yolov5
"""
def random_perspective(img, degrees=10, translate=.1, scale=.1, shear=10, perspective=0.0, border=(0, 0)):
    height = img.shape[0] + border[0] * 2  # shape(h,w,c)
    width = img.shape[1] + border[1] * 2

    height_orig = img.shape[0] + border[0] * 2  # shape(h,w,c)
    width_orig = img.shape[1] + border[1] * 2

    # Center
    C = np.eye(3)
    C[0, 2] = -img.shape[1] / 2  # x translation (pixels)
    C[1, 2] = -img.shape[0] / 2  # y translation (pixels)

    # Perspective
    P = np.eye(3)
    P[2, 0] = random.uniform(-perspective, perspective)  # x perspective (about y)
    P[2, 1] = random.uniform(-perspective, perspective)  # y perspective (about x)

    if random.randint(0,1) < 0.5:
        # Shear
        S = np.eye(3)
        sx_d = random.uniform(-shear, shear)
        sy_d = random.uniform(-shear, shear)
        S[0, 1] = math.tan(sx_d * math.pi / 180)  # x shear (deg)
        S[1, 0] = math.tan(sy_d * math.pi / 180)  # y shear (deg)

        # Rotation and Scale
        R = np.eye(3)
        if abs(sx_d) > 5 or abs(sy_d) > 5:
            degrees = 0
        a = random.uniform(-degrees, degrees)
        s = random.uniform(1 - scale, 1 + scale)
        R[:2] = cv2.getRotationMatrix2D(angle=a, center=(0, 0), scale=s)
    else:
        # Rotation and Scale
        R = np.eye(3)
        a = random.uniform(-degrees, degrees)
        s = random.uniform(1 - scale, 1 + scale)
        R[:2] = cv2.getRotationMatrix2D(angle=a, center=(0, 0), scale=s)

        # Shear
        S = np.eye(3)
        shear = 15
        sx_d = random.uniform(-shear, shear)
        sy_d = random.uniform(-shear, shear)
        S[0, 1] = math.tan(sx_d * math.pi / 180)  # x shear (deg)
        S[1, 0] = math.tan(sy_d * math.pi / 180)  # y shear (deg)


    # Compute final width and height
    pre_M_1 = S @ R @ P @ np.array([[width_orig],[height_orig],[1]])
    pre_M_2 = S @ R @ P @ np.array([[0],[0],[1]])
    width = int(abs(pre_M_1[0,0] - pre_M_2[0,0]))
    height = int(abs(pre_M_1[1,0] - pre_M_2[1,0]))

    pre_M_1 = S @ R @ P @ np.array([[0],[height_orig],[1]])
    pre_M_2 = S @ R @ P @ np.array([[width_orig],[0],[1]])

    width = max( abs(int(pre_M_1[0,0] - pre_M_2[0,0])), width)
    height = max( abs(int(pre_M_1[1,0] - pre_M_2[1,0])), height)

    # Translation
    T = np.eye(3)
    T[0, 2] = random.uniform(0.5 - translate, 0.5 + translate) * width  # x translation (pixels)
    T[1, 2] = random.uniform(0.5 - translate, 0.5 + translate) * height  # y translation (pixels)

    # Combined rotation matrix
    M = T @ S @ R @ P @ C  # order of operations (right to left) is IMPORTANT
    if (border[0] != 0) or (border[1] != 0) or (M != np.eye(3)).any():  # image changed
        if perspective:
            img = cv2.warpPerspective(img, M, dsize=(width, height), borderValue=(114, 114, 114))
        else:  # affine
            img = cv2.warpAffine(img, M[:2], dsize=(width, height), borderValue=(114, 114, 114))

    if width == 0 or height == 0:
        print("Hi~ image:", img.shape, height, width)
    img = cv2.resize(img, (width_orig, height_orig))

    blur_kernel_size = random.choice([1,3,5,7,9,11])
    img = cv2.GaussianBlur(img,(blur_kernel_size,blur_kernel_size),0)
    if random.randint(0,1) < 0.5:
        img = cv2.bitwise_not(img)

    return img
