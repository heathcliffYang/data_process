import cv2
import pandas as pd
from .ops import LabelRatio2Coord, clipping_coordinate

# cv2.putText(影像, 文字, 座標, 字型, 大小, 顏色, 線條寬度, 線條種類)

def PlotBox(img, bbox, info=None):
    h, w, _ = img.shape
    bbox = LabelRatio2Coord(img, bbox)
    text_coord = clipping_coordinate(img, [bbox['x1'] - w*0.01, bbox['y1'] - h*0.01])
    if info is not None and 'label' in info:
        cv2.putText(img, str(bbox['label']),\
                         tuple(text_coord), cv2.FONT_HERSHEY_SIMPLEX,\
                         w*0.1, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.rectangle(img, (bbox['x1'], bbox['y1']),\
                       (bbox['x2'], bbox['y2']), (0, 255, 255), 2)


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
