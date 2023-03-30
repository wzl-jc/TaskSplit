'''
Main process of client(test version).
'''
import multiprocessing as mp
import numpy as np
from TaskClassDict import task_class_dict as td
import socket
from AppInfo import AppInfo
from AppInfo import recvall
from TaskGenerator import TaskGenerator


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 5004
    a = AppInfo(ip, port)
    print(a.get_scheduler_task())
    print(a.get_split_task())
    b = TaskGenerator(a.get_split_task(), a.get_scheduler_task())
    frame = np.ones((1080, 1920, 3))
    print(b.get_task_list(frame))
    # sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sender.connect((ip, port))
    # while True:
    #     name_len = recvall(sender, 4)
    #     name_len = int.from_bytes(name_len, byteorder='big', signed=False)
    #     print(name_len)
    #     name_str = recvall(sender, name_len)
    #     name_str = name_str.decode('utf-8')
    #     print(name_str)
    #
    #     flow_step_num = recvall(sender, 4)
    #     flow_step_num = int.from_bytes(flow_step_num, byteorder='big', signed=False)
    #     print(flow_step_num)
    #     flow_list = []
    #     for i in range(flow_step_num):
    #         flow_i_name_len = recvall(sender, 4)
    #         flow_i_name_len = int.from_bytes(flow_i_name_len, byteorder='big', signed=False)
    #         flow_i_name = recvall(sender, flow_i_name_len)
    #         flow_i_name = flow_i_name.decode('utf-8')
    #         flow_list.append({"name": flow_i_name})
    #
    #     model_ctx_dict = {}
    #     for i in range(flow_step_num):
    #         step_i_name = flow_list[i]["name"]
    #         step_i_dict = {}
    #         step_i_dict_len = recvall(sender, 4)
    #         step_i_dict_len = int.from_bytes(step_i_dict_len, byteorder='big', signed=False)
    #         for j in range(step_i_dict_len):
    #             key_len = recvall(sender, 4)
    #             key_len = int.from_bytes(key_len, byteorder='big', signed=False)
    #             key_str = recvall(sender, key_len)
    #             key_str = key_str.decode('utf-8')
    #
    #             val_type = recvall(sender, 4)
    #             val_type = int.from_bytes(val_type, byteorder='big', signed=False)
    #             if val_type == 0:
    #                 val_int = recvall(sender, 4)
    #                 val_int = int.from_bytes(val_int, byteorder='big', signed=False)
    #                 step_i_dict[key_str] = val_int
    #             elif val_type == 1:
    #                 float_str_len = recvall(sender, 4)
    #                 float_str_len = int.from_bytes(float_str_len, byteorder='big', signed=False)
    #                 float_str = recvall(sender, float_str_len)
    #                 float_str = float_str.decode('utf-8')
    #                 step_i_dict[key_str] = float(float_str)
    #             elif val_type == 2:
    #                 val_str_len = recvall(sender, 4)
    #                 val_str_len = int.from_bytes(val_str_len, byteorder='big', signed=False)
    #                 val_str = recvall(sender, val_str_len)
    #                 val_str = val_str.decode('utf-8')
    #                 step_i_dict[key_str] = val_str
    #             elif val_type == 3:
    #                 bool_int = recvall(sender, 4)
    #                 bool_int = int.from_bytes(bool_int, byteorder='big', signed=False)
    #                 bool_val = True if bool_int == 1 else False
    #                 step_i_dict[key_str] = bool_val
    #         model_ctx_dict[step_i_name] = step_i_dict
    #
    #     input_ctx_dict = {}
    #     for i in range(flow_step_num + 1):
    #         if i == flow_step_num:
    #             flow_i_name = "R"
    #         else:
    #             flow_i_name = flow_list[i]["name"]
    #         input_i_list_len = recvall(sender, 4)
    #         input_i_list_len = int.from_bytes(input_i_list_len, byteorder='big', signed=False)
    #         input_i_list = []
    #         for j in range(input_i_list_len):
    #             input_i_j_len = recvall(sender, 4)
    #             input_i_j_len = int.from_bytes(input_i_j_len, byteorder='big', signed=False)
    #             input_i_j = recvall(sender, input_i_j_len)
    #             input_i_j = input_i_j.decode('utf-8')
    #             input_i_list.append(input_i_j)
    #         input_ctx_dict[flow_i_name] = input_i_list
    #
    #     output_ctx_dict = {}
    #     for i in range(flow_step_num + 1):
    #         if i == flow_step_num:
    #             flow_i_name = "R"
    #         else:
    #             flow_i_name = flow_list[i]["name"]
    #         output_i_list_len = recvall(sender, 4)
    #         output_i_list_len = int.from_bytes(output_i_list_len, byteorder='big', signed=False)
    #         output_i_list = []
    #         for j in range(output_i_list_len):
    #             output_i_j_len = recvall(sender, 4)
    #             output_i_j_len = int.from_bytes(output_i_j_len, byteorder='big', signed=False)
    #             output_i_j = recvall(sender, output_i_j_len)
    #             output_i_j = output_i_j.decode('utf-8')
    #             output_i_list.append(output_i_j)
    #         output_ctx_dict[flow_i_name] = output_i_list
    #
    #     task = {
    #         "name": name_str,
    #         "flow": flow_list,
    #         "model_ctx": model_ctx_dict,
    #         "input_ctx": input_ctx_dict,
    #         "output_ctx": output_ctx_dict
    #     }
    #     print(task)
    #


