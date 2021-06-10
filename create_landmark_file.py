"""
Read a face image, generate its landmarks and then write into a file

dataset_name/
    train/
        JPEGImages/
            person_1/
            person_2/

        labels/
            person_1/
            person_2/
"""
from data_process.file_utils.basic import *
from data_process.label_utils.label_io import WriteLandmarkFile, ReadLandmarkFile, WriteLandmarkFile
from data_process.data_augmentation.landmarks import *
import argparse
import face_alignment
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sourceImgDir", type=str)
    args = parser.parse_args()

    src_img_dir = args.sourceImgDir
    src_img_file_list = TraverseDir(src_img_dir, ['.jpg'], skip='.txt')
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)

    for img_path in src_img_file_list:
        if not os.path.isfile(img_path):
            continue
        img = cv2.imread(img_path)
        label_path =PathHandler(img_path, 'create_txt')
        print(img_path, "\n", label_path, "\n")
        if img.shape[0] < 100 or img.shape[1] < 100:
            os.remove(img_path)
            continue
        preds = fa.get_landmarks(img)
        if preds == None:
            WriteLandmarkFile(None, label_path, img.shape[1], img.shape[0])
            continue
        landmarks = Landmarks(preds)

        # print("nodes direct:")
        # for i in range(68):
        #     node = landmarks[i+1]
        #     print(node.x, node.y)
        # print("nodes write")
        WriteLandmarkFile(landmarks, label_path, img.shape[1], img.shape[0])

        # print("nodes read")
        read_preds = ReadLandmarkFile(label_path, img.shape[1], img.shape[0])
        if read_preds != None:
            read_landmarks = Landmarks(read_preds)
        # print("nodes red:")
        # for i in range(68):
        #     node = read_landmarks[i+1]
        #     print(node.x, node.y)
        # break
