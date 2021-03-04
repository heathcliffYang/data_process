"""
images/
labels/
results/ : save plot images
"""
from .label_io import PlotBox, ReadYoloLabel

def PlotLabelFile(img, label_path):
    bbox_list = ReadYoloLabel(label_path, 'xyxy')
    for bbox in bbox_list:
        PlotBox(img, bbox)
