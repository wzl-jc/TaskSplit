import cv2
import numpy as np
import time

# 读取视频流
video = cv2.VideoCapture("videos/helmet2.mp4")

# 读取第一帧
ret, frame1 = video.read()

# 设置初始值
prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
avg = np.float32(prev_gray)

# 设置阈值
threshold = 1

while True:
    time.sleep(0.1)
    # 读取当前帧
    ret, frame2 = video.read()

    if not ret:
        break

    # 将当前帧转换为灰度图像并进行高斯模糊
    gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # 计算当前帧和前一帧之间的帧差值
    frame_diff = cv2.absdiff(prev_gray, gray)

    # 计算平均帧差值
    cv2.accumulateWeighted(frame_diff, avg, 0.5)
    avg_frame_diff = cv2.convertScaleAbs(avg)

    # 根据阈值判断是否触发事件
    if cv2.mean(avg_frame_diff)[0] > threshold:
        # 在检测到事件时执行所需的操作
        print('事件已发生！' + str(time.time()))

        # 在当前帧中绘制矩形
        cv2.rectangle(frame2, (0, 0), (frame2.shape[1], frame2.shape[0]), (0, 0, 255), 5)

        # 在当前帧中添加文本
        cv2.putText(frame2, 'Event Occurred', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 更新上一帧
    prev_gray = gray

    # 在屏幕上显示当前帧
    cv2.imshow('frame', frame2)

    # 按q键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放视频流
video.release()

# 关闭窗口
cv2.destroyAllWindows()
