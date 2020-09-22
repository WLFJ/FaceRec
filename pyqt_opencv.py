#!/bin/env python3

import sys
import cv2
import requests
import os
import json
import threading
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pickle

import cv2
import numpy as np

from Cap_Rec import Video
from face_proc import FaceProc
from FaceInfo import FaceInfo
from manager import manager

font = cv2.FONT_HERSHEY_SIMPLEX

def rec_check_in(pinfo):
    if stu_manager.is_in(pinfo):
        return
    res = requests.get(f'http://localhost:8000/checkin/{act_id}/{pinfo}')
    if res.text != '{"msg": "OK."}':
        print('签到失败', res.text)
    else:
        print('签到成功', pinfo)
        stu_manager.record(pinfo)


class win(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setGeometry(250, 80, 800, 600)  # 从屏幕(250，80)开始建立一个800*600的界面
        self.setWindowTitle('camera')
        # 创建一个video对象
        self.video = Video(cv2.VideoCapture(0))
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)
        self.update()
        self.videoFrame = QLabel('VideoCapture')
        self.videoFrame.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.videoFrame)
        # self.ret, self.capturedFrame = self.video.capture.read()

    def play(self):
        try:
            # 实现的特别好 通过捕捉、转换、变换大小
            self.video.captureNextFrame(self)
            # 业务逻辑
            # ---在这里添加面部算法
            # 检测到人脸
            people_features = face_proc.RecFace(self.video.currentFrame)
            pinfo_list = []
            if len(people_features) != 0:
                for feature, pos in people_features:
                    cv2.rectangle(self.video.currentFrame, tuple([pos[0], pos[2]]), tuple([pos[1], pos[3]]), (255, 0, 0), 2)
                    pinfo = face_proc.FindPInfo(feature)
                    pinfo_list.append(pinfo)
                    cv2.putText(self.video.currentFrame, pinfo, (pos[0], pos[2]), font, 1.2, (255, 255, 255), 2)

            # 显示画面
            # 我们需要在这里录入信息
            height, width = self.video.convertFrame()
            img = QImage(self.video.currentFrame, width, height, QImage.Format_RGB888)
            img = QPixmap.fromImage(img)
            self.videoFrame.setPixmap(img)

            self.videoFrame.setScaledContents(True)
            # 下面是真正的业务逻辑
            if len(people_features) != 0:
                for feature, pos in people_features:
                    pinfo = pinfo_list.pop(0)
                    # 如果pinfo识别到了 我们就要通知将这个面部信息更新一下
                    if pinfo != face_proc.NOT_FOUND:
                        # 同时应该通知记录签到信息
                        # 这里通过新开线程实现
                        threading.Thread(target=rec_check_in, args=(pinfo,)).start()
                    else:
                        pass
                        # 我们只能在这里创建子窗体实现了
                        # 现在我们弹出对话框 同时阻塞当前进程
                        # pinfo, ok = QInputDialog.getText(self,'未知人脸(详情见屏幕)','请输入学号')
                        # if ok:
                        #     try:
                        #         feature, pos = face_proc.RecFace_grey(self.video.currentFrame)[0]
                        #     except:
                        #         print("录入失败")
                        # else:
                        #     continue
                    # 现在关键是这个方法了
                    face_proc.AddFeature(pinfo, feature)

            # 业务逻辑
        except TypeError:
            raise
            #print("Frame Error !")

    def closeEvent(self, event):
        if self.video.capture.isOpened():
            self.video.capture.release()
        # 保存面部信息表
        # bad data_structure!
        for i, s1 in enumerate(face_database_all):
            for j, s2 in enumerate(face_databese):
                if s1.pinfo == s2.pinfo:
                    face_database_all[i] = s2
                    del face_databese[j]

        with open('facedb.db', 'wb') as f:
            s = pickle.dumps(face_database_all)
            f.write(s)

        event.accept()


if __name__ == '__main__':
    # 准备面部数据库
    with open('facedb.db', 'rb') as f:
        face_database_all = pickle.loads(f.read())
    # 通过传入的数据将数据库精简, 但是在修改时依然需要将其写回去, 一定要注意
    act_id = sys.argv[1]
    # 获取待签到的学号
    stu_ids = json.dumps(requests.get(f'http://localhost:8000/checkin/{act_id}').text)
    face_databese = [s for s in face_database_all if s.pinfo in stu_ids]
    # 准备结束
    face_proc = FaceProc(face_databese)
    # 准备签到信息
    stu_manager = manager()
    # 准备结束
    app = QApplication(sys.argv)
    win = win()
    win.show()
    sys.exit(app.exec_())
