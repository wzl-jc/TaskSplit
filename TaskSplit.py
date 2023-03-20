'''
此文件进行视频任务切分
'''
import multiprocessing as mp
import threading
import numpy as np
import time
import cv2
from threading import Thread
import queue
import math
from TaskSummarizer import task_summarizer
from TaskClassDict import task_class_dict as td


def task_split_layer(q_appinfo, q_frame_app_split, q_task, q_task_res, q_frame_split_app):
    '''
    任务切分层的主进程
    Args:
        q_task_res: 接收调度层任务执行结果的队列
        q_appinfo: 接收应用信息的队列
        q_frame_app_split: 接收应用层视频帧的队列
        q_task: 向调度层传递任务的队列
        q_frame_split_app: 向应用层传递汇总后结果的队列
    Returns:
        None
    '''
    object_size = {'object_size': [50, 50]}  # 目标大小，初始化为100*100，[height, width]任务切分线程和汇总线程都会访问
    object_size_lock = threading.Lock()  # 读写object_size用到的锁

    task_recorder = {}  # 任务记录变量，用于任务切分器向任务汇总器报告任务切分的信息，以及任务切分器汇总任务执行的结果
    task_recorder_lock = threading.Lock()  # 读写task_recorder用到的锁
    # 创建一个新线程负责任务切分
    t1 = Thread(target=task_split, args=(q_appinfo, q_frame_app_split, q_task, object_size, object_size_lock,
                                         task_recorder, task_recorder_lock))  # 任务切分线程
    t1.start()
    # 进程的主线程负责任务汇总
    task_summarizer(q_task_res, q_frame_split_app, object_size, object_size_lock, task_recorder, task_recorder_lock)


def task_split(q_appinfo, q_app_frame, q_task, object_size, object_size_lock, task_recorder, task_recorder_lock):
    '''
    视频任务切分进程
    Args:
        task_recorder_lock: 读写task_recorder用到的锁
        task_recorder: 任务记录变量，用于任务切分器向任务汇总器报告任务切分的信息，以及任务切分器汇总任务执行的结果
        object_size_lock: 读写目标大小用到的锁
        object_size: 目标大小
        q_task: 任务切分层向调度层传输任务的队列
        q_app_frame: 应用层传输视频帧的队列
        q_appinfo: 接收当前应用的相关信息的队列
    Returns:
        None
    '''
    # 第一部分：接受应用层相关信息
    app_info = None
    while True:
        if not q_appinfo.empty():
            try:
                app_info = q_appinfo.get_nowait()
                break
            except queue.Empty:
                print("In application.py,exception at q_appinfo.put_nowait, try again!")
                continue
    print(app_info)

    # 第二部分：从应用层接收视频帧并生成任务
    # 冷启动
    cold_boot_num = 5  # 冷启动帧数
    task_split_id = {'task_split_id': 0}  # 标记切分后的任务id，第一个任务的id为1
    temp_dag = {
        'task_list': app_info['task_list'],
        'task_dag': app_info['task_dag']
    }
    cold_boot(q_app_frame, q_task, task_split_id, temp_dag, cold_boot_num, task_recorder,
              task_recorder_lock)
    # print(task_split_id)

    dag_root = ''
    for task_name in app_info['task_list']:
        if td[task_name] not in app_info['task_dag']:
            dag_root = task_name
            break

    if td[dag_root] == 0 or td[dag_root] == 2:  # 纯detection任务
        detection_split(app_info, dag_root, object_size, object_size_lock, q_app_frame, q_task, task_split_id, task_recorder,
                        task_recorder_lock)


