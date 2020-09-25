#!/bin/env python3
'''
此类用于通过读取照片生成初始化数据库
'''

from sys import exit
import os
import pickle
import threading
import time

import cv2

from FaceRec.FaceInfo import FaceInfo
from FaceRec.face_proc import FaceProc

ROOT_DIR = 'faces'
THREADS = 2

db = []

class RecThread(threading.Thread):
    def __init__(self, task_list):
        super(RecThread, self).__init__()
        self.task_list = task_list
        self.result = []

    def run(self):
        for pinfo, pic_name in self.task_list:
            print(f'Rec {pinfo}...')
            readImg = cv2.imread(f'{ROOT_DIR}/{pic_name}')
            features, pos = faceproc.RecFace_grey(readImg)[0]
            self.result.append(FaceInfo(features, pinfo, [features]))

    def get_result(self):
        return self.result

if __name__ == '__main__':
    start_time = time.time()
    # 从一开始就计时
    # Bad design
    faceproc = FaceProc(None)
    images = os.listdir(ROOT_DIR)
    # 下面就是遍历啦
    # (pinfo, filename)
    task_list = []
    for pic in images:
        sp = pic.split('.')
        if len(sp) <= 1 or len(sp[0]) == 0:
            continue
        pinfo, suffix = sp
        task_list.append((pinfo, pic))

    # 现在要开始分配任务, 创建进程了
    task_len = len(task_list)
    sub_task_seg = task_len // min(THREADS, task_len)
    threads = []
    for i in range(0, task_len, sub_task_seg):
        t = RecThread(task_list[i:min(i+sub_task_seg, task_len)])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
        db.extend(t.get_result())

    with open('facedb.db', 'wb') as f:
        s = pickle.dumps(db)
        f.write(s)

    print('文件写到facedb.db中了')
    end_time = time.time()
    print(f'总用时为{round(end_time - start_time, 2)}secs')


