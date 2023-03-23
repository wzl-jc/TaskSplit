'''
此文件进行视频任务结果汇总
'''
import multiprocessing as mp
import threading
import numpy as np
import time
import cv2
from threading import Thread
import queue
import math


def task_summarizer(q_task_res, q_frame_split_app, object_size, object_size_lock, task_recorder, task_recorder_lock):
    '''
    任务汇总器方法
    Args:
        q_task_res: 接收调度层任务执行结果的队列
        q_frame_split_app: 向应用层传递汇总后结果的队列
        object_size: 目标大小
        object_size_lock: 读写object_size用到的锁
        task_recorder: 任务记录变量
        task_recorder_lock: 读写task_recorder用到的锁
    Returns:
        None
    '''
    local_obj_size = [50, 50]  # 与函数task_split_layer中的初始值保持一致，用于本地记录目标大小的变化
    task_num = 0
    while True:
        if not q_task_res.empty():
            try:
                task_res = q_task_res.get_nowait()
                task_num += 1
            except queue.Empty:
                print("In TaskSummarizer.py,exception at q_task_res.get_nowait, try again!")
                continue
            task_id = task_res['task_split_id']
            task_sub_id = task_res['task_split_sub_id']

            # 在task_recorder中汇总任务执行结果
            task_recorder_lock.acquire()   # 获得锁
            for i in range(task_res['obj_coord_array'].shape[0]):  # 将当前任务检测到的目标坐标转换之后记录
                # 当前切片左上角在图像中的x,y坐标，注意进行转换
                temp_sub_task_x = task_recorder[task_id]['slice_coord_dict'][task_sub_id][1]
                temp_sub_task_y = task_recorder[task_id]['slice_coord_dict'][task_sub_id][0]
                temp_x_min = int(task_res['obj_coord_array'][i][0]) + temp_sub_task_x
                task_recorder[task_id]['received_obj_list'].append(temp_x_min)
                temp_y_min = int(task_res['obj_coord_array'][i][1]) + temp_sub_task_y
                task_recorder[task_id]['received_obj_list'].append(temp_y_min)
                temp_x_max = int(task_res['obj_coord_array'][i][2]) + temp_sub_task_x
                task_recorder[task_id]['received_obj_list'].append(temp_x_max)
                temp_y_max = int(task_res['obj_coord_array'][i][3]) + temp_sub_task_y
                task_recorder[task_id]['received_obj_list'].append(temp_y_max)
                # 更新本地的local_obj_size变量
                temp_obj_height = int(math.ceil((temp_y_max-temp_y_min)/10))*10
                local_obj_size[0] = max(local_obj_size[0], temp_obj_height)
                temp_obj_width = int(math.ceil((temp_x_max-temp_x_min)/10))*10
                local_obj_size[1] = max(local_obj_size[1], temp_obj_width)
            # task_id任务接收到的子任务结果数量++
            task_recorder[task_id]['received_task_num'] += 1
            if task_recorder[task_id]['received_task_num'] == task_recorder[task_id]['sub_task_num']:
                # 若task_id任务接收到了所有的子任务结果，则汇总结果并传递给应用层
                # 对各个切片的bbox结果去重
                # print(int(len(task_recorder[task_id]['received_obj_list'])/4))
                task_recorder[task_id]['received_obj_list'] = bounding_box_deduplication(task_recorder[task_id]
                                                                                         ['received_obj_list'])
                # print(int(len(task_recorder[task_id]['received_obj_list']) / 4))
                obj_coord_array = np.array(task_recorder[task_id]['received_obj_list'])
                obj_coord_array = obj_coord_array.reshape((-1, 4))
                app_res = {'frame': task_recorder[task_id]['frame'],
                           'obj_coord_array': obj_coord_array}

                del task_recorder[task_id]  # task_id任务的结果已经完成汇总，将其从task_recorder中删除
                task_recorder_lock.release()  # 释放锁
                while True:  # 向q_appinfo中放置应用信息，放置成功则跳出死循环，否则继续尝试
                    try:
                        q_frame_split_app.put_nowait(app_res)
                        break
                    except:
                        print("In TaskSummarizer.py,exception at q_frame_split_app.put_nowait, try again!")
                        continue
            else:
                task_recorder_lock.release()  # 释放锁
            if task_num % 89 == 0:   # 每收到89个任务的结果，更新一次object_size
                object_size_lock.acquire()
                object_size['object_size'][0] = max(object_size['object_size'][0], local_obj_size[0])
                object_size['object_size'][1] = max(object_size['object_size'][1], local_obj_size[1])
                print("TaskSummarizer modify obj_size {}.".format(object_size['object_size']))
                object_size_lock.release()


def cal_iou(box1, box2):
    """
    :param box1: = [xmin1, ymin1, xmax1, ymax1]
    :param box2: = [xmin2, ymin2, xmax2, ymax2]
    :return:
    """
    xmin1, ymin1, xmax1, ymax1 = box1
    xmin2, ymin2, xmax2, ymax2 = box2
    # 计算每个矩形的面积
    s1 = (xmax1 - xmin1) * (ymax1 - ymin1)  # b1的面积
    s2 = (xmax2 - xmin2) * (ymax2 - ymin2)  # b2的面积

    # 计算相交矩形
    xmin = max(xmin1, xmin2)
    ymin = max(ymin1, ymin2)
    xmax = min(xmax1, xmax2)
    ymax = min(ymax1, ymax2)

    w = max(0, xmax - xmin)
    h = max(0, ymax - ymin)
    a1 = w * h  # C∩G的面积
    a2 = s1 + s2 - a1
    iou = a1 / a2  # iou = a1/ (s1 + s2 - a1)
    return iou


