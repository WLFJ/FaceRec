#!/bin/env python3

import pickle
import sys
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QInputDialog

import cv2

# 需要导入的包
from FaceRec.FaceRec import FaceRec
from FaceRec.manager import manager
from FaceRec.FaceInfo import FaceInfo
# 结束

import numpy as np

class Video():
    def __init__(self, capture):
        self.capture = capture
        self.currentFrame = np.array([])

    def captureFrame(self):
        return captureNextFrame()

    def captureNextFrame(self, window):
        ret, readFrame = self.capture.read()

        if (ret == True):
            self.currentFrame = cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)

    def convertFrame(self):
        height, width = self.currentFrame.shape[:2]
        self.previousFrame = self.currentFrame
        return height, width


class Ask(QWidget):

    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):

        self.btn = QPushButton('Dialog', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.showDialog)
        
        self.le = QLineEdit(self)
        self.le.move(130, 22)
        
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Input dialog')
        self.show()
        
        
    def showDialog(self):
        
        text, ok = QInputDialog.getText(self, 'Input Dialog', 
            'Enter your name:')
        
        if ok:
            self.le.setText(str(text))
        

class win(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setGeometry(250, 80, 800, 600)  # 从屏幕(250，80)开始建立一个800*600的界面
        self.setWindowTitle('camera')
        self.video = Video(cv2.VideoCapture(0))
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)
        self.update()
        self.videoFrame = QLabel('VideoCapture')
        self.videoFrame.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.videoFrame)

    def update_frame(self, frame):
        """
        在图片捕捉之后, 对frame进行加框识别之后对界面的更新操作.
        """
        height, width = self.video.convertFrame()
        img = QImage(frame, width, height, QImage.Format_RGB888)
        img = QPixmap.fromImage(img)
        self.videoFrame.setPixmap(img)
        self.videoFrame.setScaledContents(True)


    def play(self):
        try:
            self.video.captureNextFrame(self)
            # 因为在对界面更新之后还有一些操作, 因此需要传入捕捉的图像、对图像加框之后的操作
            fr.frame_come(self.video.currentFrame, self.update_frame)
        except TypeError:
            raise

    def closeEvent(self, event):
        if self.video.capture.isOpened():
            self.video.capture.release()
        # 为了保护数据的完整性, 必须在窗口关闭时间触发时指定
        # 返回经过更新的数据库, 需要手动保存
        db = fr.close_event()
        with open('facedb.db', 'wb') as f:
            s = pickle.dumps(db)
            f.write(s)
        # 结束

        event.accept()


if __name__ == '__main__':
    # 获取界面数据库
    with open('facedb.db', 'rb') as f:
        face_database_all = pickle.loads(f.read())
    # 获取启动参数, 指定活动ID
    # 打印数据
    act_id = sys.argv[1]
    # 实例化识别引擎
    fr = FaceRec(manager(), face_database_all, 'localhost:8000', act_id)
    # 回调函数, 在识别成功和识别失败时调用你绑定的函数, 注意参数个数必须相同, 例子如下:
    def callback_succ(pinfo, pname):
        print('识别成功!', pinfo, pname)
    fr.rec_out = callback_succ
    def callback_faild(frame):
        # 识别失败自然不会有pinfo了, 于是会返回当前完整的图片
        # (后期会变成单独的人脸照片, 现在因为效率问题没有实现)
        print('识别失败')
    fr.rec_fail = callback_faild
    # 结束
    app = QApplication(sys.argv)
    win = win()
    win.show()
    sys.exit(app.exec_())
