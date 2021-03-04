import os
import cv2

image_extensions = ['.jpg', '.png', '.JPG', '.jpeg']
label_extensions = ['.json', '.txt']
img_dir_names = {'/images/', '/JPEGImages/'}
label_dir_names = {'.json': '/labels/', '.txt': '/labelsJSON/'}

def TraverseDir(dir, extension, check_exist, skip=None):
    # split skip types
    skip_dir = []
    skip_file_pattern = []
    if isinstance(skip, list) and len(skip) != 0:
        for skip_string in skip:
            if '/' in skip_string:
                skip_dir.append(skip_string)
            else:
                skip_file_pattern.append(skip_string)
    elif isinstance(skip, str):
        if '/' in skip_string:
            skip_dir.append(skip_string)
        else:
            skip_file_pattern.append(skip_string)
    # traverse dir
    file_list = []
    for root, dirs, files in os.walk(dir):
        skip_dir_signal = False
        # filter out some directories
        for skip_string in skip_dir:
            if skip_string in root:
                skip_dir_signal = True
                break
        if skip_dir_signal is True:
            continue
        # traverse files
        for f in files:
            if extension not in f:
                break
            # filter out some file names
            skip_file_signal = False
            for skip_string in skip_file_pattern:
                if skip_string in f:
                    skip_file_signal = True
                    break
            if skip_file_signal is True:
                continue
            # Check corresponding files exist or not
            if check_exist is True:
                path = PathHandler(root+"/"+f, 'find')
                if CheckFile(path):
                    file_list.append(root+"/"+f)
                else:
                    continue
                    print(f)
            else:
                file_list.append(root+"/"+f)
    print("Total available: %d files"%(len(file_list)))
    return file_list

def PathHandler(path, task):
    extension = '.'+path.split('.')[-1]
    if task == 'plot': # plot result images
        path = path.replace(label_dir_names[extension], '/results/').replace(extension, '.jpg')
    elif task == 'find':
        if extension == '.json' or extension == '.txt':
            # Given a label file and we need to find the image file
            img_path = None
            for img_dir in img_dir_names:
                path_pre = path.replace(label_dir_names[extension], img_dir).split('.')[0]
                for img_extension in img_extensions:
                    if CheckFile(path_pre + img_extension):
                        img_path = path_pre + img_extension
            return img_path
        else:
            # Given an image file and we need to find the label file


    return path

def CheckFile(path):
    if os.path.isfile(path) == False  or os.stat(path).st_size == 0:
        print("False")
        return False
    else:
        # print("True")
        return True