def cal_intersection(box1, box2):
    """
    计算box1和box2的相交部分面积占box1和box2的比例
    :param box1: = [xmin1, ymin1, xmax1, ymax1]
    :param box2: = [xmin2, ymin2, xmax2, ymax2]
    :return:
    """
    xmin1, ymin1, xmax1, ymax1 = box1
    xmin2, ymin2, xmax2, ymax2 = box2
    # 计算每个矩形的面积
    s1 = (xmax1 - xmin1) * (ymax1 - ymin1)  # b1的面积
    s2 = (xmax2 - xmin2) * (ymax2 - ymin2)  # b2的面积

    # 计算相交矩形
    xmin = max(xmin1, xmin2)
    ymin = max(ymin1, ymin2)
    xmax = min(xmax1, xmax2)
    ymax = min(ymax1, ymax2)

    w = max(0, xmax - xmin)
    h = max(0, ymax - ymin)
    a1 = w * h  # C∩G的面积
    return a1 / s1, a1 / s2


def bounding_box_deduplication(box_list, iou_threshold=0.5, intersect_threshold=0.6):
    '''
    对bounding box去重包括两步：1.利用IOU去重，这一步重点解决同一个目标在不同的切片都被识别出，且不同的切片包含有该目标的大部分；
    2.利用相交部分面积占自己面积的百分比去重，这一步重点解决一个目标在不同的切片都被识别出，但一个切片包含完整的目标，另一个切片只包含
    目标的一小部分，此时只利用IOU很难去重，因为相交部分面积很小，IOU的阈值也不能降到特别低否则会造成不同目标之间被错误去重，因此考虑利用
    相交部分面积占自己面积的百分比去重，这一步就可以解决一个切片只包含目标的一小部分且被识别时的去重情况.
    注意：切分+overlap(overlap大小至少为目标大小)的方式可以保证对于任意一个目标，其一定在某一个切片内被完整的识别
    :param intersect_threshold: 相交部分面积占自己面积的百分比阈值
    :param iou_threshold: IoU去重的阈值
    :param box_list: [xmin1,ymin1,xmax1,ymax1,xmin2,ymin2,xmax2,ymax2,...]，len(box_list)= 4*box数目
    :return: 去重之后的bounding box坐标
    '''
    box_num = int(len(box_list) / 4)  # bounding box数量

    # 第一步：利用IOU去重
    while True:
        if_dup = False  # 记录本轮迭代是否进行了去重
        for i in range(box_num - 1):
            if box_list[4 * i] != -1:
                for j in range(i + 1, box_num):
                    if box_list[4 * j] != -1:
                        temp_iou = cal_iou(
                            [box_list[4 * i], box_list[4 * i + 1], box_list[4 * i + 2], box_list[4 * i + 3]],
                            [box_list[4 * j], box_list[4 * j + 1], box_list[4 * j + 2], box_list[4 * j + 3]])
                        if temp_iou > iou_threshold:
                            if_dup = True  # iou大于阈值，进行去重
                            dup_index = -1  # 要去除的bounding box索引
                            # 保留两个bounding box中面积更大的一个
                            area_i = (box_list[4 * i + 2] - box_list[4 * i]) * (
                                        box_list[4 * i + 3] - box_list[4 * i + 1])
                            area_j = (box_list[4 * j + 2] - box_list[4 * j]) * (
                                        box_list[4 * j + 3] - box_list[4 * j + 1])
                            if area_i < area_j:
                                dup_index = i
                            else:
                                dup_index = j
                            box_list[4 * dup_index] = -1  # 把要去除的bounding box坐标赋为-1
                            box_list[4 * dup_index + 1] = -1
                            box_list[4 * dup_index + 2] = -1
                            box_list[4 * dup_index + 3] = -1
                            break
                if if_dup:
                    break
        if not if_dup:
            break

    # 第二步：利用相交部分面积占自己面积的百分比去重
    while True:
        if_dup = False  # 记录本轮迭代是否进行了去重
        for i in range(box_num - 1):
            if box_list[4 * i] != -1:
                for j in range(i + 1, box_num):
                    if box_list[4 * j] != -1:
                        p1, p2 = cal_intersection(
                            [box_list[4 * i], box_list[4 * i + 1], box_list[4 * i + 2], box_list[4 * i + 3]],
                            [box_list[4 * j], box_list[4 * j + 1], box_list[4 * j + 2], box_list[4 * j + 3]])
                        if p1 > intersect_threshold:
                            if_dup = True  # p1大于阈值，进行去重
                            box_list[4 * i] = -1  # 把要去除的bounding box坐标赋为-1
                            box_list[4 * i + 1] = -1
                            box_list[4 * i + 2] = -1
                            box_list[4 * i + 3] = -1
                            break
                        elif p2 > intersect_threshold:
                            if_dup = True  # p2大于阈值，进行去重
                            box_list[4 * j] = -1  # 把要去除的bounding box坐标赋为-1
                            box_list[4 * j + 1] = -1
                            box_list[4 * j + 2] = -1
                            box_list[4 * j + 3] = -1
                            break

                if if_dup:
                    break
        if not if_dup:
            break

    # 整理去重后的结果，去除值为-1的坐标
    res_list = []
    for i in range(len(box_list)):
        if box_list[i] != -1:
            res_list.append(box_list[i])
    return res_list


