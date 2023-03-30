import socket


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
        self.scheduler_task = None
        self.split_task = None
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((self.server_ip, self.server_port))
        print("Connect success!")
        self.getappinfo()

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
            break
        print("break while!")
        self.sender.close()
        print("client close socket")

    def get_scheduler_task(self):
        return self.scheduler_task

    def get_split_task(self):
        return self.split_task