def cold_boot(q_app_frame, q_task, task_split_id, app_dag, cold_boot_num, task_recorder, task_recorder_lock):
    '''
    冷启动阶段的函数
    Args:
        task_recorder_lock: 读写task_recorder用到的锁
        task_recorder: 任务记录变量，用于任务切分器向任务汇总器报告任务切分的信息，以及任务切分器汇总任务执行的结果
        q_app_frame: 接收视频帧的队列
        q_task: 传输任务的队列
        task_split_id: 切分后的任务id
        app_dag: 任务执行的DAG图
        cold_boot_num: 冷启动帧数
    Returns:
        None
    '''
    n_frame = 0
    while True:
        task_dict = {}
        if n_frame < cold_boot_num:  # 冷启动阶段一律执行detection
            if not q_app_frame.empty():
                try:
                    frame = q_app_frame.get_nowait()
                    n_frame += 1
                except:
                    continue
            else:
                continue
            # slice_size = (frame.shape[0], frame.shape[1])  # 每一帧切分成的切片大小，冷启动阶段不切分
            slice_coord = (0, 0)  # 切片的左上角坐标，用于汇总结果
            task_split_id['task_split_id'] += 1  # 更新切分任务id，第一个任务的id为1
            # 构造任务相关信息
            # task_dict['task_type'] = 'D'  # 任务类型,D:Detection,T:Tracking
            # task_dict['app_type'] = app_type  # 应用类型，用于决定使用哪一场景中的模型.与app_info['app_type']保持一致
            task_dict['task_list'] = app_dag['task_list']   # 子任务列表
            task_dict['task_dag'] = app_dag['task_dag']   # 子任务之间的依赖关系
            task_dict['model_type'] = 0  # 模型的种类,0:大模型，精度优先；1:小模型，延时优先
            task_dict['frame'] = frame  # Detection任务只有一帧
            task_dict['task_split_id'] = task_split_id['task_split_id']  # 任务id
            task_dict['task_split_sub_id'] = 1  # 一个大任务中的子任务id，这里未切分，仅有一个子任务，第一个子任务的id为1
            # task_dict['slice_size'] = slice_size
            # task_dict['slice_coord'] = slice_coord
            # 构造任务记录器相关信息
            task_recorder_dict = {
                # 'task_type': 'D',
                'frame': frame,
                'task_split_id': task_split_id['task_split_id'],  # 任务id
                'slice_coord_dict': {1: slice_coord},
                'sub_task_num': 1,  # 该任务切分为的子任务数量
                'received_task_num': 0,  # 已经接收到的子任务结果数量
                'received_obj_list': []  # 已经接收到的目标坐标
            }
            # 第一步：向任务汇总器传递新任务的信息
            while True:
                task_recorder_lock.acquire()  # 获得锁
                if len(task_recorder) < 300:  # task_recorder规模不大，则插入新任务并且释放锁
                    task_recorder[task_split_id['task_split_id']] = task_recorder_dict
                    task_recorder_lock.release()
                    # print("In cold_boot, len(task_recorder) < 300, update task_recorder!")
                    break
                else:  # task_recorder规模很大，则释放锁并且等待，直到task_recorder规模小于要求
                    task_recorder_lock.release()
                    # print("In cold_boot, len(task_recorder) > 300, sleep and wait!")
                    time.sleep(3)
            # 第二步：向调度层传递各个任务
            try:
                q_task.put(task_dict)  # 阻塞式放置任务
                # print("Put task: {}".format(task_dict['task_split_id']))
                continue
            except:
                print("In TaskSplit.py,exception at q_task.put_nowait!")
                continue
        else:
            break


