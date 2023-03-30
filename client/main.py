'''
此文件为边缘端整个系统的入口，用于启动系统中的各个进程
'''
import multiprocessing as mp
from application import video_app
from TaskSplit import task_split_layer
from video_helper import *
import os
import numpy as np

if __name__ == '__main__':
    # args = parse_args()
    q_appinfo = mp.Queue(maxsize=1)  # 应用层向任务切分层传递应用信息的队列
    q_frame_app_split = mp.Queue(maxsize=1)  # 应用层向任务切分层传递视频帧的队列
    q_frame_split_app = mp.Queue(maxsize=1)  # 应用层接收任务切分层汇总结果的队列
    q_task = mp.Queue(maxsize=1)  # 任务切分层向调度层传递任务的队列
    q_task_res = mp.Queue(maxsize=1)  # 调度层向任务切分层传递任务执行结果的队列

    p_app = mp.Process(target=video_app, args=(q_appinfo, q_frame_app_split, q_frame_split_app))  # 应用层进程
    # 任务切分进程
    p_task_split = mp.Process(target=task_split_layer, args=(q_appinfo, q_frame_app_split,
                                                             q_task, q_task_res, q_frame_split_app))
    p_app.start()
    p_task_split.start()

    # 模拟调度层和执行层，接收到任务之后返回随机结果
    while True:
        if not q_task.empty():
            try:
                task = q_task.get_nowait()
                # print("Get task:{}.{}".format(task['task_split_id'], task['task_split_sub_id']))
            except:
                continue
        else:
            continue
        # 检测到的目标坐标列表，列表每一个元素都是一个元组，元组第一个元素为左上角坐标，第二个元素为右下角坐标
        res_obj_coord_array = np.array([[0, 0, 200, 200],
                                        [100, 100, 210, 210]])
        res_dict = {  # 'task_type': task['task_type'],  # 任务类型,D:Detection,T:Tracking
                    #  'app_type': task['app_type'],  # 应用类型，用于决定使用哪一场景中的模型.与app_info['app_type']保持一致
                    'model_type': task['model_type'],
                    'frame': task['frame'],
                    'task_split_id': task['task_split_id'],  # 大任务id
                    'task_split_sub_id': task['task_split_sub_id'],  # 子任务id，第一个子任务的id为1
                    'obj_coord_array': res_obj_coord_array  # 检测到的目标坐标数组
                    }
        try:
            q_task_res.put(res_dict)  # 阻塞式放置任务结果
            # print("Put task result: {}".format(res_dict['task_split_id']))
            continue
        except:
            print("In TaskSplit.py,exception at q_task.put_nowait!")
            continue
    # 主进程充当调度进程，负责从切分层接收任务、分发给各个节点执行、收集执行结果
    # while True:
    #     task = None
    #     if not q_task.empty():
    #         try:
    #             task = q_task.get_nowait()
    #         except:
    #             continue
    #     else:
    #         continue
    #     # print(task['task_type'])
    #     # 每收到一个任务才创建执行进程池
    #     process_num = os.cpu_count() - 4 if os.cpu_count() - 4 > 0 else 1  # 当前设备工作进程的数量
    #     print("Task process pool size:{}".format(process_num))
    #     po = mp.Pool(process_num)
    #     task_res = []
    #     if task['task_type'] == 'D':  # Detection类任务
    #         frame = task['frame']
    #         slice_size = task['slice_size']
    #         slice_coord_list = task['slice_coord_list']
    #         if task['app_type'] == 0:  # 人脸检测
    #             if task['model_type'] == 0:  # 精度优先
    #                 for coord in slice_coord_list:
    #                     # print(coord)
    #                     temp_task_res = po.apply_async(facedetection,
    #                                                    args=(args, frame, coord, slice_size))
    #                     task_res.append(temp_task_res)
    #
    #     # 关闭进程池，等待各个进程的执行结果并汇总
    #     po.close()
    #     po.join()
    #     task_res_dict = {}
    #     for i in range(len(task_res)):
    #         task_res[i] = task_res[i].get()
    #         # print(type(task_res[i]))
    #     if task['task_type'] == 'D':
    #         task_res_dict['task_type'] = 'D'
    #         task_res_dict['frame_num'] = 1
    #         task_res_dict['frame'] = task['frame']
    #         boxes_list = []  # 存放boundingbox坐标
    #         for i in range(len(task_res)):
    #             boxes = task_res[i]['boxes']
    #             # print(type(boxes))
    #             boxes = boxes.numpy()
    #             # print(type(boxes), boxes.shape)
    #             x, y = task_res[i]['coord']
    #             for j in range(boxes.shape[0]):
    #                 boxes_list.append(int(x + boxes[j][0]))
    #                 boxes_list.append(int(y + boxes[j][1]))
    #                 boxes_list.append(int(x + boxes[j][2]))
    #                 boxes_list.append(int(y + boxes[j][3]))
    #         boxes_list = bounding_box_deduplication(boxes_list)
    #         boxes_num = int(len(boxes_list) / 4)
    #         boxes_array = np.array(boxes_list)  # 从list转为数组
    #         boxes_array.resize((boxes_num, 4))
    #         task_res_dict['boxes'] = boxes_array
    #         # print(boxes_array)
    #     try:
    #         q_task_res.put(task_res_dict, block=True, timeout=2)
    #     except:
    #         pass







