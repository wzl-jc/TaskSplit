## 2023-3-19
* 应用层接口还没改成DAG图，与网页的接口还没合在一起.
* 事件检测器暂时删除，因为不允许遗漏，检测间隔很难确定（即使使用冷启动评估物体的像素级移动速度）.
* 目前仍是针对纯D或者D+T的任务进行切分，根据DAG图的切分待完善.
* 与调度层的接口待完善.

## 2023-3-20
* 应用层接口已改成DAG图.
* 事件检测器后续打算直接用帧差法，不再使用模型检测法，模型种类太多而且间隔难以确定，容易发生漏判.
