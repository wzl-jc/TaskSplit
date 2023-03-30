'''
此文件为云端和边缘端通信的文件
'''
from threading import Thread
import multiprocessing as mp
import socket
from TaskClassDict import task_class_dict as td


def recvall(sock, n):
    """
    :param sock:
    :param n: number of bytes to be received
    :return: received bytes
    """
    buf = b''
    while n:
        newbuf = sock.recv(n)
        if not newbuf:
            return None
        buf += newbuf
        n -= len(newbuf)
    return buf


def send_app_info(sock, app_info):
    '''
    将app_info(python字典类型)序列化，通过sock发送至边缘端
    :param sock: socket
    :param app_info: 任务信息
    :return:
    '''
    # 发送工作流名称
    name_len = len(app_info["name"])
    name_len_bytes = name_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(name_len_bytes)
    sock.sendall(app_info["name"].encode('utf-8'))

    # 发送工作流各步骤索引和先后顺序
    flow_step_num = len(app_info["flow"])
    flow_step_num_bytes = flow_step_num.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(flow_step_num_bytes)
    for i in range(flow_step_num):
        step_i_len = len(app_info["flow"][i]["name"])
        step_i_len_bytes = step_i_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(step_i_len_bytes)
        sock.sendall(app_info["flow"][i]["name"].encode('utf-8'))

    # 发送工作流各步骤所用模型的参数
    model_ctx = app_info["model_ctx"]
    for i in range(flow_step_num):
        step_i_name = app_info["flow"][i]["name"]
        model_ctx_i = model_ctx[step_i_name]
        model_ctx_i_len = len(model_ctx_i)
        model_ctx_i_len_bytes = model_ctx_i_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(model_ctx_i_len_bytes)
        # 按键值对的形式传递
        for key in model_ctx_i.keys():
            key_len = len(key)
            key_len_bytes = key_len.to_bytes(length=4, byteorder='big', signed=False)
            sock.sendall(key_len_bytes)
            sock.sendall(key.encode('utf-8'))

            val = model_ctx_i[key]
            if isinstance(val, int):
                val_type = 0   # 表示val类型的数字
                val_type_bytes = val_type.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_type_bytes)
                val_bytes = val.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_bytes)
            elif isinstance(val, float):
                val_type = 1
                val_type_bytes = val_type.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_type_bytes)
                val_str = str(val)
                val_str_len = len(val_str)
                val_str_len_bytes = val_str_len.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_str_len_bytes)
                sock.sendall(val_str.encode('utf-8'))
            elif isinstance(val, str):
                val_type = 2
                val_type_bytes = val_type.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_type_bytes)
                val_str_len = len(val)
                val_str_len_bytes = val_str_len.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_str_len_bytes)
                sock.sendall(val.encode('utf-8'))
            elif isinstance(val, bool):
                val_type = 3
                val_type_bytes = val_type.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_type_bytes)
                val_int = 1 if val else 0
                val_int_bytes = val_int.to_bytes(length=4, byteorder='big', signed=False)
                sock.sendall(val_int_bytes)

    # 工作流各步骤输入数据字段标识和顺序
    input_ctx = app_info["input_ctx"]
    for i in range(flow_step_num):
        step_i_name = app_info["flow"][i]["name"]
        temp_list = input_ctx[step_i_name]
        temp_list_len = len(temp_list)
        temp_list_len_bytes = temp_list_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(temp_list_len_bytes)
        for j in range(temp_list_len):
            input_j_len = len(temp_list[j])
            input_j_len_bytes = input_j_len.to_bytes(length=4, byteorder='big', signed=False)
            sock.sendall(input_j_len_bytes)
            sock.sendall(temp_list[j].encode('utf-8'))
    res_name = "R"
    temp_list = input_ctx[res_name]
    temp_list_len = len(temp_list)
    temp_list_len_bytes = temp_list_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(temp_list_len_bytes)
    for i in range(temp_list_len):
        res_i_len = len(temp_list[i])
        res_i_len_bytes = res_i_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(res_i_len_bytes)
        sock.sendall(temp_list[i].encode('utf-8'))

    # 工作流各步骤输出数据字段标识和顺序
    output_ctx = app_info["output_ctx"]
    for i in range(flow_step_num):
        step_i_name = app_info["flow"][i]["name"]
        temp_list = output_ctx[step_i_name]
        temp_list_len = len(temp_list)
        temp_list_len_bytes = temp_list_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(temp_list_len_bytes)
        for j in range(temp_list_len):
            output_j_len = len(temp_list[j])
            output_j_len_bytes = output_j_len.to_bytes(length=4, byteorder='big', signed=False)
            sock.sendall(output_j_len_bytes)
            sock.sendall(temp_list[j].encode('utf-8'))
    res_name = "R"
    temp_list = output_ctx[res_name]
    temp_list_len = len(temp_list)
    temp_list_len_bytes = temp_list_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(temp_list_len_bytes)
    for i in range(temp_list_len):
        res_i_len = len(temp_list[i])
        res_i_len_bytes = res_i_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(res_i_len_bytes)
        sock.sendall(temp_list[i].encode('utf-8'))

    # 传输task_list
    task_list = app_info['task_list']
    task_list_len = len(task_list)
    task_list_len_bytes = task_list_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(task_list_len_bytes)
    for task_name in task_list:
        task_name_len = len(task_name)
        task_name_len_bytes = task_name_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(task_name_len_bytes)
        sock.sendall(task_name.encode('utf-8'))

    # 传输task_dag
    task_dag = app_info['task_dag']
    task_dag_len = len(task_dag)
    task_dag_len_bytes = task_dag_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(task_dag_len_bytes)
    for dag_key in task_dag.keys():
        dag_key_bytes = dag_key.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(dag_key_bytes)

        dag_val_list = task_dag[dag_key]
        dag_val_list_len = len(dag_val_list)
        dag_val_list_len_bytes = dag_val_list_len.to_bytes(length=4, byteorder='big', signed=False)
        sock.sendall(dag_val_list_len_bytes)

        for dag_val_i in dag_val_list:
            dag_val_i_bytes = dag_val_i.to_bytes(length=4, byteorder='big', signed=False)
            sock.sendall(dag_val_i_bytes)

    # 传输精度、时延、优先级
    accuracy = app_info['Accuracy']
    accuracy_str = str(accuracy)
    accuracy_str_len = len(accuracy_str)
    accuracy_str_len_bytes = accuracy_str_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(accuracy_str_len_bytes)
    sock.sendall(accuracy_str.encode('utf-8'))

    latency = app_info['Latency']
    latency_str = str(latency)
    latency_str_len = len(latency_str)
    latency_str_len_bytes = latency_str_len.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(latency_str_len_bytes)
    sock.sendall(latency_str.encode('utf-8'))

    priority = app_info['priority']
    priority_bytes = priority.to_bytes(length=4, byteorder='big', signed=False)
    sock.sendall(priority_bytes)


def communicate(q_app_info, ip, port):
    '''
    云端和边缘端通信的进程
    :param port: 服务端监听的端口号
    :param ip: 服务端监听的ip
    :param q_app_info: 获取用户从web界面提交任务的队列
    :return:
    '''
    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver.bind((ip, port))
    receiver.listen(1)
    while True:
        conn, addr = receiver.accept()
        print('Connected by:{}'.format(addr))
        task = q_app_info.get()
        print("get task!")
        send_app_info(conn, task)
        print("send success!")
        conn.close()
        print("conn close")
        break
    receiver.close()
    print("receiver close")



