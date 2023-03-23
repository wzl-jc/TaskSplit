'''
负责视频帧的读取和返回
'''
import cv2
from plot_helper import plot_boxes


def get_frames(frame_num):
    #  设置视频路径并读取帧
    video_path = 'inference/video/人少--人多.mp4'

    # read frame from video
    video_cap = cv2.VideoCapture(video_path)
    img_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    print('Frame width: {}, height: {}, fps: {}'.format(img_width, img_height, fps))
    frame_list_1 = []
    for _ in range(frame_num):
        ret, frame = video_cap.read()
        frame_list_1.append(frame)
        cv2.imwrite("frame-0" + ".jpg", frame)
    return frame_list_1, img_width, img_height


def get_frames_1(frame_index_list):
    #  此函数用来获取frame_index_list中指定索引的帧，frame_index_list中的索引升序排列，索引从0开始
    if len(frame_index_list) == 0:
        return []
    temp_idx = 0
    #  设置视频路径并读取帧
    video_path = 'inference/video/人少--人多.mp4'

    # read frame from video
    video_cap = cv2.VideoCapture(video_path)
    img_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    print('Frame width: {}, height: {}, fps: {}'.format(img_width, img_height, fps))
    frame_list_1 = []
    frame_num = frame_index_list[-1]  # 需要读取的最后一帧的索引
    for i in range(frame_num+1):
        ret, frame = video_cap.read()
        # mat = cv2.imencode('.jpg', frame)[1]
        # print(len(mat))
        if i == frame_index_list[temp_idx]:
            # cv2.imwrite("1.jpg", frame)
            frame_list_1.append(frame)
            temp_idx += 1
    return frame_list_1, img_width, img_height


def get_video_frame_num():
    #  设置视频路径并读取帧
    video_path = 'inference/video/helmet1.mp4'

    # read frame from video
    video_cap = cv2.VideoCapture(video_path)
    img_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    print(video_path)
    print('Frame width: {}, height: {}, fps: {}'.format(img_width, img_height, fps))

    res = 1
    ret, frame = video_cap.read()
    print(type(frame), frame.shape, frame)
    # while ret:
    #     ret, frame = video_cap.read()
    #     res += 1
    return res


if __name__ == '__main__':
    # frame_index = [150]
    # frame_list, width, height = get_frames_1(frame_index)
    # print(len(frame_list), frame_list[0].shape, width, height)
    # pos_list = [5, 5, 50, 50, 90, 90, 200, 200]
    # plot_boxes(pos_list, frame_list[0])
    res = get_video_frame_num()
    print(res)


