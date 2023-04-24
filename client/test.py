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
import paramiko
import datetime as dt
import os
import stat
import sys


# 递归遍历远程服务器指定目录下的所有文件
def _get_all_files_in_remote_dir(sftp1, remote_dir):
    all_files = list()
    if remote_dir[-1] == '/':
        remote_dir = remote_dir[0:-1]

    files = sftp1.listdir_attr(remote_dir)
    for file in files:
        filename = remote_dir + '/' + file.filename

        if stat.S_ISDIR(file.st_mode):  # 如果是文件夹的话递归处理
            all_files.extend(_get_all_files_in_remote_dir(sftp1, filename))
        else:
            all_files.append(filename)

    return all_files


# 远程服务器上指定文件夹下载到本地文件夹
def sftp_get_dir(sftp1, remote_dir, local_dir):
    try:
        all_files = _get_all_files_in_remote_dir(sftp1, remote_dir)

        for file in all_files:

            local_filename = file.replace(remote_dir, local_dir)
            local_filepath = os.path.dirname(local_filename)

            if not os.path.exists(local_filepath):
                os.makedirs(local_filepath)

            sftp1.get(file, local_filename)

    except:
        print('ssh get dir from master failed.')


def callback(size, file_size):
    print("Get file from server success!")


if __name__ == '__main__':
    # hostname = "114.212.81.11"
    # port = 22
    # username = 'hx'
    # password = '123456'
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(hostname, port, username, password)
    # sftp = ssh.open_sftp()
    # # stdin, stdout, stderr = ssh.exec_command('ifconfig')
    # # print(stdout.read().decode())
    # remotedir = '/home/hx/wzl/test/'
    # if remotedir[-1] == '/':
    #     remotedir = remotedir[0:-1]
    # lastdir = (remotedir.split('/'))[-1]
    # localdir = 'C:\\WorkSpace\\temptest'
    # if not os.path.exists(localdir):
    #     os.mkdir(localdir)
    # # localdir = localdir + lastdir
    # localdir = os.path.join(localdir, lastdir)
    # localdir = os.path.join(localdir, '')
    # if not os.path.exists(localdir):
    #     os.mkdir(localdir)
    # print(localdir)
    # sftp_get_dir(sftp, remotedir, localdir)
    # print("Get file from server success!")
    # ssh.close()
    a = AppInfo('172.27.150.157', 5004)
    print(a.get_task_code_path())

