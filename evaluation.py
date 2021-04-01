#!/usr/bin/env python
"""
@author: heathcliffYang

1. box
each frame image, we have ground-truth bounding box data frame n x [x1, y1, w, h]
                          proposed bounding box [frames, bboxes_list, 4]

2. string
"""
import data_process
from data_process.label_utils.label_io import ReadGTFile, ReadBBoxYoloLabels
from data_process.file_utils.basic import TraverseDir
from data_process.data_augmentation.face import fd_get_bboxes
from data_process.label_utils.tools import mAP
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testMode", type=str, help="box or string match")
    parser.add_argument("gtFilePath", type=str)
    parser.add_argument("gtColumn", type=str)
    parser.add_argument("predDir", type=str)
    parser.add_argument("--compareDir", type=str, default=None, nargs='?')
    parser.add_argument("--printFail", type=int, default=0, nargs='?')

    args = parser.parse_args()

    if 'string' in args.testMode:
        # Retrieve ground truth
        gt_file_path = args.gtFilePath
        gt_column = args.gtColumn
        answer_dict = ReadGTFile(gt_file_path, gt_column)

        # Get prediction result
        prediction_list = TraverseDir(args.predDir, '.jpg', skip='corners')
        hits = 0
        fails = 0
        fail_list = []
        for f in prediction_list:
            # extract prediction
            pred = f.split('_')[-1].replace('.jpg', '').replace('-','')
            if pred in answer_dict:
                answer_dict[pred] += 1
                hits += 1
            # else:
                # print(pred)
        print("\nItems fail to detect:")
        for ans in answer_dict:
            if answer_dict[ans] == 0:
                fails += 1
                fail_list.append(ans)
                if args.printFail == 1:
                    print("  ", ans)
        print("Hits / Predictions: %d / %d = %.3f"%\
              (hits, len(prediction_list), float(hits)/len(prediction_list))\
             )
        print("Fails / Total ans: %d / %d = %.3f, Accuracy: %.3f"%\
               (fails, len(answer_dict), float(fails)/len(answer_dict),\
                1. - float(fails)/len(answer_dict)))

        if args.compareDir is not None:
            answer_dict = ReadGTFile(gt_file_path, gt_column)
            prediction_list_2 = TraverseDir(args.compareDir, '.jpg', skip='corners')
            fail_list_2 = {}
            count_1 = 0
            count_2 = 0
            common = 0
            for f in prediction_list_2:
                # extract prediction
                pred = f.split('_')[-1].replace('.jpg', '').replace('-','')
                if pred in answer_dict:
                    answer_dict[pred] += 1
            for ans in answer_dict:
                if answer_dict[ans] == 0:
                    fail_list_2[ans] = 0
            print("Diff 2 directories:\n  Fails only the first owned:")
            for fail_ans in fail_list:
                if fail_ans not in fail_list_2:
                    count_1 += 1
                    print("    ", fail_ans)
                else:
                    fail_list_2[fail_ans] = 1
                    common += 1
            print("  Fails only the second owned:")
            for fail_ans in fail_list_2:
                if fail_list_2[fail_ans] == 0:
                    count_2 += 1
                    print("    ", fail_ans)
            print("1: %d, 2: %d, common: %d"%(count_1, count_2, common))
    elif 'box' in args.testMode:
        print("Evaluate bboxes iou")
        img_dir = '/home/ginny/Projects/dataset/masked_face_dataset/backup_labels/TEST/JPEGImages'
        imgs_bbox_gt = ReadBBoxYoloLabels(img_dir)

        print(imgs_bbox_gt)

        img_file_list = TraverseDir(img_dir, '.jpg', check_exist='txt')#, debug=True)
        imgs_bbox_pre = {}
        for img_path in img_file_list:
            img_bbox = fd_get_bboxes(img_path)
            imgs_bbox_pre[img_path] = img_bbox
            # print("image: %s\n  gt: "%(img_path), imgs_bbox_gt[img_path])
            # print("  pred: ", imgs_bbox_pre[img_path])

        score = mAP(imgs_bbox_gt, imgs_bbox_pre, 0.5)
        print("mAP@0.5:", score)