def detection_split(app_info, dag_root, object_size, object_size_lock, q_app_frame, q_task, task_split_id, task_recorder,
                    task_recorder_lock):
    '''
    detection任务的切分
    Args:
        task_recorder_lock: 读写task_recorder用到的锁
        task_recorder: 任务记录变量，用于任务切分器向任务汇总器报告任务切分的信息，以及任务切分器汇总任务执行的结果
        app_info: 应用层信息，精度和时延的要求以及优先级
        dag_root: DAG图中根任务的名字
        object_size: 目标大小
        object_size_lock: 目标大小锁
        q_app_frame: 获取视频帧的队列
        q_task: 传输任务的队列
        task_split_id: 切分后的任务id
    Returns:
        None
    '''
    n_frame = 0  # 已获取的帧数
    object_size_lock.acquire()
    obj_size = object_size['object_size']  # [height, width]
    object_size_lock.release()
    nano_worker_num = 4  # nano和server端工作进程数目
    server_worker_num = 32
    worker_count = 1  # 统计工作进程的次数，用于求工作进程的平均值
    detection_model_profile = np.loadtxt('profile/detection_model_profile.csv', delimiter=',')
    cur_split_strategy = None  # 当前的切分策略
    while True:
        if not q_app_frame.empty():
            try:
                frame = q_app_frame.get_nowait()
                n_frame += 1
                if n_frame % 200 == 0:  # 每隔200帧重新确定目标大小是否有变化
                    object_size_lock.acquire()
                    obj_size = object_size['object_size']  # [height, width]
                    print("TaskSplit get obj_size {}.".format(obj_size))
                    object_size_lock.release()
            except:
                continue
            # 若当前切分策略为空，则更新detection切分策略
            if cur_split_strategy is None:
                nano_split_size = get_detection_split_size(app_info, dag_root, 0, detection_model_profile)
                server_split_size = get_detection_split_size(app_info, dag_root, 1, detection_model_profile)
                frame_shape = [frame.shape[0], frame.shape[1]]
                cur_split_strategy = get_detection_split_res(frame_shape, nano_split_size, nano_worker_num,
                                                             server_split_size, server_worker_num, obj_size)
            print("Current split strategy is {}.".format(cur_split_strategy))

            # 依据当前的切分策略对图像切分成任务
            temp_task_list = []
            slice_coord_dict = {}
            task_split_id['task_split_id'] += 1  # 更新切分任务id，第一个任务的id为1
            for i in range(cur_split_strategy['split_num']):
                x = cur_split_strategy['coord_res'][i][0]
                y = cur_split_strategy['coord_res'][i][1]
                h = cur_split_strategy['size_res'][i][0]
                w = cur_split_strategy['size_res'][i][1]
                sub_frame = frame[x:x+h, y:y+w, :]
                # print(sub_frame.shape)
                task_dict = {  # 'task_type': 'D',  # 任务类型,D:Detection,T:Tracking
                             # 'app_type': app_info['app_type'],  # 应用类型，用于决定使用哪一场景中的模型.与app_info['app_type']保持一致
                             'task_list': app_info['task_list'],  # 子任务列表
                             'task_dag': app_info['task_dag'],  # 子任务之间的依赖关系
                             'model_type': cur_split_strategy['model_type_res'][i],
                             'frame': sub_frame,
                             'task_split_id': task_split_id['task_split_id'],   # 大任务id
                             'task_split_sub_id': i+1   # 子任务id，第一个子任务的id为1
                             }
                slice_coord_dict[i+1] = (x, y)
                temp_task_list.append(task_dict)

            # 第一步：向任务汇总器传递新任务的信息
            task_recorder_dict = {
                # 'task_type': 'D',
                'frame': frame,
                'task_split_id': task_split_id['task_split_id'],  # 任务id
                'slice_coord_dict': slice_coord_dict,
                'sub_task_num': len(slice_coord_dict),  # 该任务切分为的子任务数量
                'received_task_num': 0,  # 已经接收到的子任务结果数量
                'received_obj_list': []  # 已经接收到的目标坐标
            }
            # 加锁，向任务汇总器传递新任务的信息
            while True:
                task_recorder_lock.acquire()  # 获得锁
                if len(task_recorder) < 300:  # task_recorder规模不大，则插入新任务并且释放锁
                    task_recorder[task_split_id['task_split_id']] = task_recorder_dict
                    task_recorder_lock.release()
                    # print("In detection_split, len(task_recorder) < 300, update task_recorder!")
                    break
                else:  # task_recorder规模很大，则释放锁并且等待，直到task_recorder规模小于要求
                    task_recorder_lock.release()
                    # print("In detection_split, len(task_recorder) > 300, sleep and wait!")
                    time.sleep(3)

            # 第二步：向调度层传递各个任务
            for task_dict in temp_task_list:
                try:
                    q_task.put(task_dict)  # 阻塞式放置任务
                    # print("Put task: {}".format(task_dict['task_split_id']))
                    continue
                except:
                    print("In TaskSplit.py,exception at q_task.put_nowait!")
                    continue
            # while True:
            #     pass


