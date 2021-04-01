"""
images/
labels/
results/ : save plot images
"""
from .label_io import PlotBox, ReadYoloLabel
from .ops import IsNormalizedBBox, CorrectBBox, img_box_match


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

def mAP(imgs_bbox_gt, imgs_bbox_pre, iou_threshold):
    """
    mAP calculation (Precision recall curve)
    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)

    Reference: https://github.com/rafaelpadilla/Object-Detection-Metrics
    """
    imgs_num_gt_bboxes = dict()
    total_pre_TF = []
    total_num_bboxes = 0
    for img_name in imgs_bbox_gt:
        if img_name in imgs_bbox_pre:
            pre_TF, num_gt_bboxes = img_box_match(imgs_bbox_gt[img_name],\
                                                  imgs_bbox_pre[img_name], iou_threshold)
            imgs_num_gt_bboxes[img_name] = num_gt_bboxes
            total_num_bboxes += num_gt_bboxes
            total_pre_TF += pre_TF
    total_pre_TF.sort(key = lambda x: x[1], reverse=True)
    #
    TP = 0
    FP = 0
    FN = total_num_bboxes
    tmp_precision = 0
    precision_list = []
    recall_list = []
    for pre in total_pre_TF:
        if pre[0] == True:
            TP += 1
            FN -= 1
        else:
            FP += 1

        if TP + FP != 0:
            precision = TP / (TP + FP)
        else:
            precision = 0

        if TP + FN != 0:
            recall = TP / (TP + FN)
        else:
            recall = 0

        print(TP, FP, FN, precision, recall)
        precision_list.append(precision)
        recall_list.append(recall)
    # area under precision x recall curve,
    # NOT 11-point interpolation !! (TODO)
    precision_list.reverse() # ascending
    recall_list.reverse() # ascending
    mAP = 0
    p_prev = precision_list[0]
    r_prev = recall_list[0]
    maximum_precision_collect = [0.] * 11
    for p, r in zip(precision_list, recall_list):
        interpolate_bucket_idx = int(r * 10 + 0.5) - 1
        # print(r, interpolate_bucket_idx)
        if p >= p_prev:
            # print(p)
            maximum_precision_collect[interpolate_bucket_idx] = p
            p_prev = p
            r_prev = r
    p = 0
    for i in range(10, -1, -1):
        # print(i, maximum_precision_collect[i])
        if maximum_precision_collect[i] != 0.:
            p = maximum_precision_collect[i]
        else:
            maximum_precision_collect[i] = p
    # print(maximum_precision_collect)
    mAP = sum(maximum_precision_collect) / 11.
    return mAP


def hello():
    pass
