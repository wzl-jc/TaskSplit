import argparse
import dlib
import torch.backends.cudnn as cudnn
import multiprocessing as mp
import cv2
import time
import numpy as np
import os
import random


def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


def plot_boxes(pos_list, img1, img_name=None, color=None, line_thickness=None):
    '''
    在img上绘制pos_list中所有的bounding box
    :param img_name: 保存的图像名字
    :param line_thickness: 绘制bounding box时线的粗细
    :param pos_list: [xmin1,ymin1,xmax1,ymax1,xmin2,ymin2,xmax2,ymax2,...]，len(box_list)= 4*box数目
    :param img1: img.shape = (height, width, channel_num)
    :param color: 颜色
    :return: 绘制bounding box之后的img
    '''
    img = img1.copy()  # 复制是为了防止对参数img1本身进行绘制，影响后续结果
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    box_num = int(len(pos_list)/4)
    for i in range(box_num):
        c1, c2 = (int(pos_list[4*i]), int(pos_list[4*i+1])), (int(pos_list[4*i+2]), int(pos_list[4*i+3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if img_name is not None:
        cv2.imwrite(img_name, img)


if __name__ == '__main__':

    video_path = './inference/video/helmet1.mp4'

    video_cap = cv2.VideoCapture(video_path)
    # video_cap = get_video_stream()

    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    print('Frame width: {}, height: {}, fps: {}'.format(width, height, fps))
