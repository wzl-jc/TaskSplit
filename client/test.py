'''
Main process of client(test version).
'''
import multiprocessing as mp
import numpy as np
from TaskClassDict import task_class_dict as td


if __name__ == '__main__':
    frame = np.ones((1080, 1920, 3))
    task_list = ['FaceDetection', 'FacePoseEstimation'],  # 任务包含的子任务
    task_dag = {
        td['FacePoseEstimation']: [td['FaceDetection']]  # 子任务之间的依赖关系
    }
    task_dict = {
        'task_list': task_list,  # 子任务列表
        'task_dag': task_dag,  # 子任务之间的依赖关系
        'model_type': 0,
        'frame': frame,
        'task_split_id': 1,  # 大任务id
        'task_split_sub_id': 1  # 子任务id，第一个子任务的id为1
    }


