'''
Main process of client(test version).
'''
import multiprocessing as mp
import numpy as np
from video_helper import *
import os


def gcd(x, y):
    # 求x和y的最大公因数
    if x < y:
        x, y = y, x
    if y == 0:
        return x
    else:
        return gcd(y, x % y)


def split_helper(img_size, split_size, obj_size):
    '''
    返回img_size长度按照split_size切分，物体大小为obj_size（即切片之间的重合部分大小为obj_size）时切片的数量以及各个切片的开始位置
    Args:
        img_size: 图像大小
        split_size: 切片大小
        obj_size: 物体大小
    Returns:
        res_dict['split_num']为切片数量
        res_dict['start_pos_list']为各个切片的开始位置
    '''
    res_dict = {}
    if split_size >= img_size:
        res_dict['split_num'] = 1
        res_dict['start_pos_list'] = [0]
    else:
        split_num = 0
        start_pos_list = []
        start_pos = 0
        end_pos = start_pos + split_size - 1
        while end_pos < img_size-1:
            split_num += 1
            start_pos_list.append(start_pos)
            start_pos = start_pos + split_size - obj_size
            end_pos = start_pos + split_size - 1
        # 最后添加一个以边界为结束位置的切片
        split_num += 1
        start_pos_list.append(img_size-split_size)
        res_dict['split_num'] = split_num
        res_dict['start_pos_list'] = start_pos_list
    return res_dict


def get_detection_split_res(img_shape, nano_split_size, nano_worker_num, server_split_size, server_worker_num,
                            obj_size):
    print(img_shape)
    gcd_res = gcd(img_shape[0], img_shape[1])  # 求出图像的高度、宽度比
    frame_height_percent = int(img_shape[0] / gcd_res)
    frame_width_percent = int(img_shape[1] / gcd_res)
    print(frame_height_percent, frame_width_percent)
    # 高度和宽度按照nano_split_size、obj_size切分的结果
    nano_height_split_res = split_helper(img_shape[0], nano_split_size['split_size'], obj_size[0])
    nano_split_width = int(nano_split_size['split_size']/frame_height_percent*frame_width_percent)
    nano_width_split_res = split_helper(img_shape[1], nano_split_width, obj_size[1])
    print(nano_height_split_res, nano_width_split_res)

    coord_res = []  # 各个切片的左上角坐标
    size_res = []  # 各个切片的大小
    model_type_res = []  # 各个切片使用的模型种类
    # 首先尽可能将nano端的切片加入结果
    if nano_height_split_res['split_num'] * nano_width_split_res['split_num'] <= nano_worker_num:
        # 若nano端切片的数量小于等于nano端工作进程的数量，说明切分的任务可以都在nano端执行，将nano切片的结果全部加入
        for i in range(nano_height_split_res['split_num']):
            for j in range(nano_width_split_res['split_num']):
                coord_res.append((nano_height_split_res['start_pos_list'][i],
                                  nano_width_split_res['start_pos_list'][j]))
                size_res.append((nano_split_size['split_size'], nano_split_width))
                model_type_res.append(nano_split_size['model_size'])
    else:
        # 若nano端切片的数量大于nano端工作进程的数量，加入尽可能多的nano端切片，其余的全为server切片
        nano_split_row = int(nano_worker_num/nano_width_split_res['split_num'])+1
        for i in range(nano_split_row):
            for j in range(nano_width_split_res['split_num']):
                coord_res.append((nano_height_split_res['start_pos_list'][i],
                                  nano_width_split_res['start_pos_list'][j]))
                size_res.append((nano_split_size['split_size'], nano_split_width))
                model_type_res.append(nano_split_size['model_size'])
        # server端切片开始的height位置
        server_height_start = nano_height_split_res['start_pos_list'][nano_split_row-1]+nano_split_size['split_size']
        server_height_start -= obj_size[0]
        server_height_start = min(server_height_start, img_shape[0]-server_split_size['split_size'])
        server_height_split_res = split_helper(img_shape[0]-server_height_start, server_split_size['split_size'],
                                               obj_size[0])
        server_split_width = int(server_split_size['split_size'] / frame_height_percent * frame_width_percent)
        server_width_split_res = split_helper(img_shape[1], server_split_width, obj_size[1])
        for i in range(server_height_split_res['split_num']):
            for j in range(server_width_split_res['split_num']):
                coord_res.append((server_height_split_res['start_pos_list'][i]+server_height_start,
                                  server_width_split_res['start_pos_list'][j]))
                size_res.append((server_split_size['split_size'], server_split_width))
                model_type_res.append(server_split_size['model_size'])
    split_res = {'split_num': len(coord_res),
                 'coord_res': coord_res,
                 'size_res': size_res,
                 'model_type_res': model_type_res}
    return split_res


if __name__ == '__main__':
    # args = parse_args()
    #
    # frame_num = 1
    # frame_list, width, height = get_frames(frame_num)
    # face_detection = FaceDetection(args['face_detection'])
    # face_alignment = FaceAlignmentCNN(args['pose_estimation'])
    #
    # for i in range(frame_num):
    #     # t1 = time.time()
    #     boxes, labels, probs = face_detection(frame_list[i])
    #     # t2 = time.time()
    #     # print(type(boxes), type(labels), type(probs))
    #     bbox = [boxes[j, :].numpy() for j in range(boxes.size(0))]
    #     prob = [probs[j].item() for j in range(probs.size(0))]
    #     # t3 = time.time()
    #     print(bbox)
    #     # head_pose = face_alignment(frame_list[i], bbox, prob)
    #     print("")
    #     # t4 = time.time()
    #     # print(head_pose)
    #     # print("Per frame done! FaceDetection spend:{}s, PoseEstimation spend:{}s, face num:{}!".format(t2-t1, t4-t3,
    #     #                                                                                                len(bbox)))

    # frame_shape = [1080, 1920]
    # obj_size = [100, 40]
    # nano_split_size = {'model_size': 0,
    #                    'split_size': 360}
    # server_split_size = {'model_size': 1,
    #                      'split_size': 480}
    # nano_worker_num = 4  # nano和server端工作进程数目
    # server_worker_num = 32
    # cur_split_strategy = get_detection_split_res(frame_shape, nano_split_size, nano_worker_num,
    #                                              server_split_size, server_worker_num, obj_size)
    # print(cur_split_strategy)
    # frame = np.zeros((1080, 1920, 3))
    # for i in range(cur_split_strategy['split_num']):
    #     x = cur_split_strategy['coord_res'][i][0]
    #     y = cur_split_strategy['coord_res'][i][1]
    #     h = cur_split_strategy['size_res'][i][0]
    #     w = cur_split_strategy['size_res'][i][1]
    #     sub_frame = frame[x:x + h, y:y + w, :]
    #     print(sub_frame.shape)
    #
    # l = [0, 1, 2, 3, 4, 5]
    # print(l[0:2])
    a = 4
    while a < 128:
        print("Event detected! Current interval is :{}".format(a))
        a *= 2
    print("Event detected! Current interval is :{}".format(a + 16))
    print("Event detected! Current interval is :{}".format(a + 32))
    print("Event detected! Current interval is :{}".format(a + 48))
    print("Event detected! Current interval is :{}".format(a + 64))

