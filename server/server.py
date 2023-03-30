'''
此文件为云端端整个系统的入口，用于启动web服务器、云端和边缘端通信的进程
'''
import multiprocessing as mp
import time
from app import app_func
from Communicate import communicate


if __name__ == '__main__':
    q_app_info = mp.Queue(maxsize=1)

    p_web = mp.Process(target=app_func, args=(q_app_info,))
    p_communicate = mp.Process(target=communicate, args=(q_app_info, "0.0.0.0", 5004))

    p_web.start()
    p_communicate.start()



    # while True:
    #     if not q_app_info.empty():
    #         task = q_app_info.get_nowait()
    #         print("get task!")
    #         print(task)
    #         break






