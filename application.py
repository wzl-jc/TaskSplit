'''
此文件用于模拟上层应用
'''
from threading import Thread
import cv2
import time
from TaskClassDict import task_class_dict as td


def video_app(q_appinfo, q_frame_app_split, q_frame_split_app):
    t1 = Thread(target=app2split, args=(q_appinfo, q_frame_app_split))  # 向任务切分层传输数据的线程
    t1.start()

    # 主线程充当接收任务切分层结果的线程
    split2app(q_frame_split_app)


def app2split(q_appinfo, q_frame):
    '''
    负责向任务切分层次传输当前应用的相关信息和视频流
    Args:
        q_appinfo: 传输当前应用的相关信息的队列
        q_frame: 传输视频流的队列
    Returns:
        None
    '''
    time.sleep(3)
    # 第一部分：获取应用层信息并传递给任务切分层
    # app_info = {
    #     'app_name': 'face-recognition',   # 应用名
    #     'app_type': 0,                    # 应用类型,例如人脸检测、行人检测等,用于决定使用哪一场景中的模型.0:人脸检测
    #     'app_mode': 0,                    # 应用运行模式, 0:Detection；1:Detection+Tracking
    #     'Detection-mode': 0,              # 应用进行Detection时使用的模型是单阶段还是两阶段,0:单阶段；1:两阶段
    #     'Accuracy': 0.6,                 # 用户对精度的要求
    #     'Latency': 0.5,                   # 用户对时延的要求(秒)
    #     'priority': 0                     # 0为时延优先，1为精度优先
    # }
    app_info = {
        'app_name': 'face-recognition',  # 应用名
        'task_list': ['FaceDetection', 'FacePoseEstimation'],  # 任务包含的子任务
        'task_dag': {
            td['FacePoseEstimation']: [td['FaceDetection']]   # 子任务之间的依赖关系
        },
        'Accuracy': 0.6,                 # 用户对精度的要求
        'Latency': 0.5,                  # 用户对时延的要求(秒)
        'priority': 0                    # 0为时延优先，1为精度优先
    }

    while True:  # 向q_appinfo中放置应用信息，放置成功则跳出死循环，否则继续尝试
        try:
            q_appinfo.put_nowait(app_info)
            break
        except:
            print("In application.py,exception at q_appinfo.put_nowait, try again!")
            continue
    print("In application.py,q_appinfo.put_nowait success!")

    # 第二部分：向切分层传递视频流
    #  设置视频路径并读取帧
    video_path = 'inference/video/人少--人多.mp4'

    # read frame from video
    video_cap = cv2.VideoCapture(video_path)
    img_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    print('Frame width: {}, height: {}, fps: {}'.format(img_width, img_height, fps))
    ret, frame = video_cap.read()
    print(type(frame))
    print(frame.shape)
    # cv2.imwrite("0.jpg", frame)
    n_frame = 0
    while ret:
        try:
            q_frame.put(frame, block=True)   # 放置图像到队列中，阻塞式
        except:
            continue
        n_frame += 1
        # print("app2split put {} frames".format(n_frame))
        ret, frame = video_cap.read()
    # print("Frame num is {}.".format(n_frame))


def split2app(q_frame_split_app):
    '''
    负责接收任务切分层汇总后的结果（目前为图像）
    Args:
        q_frame_split_app: 任务层向切分层传递视频帧的队列
    Returns:
        None
    '''
    count = 0
    while True:
        if not q_frame_split_app.empty():
            try:
                app_res = q_frame_split_app.get_nowait()
                count += 1
                print("video_app get frame {} result {}.".format(count, app_res['obj_coord_array'].shape))
            except:
                continue