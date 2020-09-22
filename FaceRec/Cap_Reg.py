#!/bin/python

import cv2
import numpy as np

import pickle

font = cv2.FONT_HERSHEY_SIMPLEX

class Video():
    def __init__(self, capture, face_proc, manager):
        self.capture = capture
        self.currentFrame = np.array([])
        self.face_proc = face_proc
        self.manager = manager

    def captureFrame(self):
        return captureNextFrame()

    def captureNextFrame(self):
        ret, readFrame = self.capture.read()
        # ---在这里添加面部算法
        # 检测到人脸
        people_features = self.face_proc.RecFace(readFrame)
        if len(people_features) != 0:
            for feature, pos in people_features:
                cv2.rectangle(readFrame, tuple([pos[0], pos[2]]), tuple([pos[1], pos[3]]), (255, 0, 0), 2)
                pinfo = self.face_proc.FindPInfo(feature)
                cv2.putText(readFrame, pinfo, (pos[0], pos[2]), font, 1.2, (255, 255, 255), 2)
                # 如果pinfo识别到了 我们就要通知将这个面部信息更新一下
                if pinfo == self.face_proc.NOT_FOUND:
                    # 但是我们需要提供pinfo
                    pass

        if (ret == True):
            self.currentFrame = cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)

    def convertFrame(self):
        height, width = self.currentFrame.shape[:2]
        self.previousFrame = self.currentFrame
        return height, width