def get_detection_split_size(app_info, dag_root, device_type, detection_model_profile):
    '''
    根据用户对精度和时延的需求，确定在指定设备类型上进行detection切片的大小
    Args:
        app_info:应用层信息
        dag_root:根任务的名称
        device_type:设备类型
        detection_model_profile:模型知识库
    Returns:
        split_size_res['model_size']为使用的检测模型大小，0:small; 1:large
        split_size_res['split_size']为切片大小的height
    '''
    split_size_res = None
    # 遍历整个知识库，尽可能选择最合适的切片大小
    for i in range(len(detection_model_profile)):
        # 模型类型与设备类型匹配
        if detection_model_profile[i][0] == td[dag_root] and detection_model_profile[i][1] == device_type:
            # 时延优先
            # print("In get_detection_split_size, dag_root:{0}, td[dag_root]:{1}".format(dag_root, td[dag_root]))
            if app_info['priority'] == 0:
                # 寻找满足时延要求的最大的切片
                for j in range(4):
                    if detection_model_profile[i][3 + 3 * j + 2] <= app_info['Latency']:
                        split_size_res = {'model_size': detection_model_profile[i][2],
                                          'split_size': detection_model_profile[i][3 + 3 * j]}
                        break
                if split_size_res is not None:
                    break
            # 精度优先
            if app_info['priority'] == 1:
                # 寻找满足精度要求的最小的切片
                for j in range(3, -1, -1):
                    if detection_model_profile[i][3 + 3 * j + 1] >= app_info['Accuracy']:
                        split_size_res = {'model_size': detection_model_profile[i][2],
                                          'split_size': detection_model_profile[i][3 + 3 * j]}
                        break
    # 若之前的遍历未能选出最合适的切片大小，则设置为默认大小
    if split_size_res is None:
        for i in range(len(detection_model_profile)):
            if app_info['priority'] == 0:
                # 若时延优先之前未找到合适切片大小，则选择小模型并且切分为最小切片
                if detection_model_profile[i][0] == td[dag_root] \
                        and detection_model_profile[i][1] == device_type \
                        and detection_model_profile[i][2] == 0:
                    split_size_res = {'model_size': detection_model_profile[i][2],
                                      'split_size': detection_model_profile[i][3 + 3 * 3]}
                    break
            if app_info['priority'] == 1:
                # 若精度优先之前未找到合适切片大小，则选择大模型并且切分为最小切片
                if detection_model_profile[i][0] == td[dag_root] \
                        and detection_model_profile[i][1] == device_type \
                        and detection_model_profile[i][2] == 1:
                    split_size_res = {'model_size': detection_model_profile[i][2],
                                      'split_size': detection_model_profile[i][3 + 3 * 3]}
                    break
    split_size_res['model_size'] = int(split_size_res['model_size'])
    split_size_res['split_size'] = int(split_size_res['split_size'])
    return split_size_res


def gcd(x, y):
    # 求x和y的最大公因数
    if x < y:
        x, y = y, x
    if y == 0:
        return x
    else:
        return gcd(y, x % y)


def split_helper(img_size, split_size, obj_size):
    '''
    返回img_size长度按照split_size切分，物体大小为obj_size（即切片之间的重合部分大小为obj_size）时切片的数量以及各个切片的开始位置
    Args:
        img_size: 图像大小
        split_size: 切片大小
        obj_size: 物体大小
    Returns:
        res_dict['split_num']为切片数量
        res_dict['start_pos_list']为各个切片的开始位置
    '''
    res_dict = {}
    if split_size >= img_size:
        res_dict['split_num'] = 1
        res_dict['start_pos_list'] = [0]
    else:
        split_num = 0
        start_pos_list = []
        start_pos = 0
        end_pos = start_pos + split_size - 1
        while end_pos < img_size-1:
            split_num += 1
            start_pos_list.append(start_pos)
            start_pos = start_pos + split_size - obj_size
            end_pos = start_pos + split_size - 1
        # 最后添加一个以边界为结束位置的切片
        split_num += 1
        start_pos_list.append(img_size-split_size)
        res_dict['split_num'] = split_num
        res_dict['start_pos_list'] = start_pos_list
    return res_dict


