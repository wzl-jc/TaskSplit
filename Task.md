### 任务切分层与调度层之间传递的任务说明：
任务的数据类型：python中的字典，共以下几个字段
* 'task_list'：任务中包含的子任务列表（字符串列表），例如['FaceDetection', 'FacePoseEstimation']
* 'task_dag'：各个子任务之间的依赖关系，为字典类型，字典的key是一个整型数（表示子任务的编号），value是一个整型数列表（表示该任务依赖的所有子任务的编号）。例如：
```python
from TaskClassDict import task_class_dict as td
task_dag = {
     td['FacePoseEstimation']: [td['FaceDetection']]  # 子任务之间的依赖关系
}
```
上面这个例子表示：任务'FacePoseEstimation'只依赖于任务'FaceDetection'的执行结果，需要在其后执行。
而任务'FaceDetection'没有作为key在字典中出现，表示它的执行不依赖于任何任务。

各类子任务的字符串名与数字编号之间的对应关系见TaskClassDict.py。
* 'model_type'：任务中使用的模型的大小，整型值。0表示大模型，1表示小模型。
* 'frame'：视频帧，shape为(x,y,3)的数组。例如frame = np.ones((1080, 1920, 3)).
* 'task_split_id'：任务id，整型数。由任务切分层维护，用于实现任务汇总，最终需要连同任务执行的结果返回给任务切分层。例如整数 1.
* 'task_split_sub_id'：切分后的任务id，整型数。由任务切分层维护，用于实现任务汇总，最终需要连同任务执行的结果返回给任务切分层。例如整数 1.

测试时生成任务的代码如下：
```python
from TaskClassDict import task_class_dict as td
import numpy as np

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
```