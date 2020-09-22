#!/bin/env python3
'''
此类用于通过读取照片生成初始化数据库
'''

from sys import exit
import os
import pickle

import cv2

from FaceRec.face_proc import FaceProc
from FaceRec.FaceInfo import FaceInfo

ROOT_DIR = 'faces'

db = []


if __name__ == '__main__':
    # Bad design
    faceproc = FaceProc(None)
    try:
        images = os.listdir(ROOT_DIR)
        # 下面就是遍历啦
        for pic in images:
            sp = pic.split('.')
            if len(sp) <= 1 or len(sp[0]) == 0:
                continue
            pinfo, suffix = sp
            # 下面通过文件名获得面部细节
            readImg = cv2.imread(f'{ROOT_DIR}/{pic}')
            try:
                features, pos = faceproc.RecFace_grey(readImg)[0]
            except:
                continue
            # 按照约定的数据结构输入数据
            print(f'{pic}处理完成')
            db.append(FaceInfo(features, pinfo, [features]))

        with open('facedb.db', 'wb') as f:
            s = pickle.dumps(db)
            f.write(s)

        print('文件写到facedb.db中了')
    except FileNotFoundError:
        os.mkdir(ROOT_DIR)
        print(f'目录不存在, 请将照片以pinfo形式命名后放入{ROOT_DIR}中')
    except ValueError:
        print('文件名非法')


