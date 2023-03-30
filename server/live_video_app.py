from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# 从摄像头获取实时视频流
cap = cv2.VideoCapture(0)


@app.route('/')
def index():
    # 将index.html渲染到浏览器上
    return "test!!!"


def gen():
    while True:
        # 从摄像头读取一帧
        ret, frame = cap.read()

        if not ret:
            break

        # 将帧转换为字符串，以便在HTML页面上显示
        frame_str = cv2.imencode('.jpg', frame)[1].tobytes()

        # 通过yield关键字实现流式传输
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_str + b'\r\n')


@app.route('/video_feed')
def video_feed():
    # 将gen()方法封装成一个Response对象
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(port=5501)
