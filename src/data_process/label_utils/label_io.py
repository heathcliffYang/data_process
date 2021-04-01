import cv2
import pandas as pd
from .ops import LabelRatio2Coord, clipping_coordinate
from data_process.file_utils.basic import TraverseDir, PathHandler

# cv2.putText(影像, 文字, 座標, 字型, 大小, 顏色, 線條寬度, 線條種類)

def PlotBox(img, bbox, info=None):
    # Color set
    color_set = {'0': (0, 255, 255), # yellow
                 '1': (255, 255, 0), # blue
                 '2': (0, 255, 0)}   # green
    h, w, _ = img.shape
    bbox = LabelRatio2Coord(img, bbox)
    if bbox is False:
        return False
    text_coord = clipping_coordinate(img, [bbox['x1'] - w*0.01, bbox['y1'] - h*0.01])
    if info is not None and 'label' in info:
        print('plot', text_coord, img.shape)
        cv2.putText(img, str(bbox['label']),\
                         tuple(text_coord), cv2.FONT_HERSHEY_SIMPLEX,\
                         w*0.002, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(img, (bbox['x1'], bbox['y1']),\
                       (bbox['x2'], bbox['y2']), color_set[str(bbox['label'])], 2)


def ReadYoloLabel(label_path, bbox_format):
    """
    bbox_format: 'xyxy' or 'xywh'

    returns:
        bbox_list : list of bbox dicts
    *** ratio
    *** clipping
    """
    bbox_list = []
    f = open(label_path, 'r')
    for i in f:
        i = i.split(' ')
        bbox = dict()
        label = int(i[0])
        bbox['label'] = label
        if bbox_format == 'xyxy':
            x_center = float(i[1])
            y_center = float(i[2])
            w_box = float(i[3])
            h_box = float(i[4])
            x1 = x_center-w_box/2
            x2 = x_center+w_box/2
            y1 = y_center-h_box/2
            y2 = y_center+h_box/2
            bbox['x_center'] = x_center
            bbox['y_center'] = y_center
            bbox['w_box'] = w_box
            bbox['h_box'] = h_box
            bbox['x1'] = x1
            bbox['x2'] = x2
            bbox['y1'] = y1
            bbox['y2'] = y2
        elif bbox_format == 'xywh':
            x_center = float(i[1])
            y_center = float(i[2])
            w_box = float(i[3])
            h_box = float(i[4])
            bbox['x_center'] = x_center
            bbox['y_center'] = y_center
            bbox['w_box'] = w_box
            bbox['h_box'] = h_box
        bbox_list.append(bbox)
    return bbox_list


def WriteYoloLabel(label_path, bbox_list):
    f = open(label_path, 'w')
    for bbox in bbox_list:
        f.write('%d %f %f %f %f\n'%(bbox['label'],\
                                  bbox['x_center'],\
                                  bbox['y_center'],\
                                  bbox['w_box'],\
                                  bbox['h_box']))
    f.close()
    return True


def ReadGTFile(gt_file_path, answer_column):
    answer_dict = dict()
    df = pd.read_csv(gt_file_path)
    for i, lpnumber in df.iterrows():
        if  isinstance(lpnumber[answer_column], str):
            ans = lpnumber[answer_column].strip()
            answer_dict[ans] = 0
    return answer_dict


def ReadBBoxPredictFile(file_path):
    """
    Args:
        file path : str

        File format:
            image_name:<image_name.jpg>
                         (percentage) (abs)
            <class_name>,<confidence>,<x1>,<y1>,<x2>,<y2>
            ...
            end

        example:
        image_name:a.jpg
        full,98%,19,30,37,50
        ...
        end

    Returns:
        imgs_bbox : dict

        {img_name1: [bbox1, bbox2, ...],
         img_name2: [bbox1, bbox2, ...],
         ...
        }
    """
    f = open(file_path, 'r')
    imgs_bbox = {}
    img_bbox = []
    imgs_name = []
    for l in f:
        if 'image_name:' in l or 'end' in l:
            if len(img_bbox) != 0:
                img_bbox.sort(key = lambda x: x['conf'], reverse=True)
                imgs_bbox[l] = img_bbox.copy()
                img_bbox = []
            # record image name
            img_name = l.split(':')[-1]
            imgs_name.append(img_name)
        else:
            # Read bboxes!
            l = l.split(',')
            bbox = dict()
            bbox['label'] = l[0]
            bbox['conf'] = float(l[1].split('%')[0])
            bbox['x1'] = int(l[2])
            bbox['y1'] = int(l[3])
            bbox['x2'] = int(l[4])
            bbox['y2'] = int(l[5])

            img_bbox.append(bbox)
    return imgs_bbox


def ReadBBoxYoloLabels(dir_path):
    img_file_list = TraverseDir(dir_path, '.jpg', check_exist='txt')
    imgs_bbox = {}
    for img_path in img_file_list:
        label_path = PathHandler(img_path, 'find_txt')
        img = cv2.imread(img_path)
        bboxes = ReadYoloLabel(label_path, 'xyxy')
        abs_bbox_list = []
        for bbox in bboxes:
            bbox = LabelRatio2Coord(img, bbox)
            abs_bbox_list.append(bbox)

        imgs_bbox[img_path] = abs_bbox_list.copy()
    return imgs_bbox
