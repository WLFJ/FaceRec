import cv2
import requests
import json
import threading

import pickle

import cv2
import numpy as np

from .face_proc import FaceProc
from .face_proc import NOT_FOUND
from .FaceInfo import FaceInfo
from .manager import manager

font = cv2.FONT_HERSHEY_SIMPLEX

class FaceRec():
    """
    面部识别封装模块
    """
    def __init__(self, stu_manager, face_database, server, act_id):
        self.stu_manager = stu_manager
        self.face_database_all = face_database
        self.stu_infos = json.loads(requests.get(f'http://{server}/checkin/{act_id}').text)
        self.face_database = [s for s in self.face_database_all if s.pinfo in self.stu_infos.keys()]
        self.face_proc = FaceProc(self.face_database)
        self.act_id = act_id
        self.server = server
        self.rec_out = lambda pinfo: {}
        self.rec_fail = lambda frame: {}

    def rec_check_in(self, pinfo):
        if self.stu_manager.is_in(pinfo):
            return
        res = requests.get(f'http://{self.server}/checkin/{self.act_id}/{pinfo}')
        if res.text != '{"msg": "OK."}':
            print('签到失败', res.text)
        else:
            self.stu_manager.record(pinfo)

    def frame_come(self, frame, frame_process):
        """
        在捕捉到来的时候
        """
        people_features = self.face_proc.RecFace(frame)
        pinfo_list = []
        if len(people_features) != 0:
            for feature, pos in people_features:
                cv2.rectangle(frame, tuple([pos[0], pos[2]]), tuple([pos[1], pos[3]]), (255, 0, 0), 2)
                (pinfo, is_auto) = self.face_proc.FindPInfo(feature)
                pinfo_list.append((pinfo, is_auto))
                # 我们要在这里添加编号, 方便处理询问
                cv2.putText(frame, pinfo, (pos[0], pos[2]), font, 1.2, (255, 255, 255), 2)

        frame_process(frame)

        if len(people_features) != 0:
            for feature, pos in people_features:
                pinfo, isA_auto = pinfo_list.pop(0)
                if pinfo != NOT_FOUND:
                    # threading.Thread(target=self.rec_out, args=(pinfo, self.stu_infos[pinfo])).start()
                    self.rec_out(pinfo, self.stu_infos[pinfo])
                    threading.Thread(target=self.rec_check_in, args=(pinfo,)).start()
                    # 现在我们要能知道是不是强制添加
                    self.face_proc.AddFeature(pinfo, feature, not is_auto)
                else:
                    threading.Thread(target=self.rec_fail, args=(frame, )).start()

    def close_event(self):
        for i, s1 in enumerate(self.face_database_all):
            for j, s2 in enumerate(self.face_database):
                if s1.pinfo == s2.pinfo:
                    self.face_database_all[i] = s2
                    del self.face_database[j]

        return self.face_database_all

