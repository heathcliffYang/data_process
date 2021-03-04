def LabelRatio2Coord(img, bbox):
    h, w, _ = img.shape
    bbox['x1'] = int(bbox['x1'] * w)
    bbox['x2'] = int(bbox['x2'] * w)
    bbox['y1'] = int(bbox['y1'] * h)
    bbox['y2'] = int(bbox['y2'] * h)
    return bbox

def LabelFormatTrans(bbox):
    if 'x1' in bbox:
        # xyxy 2 xywh
        bbox['x_center'] = (bbox['x1'] + bbox['x2']) / 2
        bbox['y_center'] = (bbox['y1'] + bbox['y2']) / 2
        bbox['w_box'] = bbox['x2'] - bbox['x1']
        bbox['h_box'] = bbox['y2'] - bbox['y1']
    else:
        # xywh 2 xyxy
        bbox['x1'] = bbox['x_center'] - bbox['w_box']/2
        bbox['x2'] = bbox['x_center'] + bbox['w_box']/2
        bbox['y1'] = bbox['y_center'] - bbox['h_box']/2
        bbox['y2'] = bbox['y_center'] + bbox['h_box']/2
    return bbox

def clipping_coordinate(img, xy):
    h, w, _ = img.shape
    xy[0] = int(max(0, xy[0]))
    xy[1] = int(max(0, xy[1]))
    xy[0] = int(min(w-1, xy[0]))
    xy[1] = int(min(h-1, xy[1]))
    return xy

def clipping_box(img, bbox):
    bbox['x1']
