'''
Main process of client(test version).
'''
import multiprocessing as mp
import time

import numpy as np
from TaskClassDict import task_class_dict as td
import server
from threading import Thread


if __name__ == '__main__':
    t1 = Thread(target=server.test1)
    t1.setDaemon(True)
    t1.start()
    while True:
        print("In test.py,{0}".format(server.task))
        time.sleep(1.5)



