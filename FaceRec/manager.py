#!/bin/python

import time

'''
本类用于管理学生签到适宜, 需要能够导出信息, 整理报表
'''

class manager():
    '''
    目前只记录签到的学生
    '''
    def __init__(self):
        self.stu_dic = dict()

    def record(self, pinfo):
        if not self.is_in(pinfo):
            self.stu_dic[pinfo] = time.time()

    def is_in(self, pinfo):
        return pinfo in self.stu_dic.keys()

    def get_rec(self):
        return self.stu_dic.copy()

if __name__ == '__main__':
    m = manager()
    m.record('10086')
    print(m.get_rec())
