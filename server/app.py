from flask import Flask, make_response, request, render_template, jsonify, send_from_directory
import queue
import json
import yaml
from yaml_to_dict import yaml_to_dict
import subprocess
import zipfile
import multiprocessing as mp

app = Flask(__name__)
task_queue = mp.Queue(maxsize=1)
# server_codebase = '/Users/wenyidai/GitHub/video_analytics_applayer/tempfiles/'
server_codebase = 'C:\\WorkSpace\\test\\'


@app.route("/edit-json")
def editjson():
    return render_template('edit_json.html')


# 路由到dist目录
@app.route("/dist/<path:path>")
def send_dist(path):
    return send_from_directory("dist", path)


# 路由到images目录
@app.route("/images/<path:path>")
def send_images(path):
    return send_from_directory("images", path)


@app.route('/test', methods=['GET'])
def test():
    return 'received request'

# @app.route('/submit-json')
# def submit_json():
#     return render_template('submit_task_json.html')


@app.route('/register')
def register():
    return render_template('register_task_beautify.html')


@app.route('/command')
def command():
    return render_template('command.html')


@app.route('/splitting-strategy')
def splitting_strategy():
    return render_template('render_splitting_strategy.html')


@app.route('/upload-json-and-codefiles-api', methods=['POST'])
def upload_json_and_codefiles_api():
    try:
        received_files = request.files
        task_json = received_files.get('task_json')
        task_dict = json.load(task_json)

        for file in received_files:
            if file == 'task_json':
                continue
            save_path = server_codebase + file + '.zip'
            received_files[file].save(save_path)
            with zipfile.ZipFile(save_path, 'r') as zip_ref:
                zip_ref.extractall(server_codebase + file)
            # delete the zip file
            # subprocess.call(['rm', save_path])
            task_dict['task_code_path'][file] = server_codebase + file

        # print(task_dict)
        task_queue.put(task_dict)

        res = make_response("提交成功！")
        res.status = '200'  # 设置状态码
        res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
        res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        return res
    
    except:
        res = make_response("提交失败！")
        res.status = '200'
        res.headers['Access-Control-Allow-Origin'] = "*"
        res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        return res


@app.route('/submit-json-api', methods=['POST'])
def submit_json_api():
    task_json = request.files.get('file')
    task_dict = json.load(task_json)
    print(task_dict)
    task_queue.put(task_dict)
    res = make_response("提交成功！")
    res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res


@app.route('/upload-codefiles-api', methods=['POST'])
def upload_codefiles_api():
    received_files = request.files
    for file in received_files:
        save_path = server_codebase + file + '.zip'
        received_files[file].save(save_path)
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(server_codebase + file)

    res = make_response("提交成功！")
    res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res


@app.route('/register-task-api', methods=['POST'])
def register_task_api():
    task_name = request.form.get('task-name')
    task_dag = request.files.get('task_dag')
    video_path = request.form.get('video-path')

    task_dag_dict = yaml_to_dict(task_dag)
    
    print("Task Name: " + task_name)
    print("Task DAG: " + str(task_dag_dict))
    print("Task Video Path: " + video_path)

    if(check_valid(task_name, task_dag_dict, video_path)):
        task = {
                'task_name' : task_name,
                'video_path' : video_path,
                'task_dag' : task_dag_dict
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


if __name__ == '__main__':
    app.run(port=5502)

