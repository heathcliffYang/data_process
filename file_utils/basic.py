import os
import cv2

image_extensions = ['.jpg', '.png', '.JPG', '.jpeg']
label_extensions = ['.json', '.txt']
img_dir_names = {'/images/', '/JPEGImages/'}
label_dir_names = {'.txt': '/labels/', '.json': '/labelsJSON/'}

def TraverseDir(dir, extension, check_exist=None, skip=None):
    """
    check_exist : json txt image, None
    """
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
            if check_exist is None:
                file_list.append(root+"/"+f)
            else:
                path = PathHandler(root+"/"+f, 'find'+'_'+check_exist)
                if path is not None: # Check if they are an image-label pair
                    file_list.append(root+"/"+f)
    print("Total available: %d files"%(len(file_list)))
    return file_list


def PathHandler(path, task):
    extension = '.'+path.split('.')[-1]
    if task == 'plot': # plot result images
        path = path.replace(label_dir_names[extension], '/results/').replace(extension, '.jpg')
    elif 'find' in task or 'create' in task:
        if 'image' in task and extension == '.json' or extension == '.txt':
            # label -> image
            img_path = None
            for img_dir in img_dir_names: # find all possible image folder name
                path_pre = path.replace(label_dir_names[extension], img_dir).split('.')[0]
                for img_extension in img_extensions: # find all image extensions
                    if CheckFile(path_pre + img_extension):
                        img_path = path_pre + img_extension
            return img_path
        else:
            # image -> label
            label_path = None
            for label_ext in label_extensions:# execute possible label file
                if label_ext.replace('.','') not in task:
                    continue
                for img_dir in img_dir_names: # find all possible image folder name
                    if img_dir not in path:
                        continue
                    path_pre = path.replace(img_dir, label_dir_names[label_ext]).split('.')[0]
                    if 'create' in task:
                        label_path = path_pre + label_ext
                    elif CheckFile(path_pre + label_ext):
                        label_path = path_pre + label_ext
                        break
            return label_path
    return path


def CheckFile(path):
    if os.path.isfile(path) == False  or os.stat(path).st_size == 0:
        return False
    else:
        # print("True")
        return True
