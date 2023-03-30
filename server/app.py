from flask import Flask, make_response, request, render_template, jsonify
import queue
import multiprocessing as mp
import yaml
from yaml_to_dict import yaml_to_dict
import subprocess
from TaskClassDict import task_class_dict as td

app = Flask(__name__)
task_queue = mp.Queue(maxsize=1)


@app.route('/test', methods=['GET'])
def test():
    return 'received request'


@app.route('/register')
def register():
    return render_template('register_task_beautify.html')


@app.route('/command')
def command():
    return render_template('command.html')


@app.route('/splitting-strategy')
def splitting_strategy():
    return render_template('render_splitting_strategy.html')


@app.route('/register-task-api', methods=['POST'])
def register_task_api():
    task_name = request.form.get('task-name')
    task_dag = request.files.get('task_dag')
    video_path = request.form.get('video-path')

    # task_dag_dict = yaml_to_dict(task_dag)
    task_dag_dict = None
    
    print("Task Name: " + task_name)
    print("Task DAG: " + str(task_dag_dict))
    print("Task Video Path: " + video_path)

    if check_valid(task_name, task_dag_dict, video_path):
        # task = {
        #         'task_name': task_name,
        #         'video_path': video_path,
        #         'task_dag': task_dag_dict
        # }
        task = {
            "name": "POSE_ESTIMATION",  # 工作流名称
            "flow": [  # 工作流各步骤索引和先后顺序
                {"name": "D"},
                {"name": "C"}
            ],
            "model_ctx": {  # 工作流各步骤所用模型的参数
                "D": {
                    "net_type": "mb_tiny_RFB_fd",
                    "input_size": 480,
                    "threshold": 0.7,
                    "candidate_size": 1500,
                    "device": "cpu"
                },
                "C": {
                    "lite_version": True,
                    "model_path": "models/hopenet_lite_6MB.pkl",
                    "batch_size": 1,
                    "device": "cpu"
                }
            },
            "input_ctx": {  # 工作流各步骤输入数据字段标识和顺序
                "D": ["image"],
                "C": ["image", "bbox", "prob"],
                "R": ["image", "bbox", "head_pose"]
            },
            "output_ctx": {  # 工作流各步骤输出数据字段标识和顺序
                "D": ["image", "bbox", "prob"],
                "C": ["image", "bbox", "head_pose"],
                "R": []
            },
            'task_list': ['FaceDetection', 'FacePoseEstimation'],  # 任务包含的子任务
            'task_dag': {
                td['FacePoseEstimation']: [td['FaceDetection']]  # 子任务之间的依赖关系
            },
            'Accuracy': 0.6,  # 用户对精度的要求
            'Latency': 0.5,  # 用户对时延的要求(秒)
            'priority': 0  # 0为时延优先，1为精度优先
        }
        task_queue.put(task)
        res = make_response("提交成功！")
    else:
        res = make_response("提交失败！")
    res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res


@app.route('/command-api', methods=['POST'])
def command_api():
    cmd = request.form.get('command')
    print(cmd)
    # 获取命令的输出
    try:
        cmdlist = cmd.split()
        output = subprocess.check_output(cmdlist)
        print(output.decode('utf-8'))
        return output.decode('utf-8')
    except:
        return "An error occured."   


@app.route('/get_splitting_strategy')
def get_splitting_strategy():
    # simulate getting data from the API
    split_res = {  
        'frame_size': (1080, 1920),
        'split_num': 14,
        'coord_res': [(0, 0), (0, 600), (0, 1200), (0, 1280), (260, 0), (260, 600), (260, 1200), (260, 1280),
                      (520, 0), (520, 813), (520, 1067), (600, 0), (600, 813), (600, 1067)],
        'size_res': [(360, 640), (360, 640), (360, 640), (360, 640), (360, 640), (360, 640), (360, 640),
                     (360, 640), (480, 853), (480, 853), (480, 853), (480, 853), (480, 853), (480, 853)],
        'model_type_res': [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
        }
    return jsonify(split_res)


def check_valid(task_name, dag_file, video_stream):
    return True


def app_func(q_app_info):
    global task_queue
    task_queue = q_app_info
    app.run(port=5502)

