#!/bin/python

import time

import dlib  # 人脸识别的库dlib
import numpy as np
import threading
from .utiles import eu_dis
from .FaceInfo import FaceInfo

import cv2

THREADS = 8
NOT_FOUND = 'Unknown face!'

class RecThread(threading.Thread):
    def __init__(self, face_list, feature):
        super(RecThread, self).__init__()
        self.face_list = face_list
        self.feature = feature

    def run(self):
        """
        在这里找到最小的属性
        """
        self.result = min([ (eu_dis(self.feature, p.features), p.pinfo, p) for p in self.face_list ])

    def get_result(self):
        try:
            return self.result
        except Exception:
            return (1, NOT_FOUND)

class FaceProc():
    '''
    在有新脸的时候会进行处理, 具体比对数据库
    '''


    def __init__(self, database):

        self.detector = dlib.get_frontal_face_detector()
        self.facerec = dlib.face_recognition_model_v1("model/dlib_face_recognition_resnet_model_v1.dat")
        self.predictor = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')

        self.choose_face = lambda l : l[0][1]

        self.database = database


    def FindPInfo(self, feature):
        '''
        在数据库中查找脸, 并将人的信息对象返回
        现在我们要改成线程方式, 多个线程计算最小值.
        现在要
        '''
        # 这里默认三个线程
        threads = []
        # 现在我们要将所有任务分配
        list_len = len(self.database)
        # 现在要把最后的也分配
        thread_seg = list_len // min(THREADS, list_len)
        res_list = []
        for i in range(0, list_len, thread_seg):
            t = RecThread(self.database[i : min(i + thread_seg, list_len)], feature)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
            res_list.append(t.get_result())

        # 这里需要查看所有<0.4的, 如果有多个, 则先输出一下
        min_res = list(sorted(filter(lambda x: x < (0.4, None, None), res_list)))
        len_min_res = len(min_res)

        if len_min_res == 0: return (NOT_FOUND, True)
        # 以下是判断识别的逻辑

        # 这里要优化展示内容
        # 这里我们要指定是谁! 从而更新人脸
        # 我们还需要添加签到时间戳(当然是运行时, 如果发现有时间间隔很小的, 自然可以将其归为同类)
        # 现在我们还需要过滤是否有record_timestamp属性的, 如果只有一个, 则直接选择了
        if len_min_res == 1 and min_res[0][0] < 0.25 and len(min_res[0][2].feature_list) < 30:
            return (min_res[0][1], True)
        elif ('record_timestamp' in dir(min_res[0][2]) and time.time() - min_res[0][2].record_timestamp < 1000):
            print('自动选择')
            return (min_res[0][1], True)
        elif len_min_res > 1 and min_res[1][0] - min_res[0][0] > 0.1:
            return (min_res[0][1], True)

        res = self.choose_face(min_res)
        return (NOT_FOUND, True) if res == None else (res, False);

    def _RecFace(self, readFrame):
        '''
        通过视频帧返回人脸信息
        我们还需要更多信息
        返回信息格式tuple(feature, (left, right, top, bottom))
        '''
        return [ (self.facerec.compute_face_descriptor(readFrame, self.predictor(readFrame, a)), (a.left(), a.right(), a.top(), a.bottom())) for a in self.detector(readFrame, 1) ]

    def RecFace_grey(self, readFrame):
        '''
        通过视频帧返回人脸信息
        我们还需要更多信息
        返回信息格式tuple(feature, (left, right, top, bottom))
        '''
        readFrame = cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)
        return self._RecFace(readFrame)

    def RecFace(self, readFrame):
        '''
        通过视频帧返回人脸信息
        我们还需要更多信息
        返回信息格式tuple(feature, (left, right, top, bottom))
        '''
        return self.RecFace_grey(readFrame)

    def AddFeature(self, pinfo, feature, force_add=False):
        '''
        为指定pinfo添加面部信息
        !! 糟糕的数据结构 应该按照pinfo为主码去做
        同时需要检查数据量
        '''
        goal_p = None
        for f in self.database:
            if f.pinfo == pinfo:
                if len(f.feature_list) >= 50 and not force_add:
                    return
                goal_p = f
                f.feature_list.append(feature)
                # 同时为其添加时间戳, 作为识别依据
                f.record_timestamp = time.time()
                break
        else:
            self.database.append(FaceInfo(features=None, pinfo=pinfo, feature_list=[feature, ]))
            goal_p = self.database[-1]

        # 下面要更新其中的数据
        feature_average = []
        for j in range(128):
            feature_average.append(0)
            for i in range(len(goal_p.feature_list)):
                feature_average[j] += goal_p.feature_list[i][j]
            feature_average[j] = (feature_average[j]) / len(goal_p.feature_list)

        goal_p.features = feature_average

