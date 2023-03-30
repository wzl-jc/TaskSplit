import cv2
import queue
import networkx as nx
from TaskClassDict import task_class_dict as td


class VideoStreamTaskGenerator:
    def __init__(self, task_name, video_path, task_queue, task_dag):
        self.task_name = task_name
        self.video_path = video_path
        self.task_queue = task_queue
        self.graph = nx.DiGraph(task_dag)
        print(self.graph.edges())

    def generate_task(self):
        task = {
                'task_name': self.task_name,
                'video_path': self.video_path,
                'task_dag': self.graph
        }
        self.task_queue.put(task)


# test
if __name__ == '__main__':
    video_path = 0
    task_name = "task_test"
    task_queue = queue.Queue()
    task_dag = {
        td['Preprocessing']: [],
        td['Detection']: [td['Preprocessing']],
        td['HelmetDetection']: [td['Detection']],
        td['FaceDetection']: [td['Detection']],
        td['HumanPoseEstimation']: [td['FaceDetection']],
    }
    print(task_dag)
    taskGenerator = VideoStreamTaskGenerator(task_name, video_path, task_queue, task_dag)
    taskGenerator.generate_task()
    task = task_queue.get_nowait()
