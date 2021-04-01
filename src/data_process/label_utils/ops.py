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


def iou_compute(box_a, box_b):
    # intersection area
    x1 = max(box_a['x1'], box_b['x1'])
    y1 = max(box_a['y1'], box_b['y1'])
    x2 = min(box_a['x2'], box_b['x2'])
    y2 = min(box_a['y2'], box_b['y2'])
    w = max(x2 - x1, 0)
    h = max(y2 - y1, 0)
    i_area = w*h
    # uion area
    u_area = (box_a['x2'] - box_a['x1'])*(box_a['y2'] - box_a['y1'])\
           + (box_b['x2'] - box_b['x1'])*(box_b['y2'] - box_b['y1']) - i_area
    return float(i_area) / u_area


def img_box_match(bboxes_gt, bboxes_pre, iou_threshold):
    """
    Goal:
        Returns info for mAP calculation (Precision recall curve)
        Precision = TP / (TP + FP)
        Recall = TP / (TP + FN)

    Returns:
        list of [TP/FP, conf]
        num_gt_bboxes : int

    Notes:
        For each prediction bbox, it finds what ground-truth bbox it belongs to in a descending order of confidence
        If iou(pred_box, gt_box) > iou_threshold, this gt_box is assigned to this pred_box.
        Then we check if the class is correct or not -> correct: TP
                                                     -> incorrect: FP
        The rest of prediction bboxes cannot find gt bboxes -> FP
        The rest of gt bboxes haven't been assigned to any prediction bboxes -> FN
    """
    num_gt_bboxes = len(bboxes_gt)
    gt_assign = [0] * num_gt_bboxes
    pre_TF = []
    for box_pre in bboxes_pre:
        max_iou = 0
        max_iou_index = -1
        for i in range(num_gt_bboxes):
            iou_temp = iou_compute(box_pre, bboxes_gt[i])
            if gt_assign[i] == 0: # This gt bbox hasn't been assigned
                # Find the box_gt with largest iou with this given box_pre
                if iou_temp > iou_threshold and iou_temp > max_iou:
                    max_iou_index = i
                    max_iou = iou_temp
        if max_iou_index != -1: # successfully find a box_gt
            gt_assign[i] = 1
            # TP
            pre_TF.append([True, box_pre['conf']])
        else:
            # FP
            pre_TF.append([False, box_pre['conf']])
    return pre_TF, num_gt_bboxes