def get_detection_split_res(img_shape, nano_split_size, nano_worker_num, server_split_size, server_worker_num,
                            obj_size):
    '''
    根据图像shape、nano和server端切片的大小、nano和server端工作进程的数量、目标大小确定切分策略
    Args:
        img_shape: 图像大小
        nano_split_size: nano端切片大小
        nano_worker_num: nano端工作进程数量
        server_split_size: server端切片大小
        server_worker_num: server端工作进程数量
        obj_size: 目标大小
    Returns:
        split_res = {'split_num': len(coord_res),  # 切片数量
                     'coord_res': coord_res,   # 每个切片左上角的坐标
                     'size_res': size_res,   # 每个切片的size
                     'model_type_res': model_type_res}   # 每个切片执行的模型大小
    '''
    # print(img_shape)  # [1080, 1920]
    gcd_res = gcd(img_shape[0], img_shape[1])  # 求出图像的高度、宽度比
    frame_height_percent = int(img_shape[0] / gcd_res)
    frame_width_percent = int(img_shape[1] / gcd_res)
    # print(frame_height_percent, frame_width_percent)
    # 高度和宽度按照nano_split_size、obj_size切分的结果
    nano_height_split_res = split_helper(img_shape[0], nano_split_size['split_size'], obj_size[0])
    nano_split_width = int(nano_split_size['split_size']/frame_height_percent*frame_width_percent)
    nano_width_split_res = split_helper(img_shape[1], nano_split_width, obj_size[1])
    # print(nano_height_split_res, nano_width_split_res)

    coord_res = []  # 各个切片的左上角坐标
    size_res = []  # 各个切片的大小
    model_type_res = []  # 各个切片使用的模型种类
    # 首先尽可能将nano端的切片加入结果
    if nano_height_split_res['split_num'] * nano_width_split_res['split_num'] <= nano_worker_num:
        # 若nano端切片的数量小于等于nano端工作进程的数量，说明切分的任务可以都在nano端执行，将nano切片的结果全部加入
        for i in range(nano_height_split_res['split_num']):
            for j in range(nano_width_split_res['split_num']):
                coord_res.append((nano_height_split_res['start_pos_list'][i],
                                  nano_width_split_res['start_pos_list'][j]))
                size_res.append((nano_split_size['split_size'], nano_split_width))
                model_type_res.append(nano_split_size['model_size'])
    else:
        # 若nano端切片的数量大于nano端工作进程的数量，加入尽可能多的nano端切片，其余的全为server切片
        nano_split_row = int(nano_worker_num/nano_width_split_res['split_num'])+1
        for i in range(nano_split_row):
            for j in range(nano_width_split_res['split_num']):
                coord_res.append((nano_height_split_res['start_pos_list'][i],
                                  nano_width_split_res['start_pos_list'][j]))
                size_res.append((nano_split_size['split_size'], nano_split_width))
                model_type_res.append(nano_split_size['model_size'])
        # server端切片开始的height位置
        server_height_start = nano_height_split_res['start_pos_list'][nano_split_row-1]+nano_split_size['split_size']
        server_height_start -= obj_size[0]
        server_height_start = min(server_height_start, img_shape[0]-server_split_size['split_size'])
        server_height_split_res = split_helper(img_shape[0]-server_height_start, server_split_size['split_size'],
                                               obj_size[0])
        server_split_width = int(server_split_size['split_size'] / frame_height_percent * frame_width_percent)
        server_width_split_res = split_helper(img_shape[1], server_split_width, obj_size[1])
        for i in range(server_height_split_res['split_num']):
            for j in range(server_width_split_res['split_num']):
                coord_res.append((server_height_split_res['start_pos_list'][i]+server_height_start,
                                  server_width_split_res['start_pos_list'][j]))
                size_res.append((server_split_size['split_size'], server_split_width))
                model_type_res.append(server_split_size['model_size'])
    # split_res = {'split_num': len(coord_res),
    #              'coord_res': coord_res,
    #              'size_res': size_res,
    #              'model_type_res': model_type_res}
    # 调试使用的切分策略
    split_res = {'split_num': 14,
                 'coord_res': [(0, 0), (0, 600), (0, 1200), (0, 1280), (260, 0), (260, 600), (260, 1200), (260, 1280),
                               (520, 0), (520, 813), (520, 1067), (600, 0), (600, 813), (600, 1067)],
                 'size_res': [(360, 640), (360, 640), (360, 640), (360, 640), (360, 640), (360, 640), (360, 640),
                              (360, 640), (480, 853), (480, 853), (480, 853), (480, 853), (480, 853), (480, 853)],
                 'model_type_res': [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]}
    return split_res

