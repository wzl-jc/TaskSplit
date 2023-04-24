'''
此文件用于存储各种任务各个阶段的编号，用于在应用层与切分层、切分层与调度层之间传递信息
'''
task_class_dict = {
    'FaceDetection': 0,    # 人脸检测
    'FacePoseEstimation': 1,  # 人脸姿态估计
    'HelmetDetection': 2,   # 头盔检测
    'Tracking': 3   # 目标追踪
}

task_class_dict_rev = {
    0: 'FaceDetection',    # 人脸检测
    1: 'FacePoseEstimation',  # 人脸姿态估计
    2: 'HelmetDetection',   # 头盔检测
    3: 'Tracking'   # 目标追踪
}
