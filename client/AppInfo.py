import socket
import paramiko
import os
import stat
from TaskClassDict import task_class_dict as td
from TaskClassDict import task_class_dict_rev as td_rev


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


class AppInfo(object):
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.ssh_port = 22
        self.ssh_username = 'hx'
        self.ssh_password = '123456'
        self.code_local_dir = 'C:\\WorkSpace\\temptest'
        if not os.path.exists(self.code_local_dir):
            os.mkdir(self.code_local_dir)
        self.scheduler_task = None
        self.split_task = None
        self.remote_task_code_path = {}   # 任务各个阶段的代码在server端的路径
        self.local_task_code_path = {}   # 下载代码之后，任务各个阶段的代码在边缘端的路径
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((self.server_ip, self.server_port))
        print("Connect success!")
        self.getappinfo()
        self.download_task_code()
        print("Get appinfo and download code success!")

    def getappinfo(self):
        while True:
            # 调度层需要的信息
            name_len = recvall(self.sender, 4)
            name_len = int.from_bytes(name_len, byteorder='big', signed=False)
            # print(name_len)
            name_str = recvall(self.sender, name_len)
            name_str = name_str.decode('utf-8')
            # print(name_str)

            flow_step_num = recvall(self.sender, 4)
            flow_step_num = int.from_bytes(flow_step_num, byteorder='big', signed=False)
            # print(flow_step_num)
            flow_list = []
            for i in range(flow_step_num):
                flow_i_name_len = recvall(self.sender, 4)
                flow_i_name_len = int.from_bytes(flow_i_name_len, byteorder='big', signed=False)
                flow_i_name = recvall(self.sender, flow_i_name_len)
                flow_i_name = flow_i_name.decode('utf-8')
                flow_list.append({"name": flow_i_name})

            model_ctx_dict = {}
            for i in range(flow_step_num):
                step_i_name = flow_list[i]["name"]
                step_i_dict = {}
                step_i_dict_len = recvall(self.sender, 4)
                step_i_dict_len = int.from_bytes(step_i_dict_len, byteorder='big', signed=False)
                for j in range(step_i_dict_len):
                    key_len = recvall(self.sender, 4)
                    key_len = int.from_bytes(key_len, byteorder='big', signed=False)
                    key_str = recvall(self.sender, key_len)
                    key_str = key_str.decode('utf-8')

                    val_type = recvall(self.sender, 4)
                    val_type = int.from_bytes(val_type, byteorder='big', signed=False)
                    if val_type == 0:
                        val_int = recvall(self.sender, 4)
                        val_int = int.from_bytes(val_int, byteorder='big', signed=False)
                        step_i_dict[key_str] = val_int
                    elif val_type == 1:
                        float_str_len = recvall(self.sender, 4)
                        float_str_len = int.from_bytes(float_str_len, byteorder='big', signed=False)
                        float_str = recvall(self.sender, float_str_len)
                        float_str = float_str.decode('utf-8')
                        step_i_dict[key_str] = float(float_str)
                    elif val_type == 2:
                        val_str_len = recvall(self.sender, 4)
                        val_str_len = int.from_bytes(val_str_len, byteorder='big', signed=False)
                        val_str = recvall(self.sender, val_str_len)
                        val_str = val_str.decode('utf-8')
                        step_i_dict[key_str] = val_str
                    elif val_type == 3:
                        bool_int = recvall(self.sender, 4)
                        bool_int = int.from_bytes(bool_int, byteorder='big', signed=False)
                        bool_val = True if bool_int == 1 else False
                        step_i_dict[key_str] = bool_val
                model_ctx_dict[step_i_name] = step_i_dict

            input_ctx_dict = {}
            for i in range(flow_step_num + 1):
                if i == flow_step_num:
                    flow_i_name = "R"
                else:
                    flow_i_name = flow_list[i]["name"]
                input_i_list_len = recvall(self.sender, 4)
                input_i_list_len = int.from_bytes(input_i_list_len, byteorder='big', signed=False)
                input_i_list = []
                for j in range(input_i_list_len):
                    input_i_j_len = recvall(self.sender, 4)
                    input_i_j_len = int.from_bytes(input_i_j_len, byteorder='big', signed=False)
                    input_i_j = recvall(self.sender, input_i_j_len)
                    input_i_j = input_i_j.decode('utf-8')
                    input_i_list.append(input_i_j)
                input_ctx_dict[flow_i_name] = input_i_list

            output_ctx_dict = {}
            for i in range(flow_step_num + 1):
                if i == flow_step_num:
                    flow_i_name = "R"
                else:
                    flow_i_name = flow_list[i]["name"]
                output_i_list_len = recvall(self.sender, 4)
                output_i_list_len = int.from_bytes(output_i_list_len, byteorder='big', signed=False)
                output_i_list = []
                for j in range(output_i_list_len):
                    output_i_j_len = recvall(self.sender, 4)
                    output_i_j_len = int.from_bytes(output_i_j_len, byteorder='big', signed=False)
                    output_i_j = recvall(self.sender, output_i_j_len)
                    output_i_j = output_i_j.decode('utf-8')
                    output_i_list.append(output_i_j)
                output_ctx_dict[flow_i_name] = output_i_list

            self.scheduler_task = {
                "name": name_str,
                "flow": flow_list,
                "model_ctx": model_ctx_dict,
                "input_ctx": input_ctx_dict,
                "output_ctx": output_ctx_dict
            }
            print(self.scheduler_task)

            # 切分层需要的信息
            task_list = []
            task_list_len = recvall(self.sender, 4)
            task_list_len = int.from_bytes(task_list_len, byteorder='big', signed=False)
            for i in range(task_list_len):
                task_name_len = recvall(self.sender, 4)
                task_name_len = int.from_bytes(task_name_len, byteorder='big', signed=False)
                task_name = recvall(self.sender, task_name_len)
                task_name = task_name.decode('utf-8')
                task_list.append(task_name)

            task_dag = {}
            task_dag_len = recvall(self.sender, 4)
            task_dag_len = int.from_bytes(task_dag_len, byteorder='big', signed=False)
            for i in range(task_dag_len):
                task_dag_key = recvall(self.sender, 4)
                task_dag_key = int.from_bytes(task_dag_key, byteorder='big', signed=False)

                task_dag_val_list = []
                task_dag_val_list_len = recvall(self.sender, 4)
                task_dag_val_list_len = int.from_bytes(task_dag_val_list_len, byteorder='big', signed=False)
                for j in range(task_dag_val_list_len):
                    task_dag_val_j = recvall(self.sender, 4)
                    task_dag_val_j = int.from_bytes(task_dag_val_j, byteorder='big', signed=False)
                    task_dag_val_list.append(task_dag_val_j)
                task_dag[task_dag_key] = task_dag_val_list

            accuracy_str_len = recvall(self.sender, 4)
            accuracy_str_len = int.from_bytes(accuracy_str_len, byteorder='big', signed=False)
            accuracy_str = recvall(self.sender, accuracy_str_len)
            accuracy_str = accuracy_str.decode('utf-8')

            latency_str_len = recvall(self.sender, 4)
            latency_str_len = int.from_bytes(latency_str_len, byteorder='big', signed=False)
            latency_str = recvall(self.sender, latency_str_len)
            latency_str = latency_str.decode('utf-8')

            priority = recvall(self.sender, 4)
            priority = int.from_bytes(priority, byteorder='big', signed=False)

            self.split_task = {
                'app_name': name_str,
                'task_list': task_list,
                'task_dag': task_dag,
                'Accuracy': float(accuracy_str),
                'Latency': float(latency_str),
                'priority': priority
            }
            print(self.split_task)

            # 各个任务代码在服务端的路径
            for i in range(task_list_len):
                task_id = recvall(self.sender, 4)
                task_id = int.from_bytes(task_id, byteorder='big', signed=False)
                task_name = td_rev[task_id]

                task_code_path_len = recvall(self.sender, 4)
                task_code_path_len = int.from_bytes(task_code_path_len, byteorder='big', signed=False)
                task_path = recvall(self.sender, task_code_path_len)
                task_path = task_path.decode('utf-8')

                self.remote_task_code_path[task_name] = task_path
            print(self.remote_task_code_path)
            break
        print("break while!")
        self.sender.close()
        print("client close socket")

    # 递归遍历远程服务器指定目录下的所有文件
    def get_all_files_in_remote_dir(self, sftp1, remote_dir):
        all_files = list()
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
        files = sftp1.listdir_attr(remote_dir)
        for file in files:
            filename = remote_dir + '/' + file.filename
            if stat.S_ISDIR(file.st_mode):  # 如果是文件夹的话递归处理
                all_files.extend(self.get_all_files_in_remote_dir(sftp1, filename))
            else:
                all_files.append(filename)
        return all_files

    # 远程服务器上指定文件夹下载到本地文件夹
    def sftp_get_dir(self, sftp1, remote_dir, local_dir):
        try:
            all_files = self.get_all_files_in_remote_dir(sftp1, remote_dir)
            for file in all_files:
                local_filename = file.replace(remote_dir, local_dir)
                local_filepath = os.path.dirname(local_filename)
                if not os.path.exists(local_filepath):
                    os.makedirs(local_filepath)
                sftp1.get(file, local_filename)
        except:
            print('ssh get dir from master failed.')

    def download_task_code(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.server_ip, self.ssh_port, self.ssh_username, self.ssh_password)
        sftp = ssh.open_sftp()
        for task_name in self.remote_task_code_path.keys():
            task_remote_dir = self.remote_task_code_path[task_name]
            if task_remote_dir[-1] == '/':
                task_remote_dir = task_remote_dir[0:-1]
            lastdir = (task_remote_dir.split('/'))[-1]
            localdir = os.path.join(self.code_local_dir, lastdir)
            localdir = os.path.join(localdir, '')
            if not os.path.exists(localdir):
                os.mkdir(localdir)
            self.local_task_code_path[task_name] = localdir
            self.sftp_get_dir(sftp, task_remote_dir, localdir)
        print(self.local_task_code_path)
        print("Get file from server success!")
        ssh.close()

    def get_scheduler_task(self):
        return self.scheduler_task

    def get_split_task(self):
        return self.split_task

    def get_task_code_path(self):
        return self.local_task_code_path


