"""
Paste glasses on all faces in a given image

images/
glasses/

"""
from file_utils.basic import TraverseDir
from ctypes import CDLL, POINTER, c_int, byref, c_char_p
import xml.etree.ElementTree as ET
import cv2
# import face_alignment

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

    glasses_img = cv2.imread("./black_glasses.png")
    for i in range(glasses_img.shape[0]):
        for j in range(glasses_img.shape[1]):
            print(glasses_img[i][j][:])

    # fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)
    # Example usage : preds = fa.get_landmarks(input)

    img_file_list = TraverseDir(src_dir, '.jpg')
    for img_path in img_file_list:
        print(img_path)
        img = cv2.imread(img_path)
        h, w, c = img.shape
        bbox_list = fd_get_bboxes(img_path)



        # """
        # Wear glasses!
        # """
        # for box in bbox_list:
        #     print(box)
        #     box_w = box[2] - box[0]
        #     box_h = box[3] - box[1]
        #     img_crop = img[box[1]:box[1]+box_h, box[0]:box[0]+box_w, :]
        #     print(img_crop.shape)
        #     # preds = fa.get_landmarks(img_crop)
        #     print(preds[0][0])
        #     for i in range(68):
        #         pt = preds[0][i]
        #         img = cv2.circle(img, (int(box[0] + pt[0]), int(box[1] + pt[1])), 3, (0,255,255), 1)
        #     break
        # print("save!!!")
        # cv2.imwrite(dst_dir+img_path.split('/')[-1], img)
