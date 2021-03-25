"""
Read a list of many pairs of image name and person ID

Create person ID name directory and then put images tagged this person ID in it
"""
from shutil import copyfile
import os
from file_utils.basic import CheckFile

"""
This script can used by `CeleA/`
"""
# # Read list file iteratively
# list_path = '/home/ginny/Projects/dataset/face_recognition/source/celebA/Anno/identity_CelebA_train.txt'
# img_dir = '/home/ginny/Projects/dataset/face_recognition/source/celebA/Img/train/'
# dst_dir = '/home/ginny/Projects/dataset/face_recognition/source/celebA/Img/celebA/'
#
# list_fp = open(list_path, 'r')
# for i in list_fp:
#     i = i.split(' ')
#     img_name = i[0]
#     person_ID = i[1].split('\n')[0]
#     if not CheckFile(img_dir + img_name):
#         print("No this img:", img_dir + img_name)
#         continue
#     if not os.path.isdir(dst_dir+person_ID+'/'):
#         os.makedirs(dst_dir+person_ID+'/')
#     print('source: %s\ndestination: %s\n'%(img_dir + img_name, dst_dir + person_ID + '/' + img_name))
#     copyfile(img_dir + img_name , dst_dir + person_ID + '/' + img_name)

"""
For `DataTang/`

Read `src_dst.txt`, grab person_ID and image name
"""
list_path = '/home/ginny/Projects/dataset/face_recognition/source/DataTang/src_dst.txt'
img_dir = '/home/ginny/Projects/dataset/face_recognition/source/DataTang/faces_128/'
dst_dir = '/home/ginny/Projects/dataset/face_recognition/source/DataTang/person_split/'

list_fp = open(list_path, 'r')
for i in list_fp:
    i = i.split(',')
    person_ID = i[0].split('/')[4]
    img_name = i[1].split('\n')[0].replace(' ','')
    if not CheckFile(img_dir + img_name):
        print("No this img:", img_dir + img_name)
        continue
    if not os.path.isdir(dst_dir + person_ID + '/'):
        os.makedirs(dst_dir+person_ID+'/')
    copyfile(img_dir + img_name, dst_dir + person_ID + '/' + img_name)
