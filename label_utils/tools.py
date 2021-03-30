"""
images/
labels/
results/ : save plot images
"""
from .label_io import PlotBox, ReadYoloLabel
from .ops import IsNormalizedBBox, CorrectBBox


def PlotLabelFile(img, label_path):
    bbox_list = ReadYoloLabel(label_path, 'xyxy')
    for bbox in bbox_list:
        state = PlotBox(img, bbox, 'label')
        if state is False:
            return False


def CheckLabelNorm(img, label_path):
    bbox_list = ReadYoloLabel(label_path, 'xyxy')
    norm = True
    new_bbox_list = []
    for bbox in bbox_list:
        if IsNormalizedBBox(bbox) is False:
            norm =  False
            new_b = CorrectBBox(bbox)
            print("New b", new_b)
            new_bbox_list.append(new_b)
        else:
            new_bbox_list.append(bbox)
    if norm is False:
        return new_bbox_list
    else:
        return None

def mAP():
    """
    Reference: https://github.com/rafaelpadilla/Object-Detection-Metrics
    """
    pass
