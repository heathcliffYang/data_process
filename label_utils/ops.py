def LabelRatio2Coord(img, bbox):
    h, w, _ = img.shape
    bbox['x1'] = int(bbox['x1'] * w)
    bbox['x2'] = int(bbox['x2'] * w)
    bbox['y1'] = int(bbox['y1'] * h)
    bbox['y2'] = int(bbox['y2'] * h)
    return bbox


def IsNormalizedBBox(bbox):
    # TODO: simpler check ratio way
    if bbox['x1'] > 1. or bbox['x1'] < 0.:
        print(bbox)
        return False
    if bbox['x2'] > 1. or bbox['x2'] < 0.:
        print(bbox)
        return False
    if bbox['y1'] > 1. or bbox['y1'] < 0.:
        print(bbox)
        return False
    if bbox['y2'] > 1. or bbox['y2'] < 0.:
        print(bbox)
        return False
    return True


def CorrectBBox(bbox):
    bbox = clipping_box(bbox)
    bbox = LabelFormatTrans(bbox)
    return bbox

def LabelFormatTrans(bbox):
    if 'x1' in bbox:
        print("xyxy to xywh")
        # xyxy 2 xywh
        bbox['x_center'] = (bbox['x1'] + bbox['x2']) / 2
        bbox['y_center'] = (bbox['y1'] + bbox['y2']) / 2
        bbox['w_box'] = bbox['x2'] - bbox['x1']
        bbox['h_box'] = bbox['y2'] - bbox['y1']
    else:
        print("xywh 2 xyxy")
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


def clipping_box(bbox):
    print("Clipping bbox", bbox)
    bbox['x1'] = max(0.0001, bbox['x1'])
    bbox['x2'] = min(1.-0.0001, bbox['x2'])
    bbox['y1'] = max(0.0001, bbox['y1'])
    bbox['y2'] = min(1.-0.0001, bbox['y2'])
    print("Clipping bbox after", bbox)
    return bbox
