import pickle
import sys
import os
from time import localtime, strftime
import wx
from pubsub import pub
import cv2
from threading import Thread
import threading
# 需要导入的包
from FaceRec.FaceRec import FaceRec
from FaceRec.manager import manager
from FaceRec.FaceInfo import FaceInfo
# 结束

import numpy as np

ID_NEW_REGISTER = 160
ID_FINISH_REGISTER = 161
ID_START_PUNCHCARD = 190
ID_END_PUNCARD = 191
ID_OPEN_LOGCAT = 283
ID_CLOSE_LOGCAT = 284
ID_WORKER_UNAVIABLE = -1

class Runthread(Thread):
    def __init__(self):
        self.endflag = 0
        super(Runthread, self).__init__()

    def update_frame(self, im_rd):
        img_height, img_width = im_rd.shape[:2]
        # image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
        pic = wx.Bitmap.FromBuffer(img_width, img_height, im_rd)
        # self.bmp.SetBitmap(pic)
        wx.CallAfter(pub.sendMessage, 'pic', pic=pic)

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while cap.isOpened():
            flag, im_rd = cap.read()
            image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
            fr.frame_come(image1, self.update_frame)
            if self.endflag == 1:
                break
        cap.release()
        cv2.destroyAllWindows()

class Interface(wx.Frame):

    def getDateAndTime(self):
        dateandtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        return "["+dateandtime+"]"

    def initInfoText(self):
        resultText = wx.StaticText(parent=self, pos=(10, 20), size=(90, 60))
        resultText.SetBackgroundColour('red')
        self.info = "\r\n"+self.getDateAndTime()+"程序初始化成功\r\n"
        self.infoText = wx.TextCtrl(parent=self,size=(400, 500),
                   style=(wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY))
        self.infoText.SetForegroundColour("ORANGE")
        self.infoText.SetLabel(self.info)
        font = wx.Font()
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        font.SetUnderlined(True)
        self.infoText.SetFont(font)
        self.infoText.SetBackgroundColour('TURQUOISE')
        pass

    def OnStartPunchCardClicked(self, event):
        self.thread = Runthread()
        self.thread.start()
        pass

    def call_back(self, pic):
        self.bmp.SetBitmap(pic)

    def OnEndPunchCardClicked(self, event):
        print("开始结束签到...")
        self.thread.endflag = 1
        db = fr.close_event()
        with open('facedb.db', 'wb') as f:
            s = pickle.dumps(db)
            f.write(s)
        print("结束签到")
        self.bmp.SetBitmap(wx.Bitmap(self.pic_index))
        pass

    def initMenu(self):
        menuBar = wx.MenuBar()
        menu_Font = wx.Font()
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)

        puncardMenu = wx.Menu()
        self.start_punchcard = wx.MenuItem(puncardMenu, ID_START_PUNCHCARD, "开始签到")
        self.start_punchcard.SetTextColour("SLATE BLUE")
        self.start_punchcard.SetFont(menu_Font)
        puncardMenu.Append(self.start_punchcard)

        self.end_puncard = wx.MenuItem(puncardMenu, ID_END_PUNCARD, "结束签到")
        self.end_puncard.SetTextColour("SLATE BLUE")
        self.end_puncard.SetFont(menu_Font)
        puncardMenu.Append(self.end_puncard)

        menuBar.Append(puncardMenu, "&刷脸签到")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnStartPunchCardClicked, id=ID_START_PUNCHCARD)
        self.Bind(wx.EVT_MENU, self.OnEndPunchCardClicked, id=ID_END_PUNCARD)

    def initGallery(self):
        self.pic_index = wx.Image("lc.jpg", wx.BITMAP_TYPE_ANY).Scale(600, 500)
        self.bmp = wx.StaticBitmap(parent=self, pos=(400, 0), bitmap=wx.Bitmap(self.pic_index))
        pass

    def callback_succ(self, pinfo):
        if pinfo in self.map:
            print("重复签到")
        else:
            print('识别成功', pinfo)
            self.infoText.AppendText("学号"+pinfo+"签到成功!\n")
            self.map.append(pinfo)


    def callback_faild(self, frame):
        print("识别失败")


    def __init__(self):
        self.map = []
        fr.rec_fail = self.callback_faild
        fr.rec_out = self.callback_succ
        wx.Frame.__init__(self, parent=None, title="中北大学学生考勤系统", size=(1020, 560))
        self.initMenu()
        self.initInfoText()
        self.initGallery()
        # self.initData()
        pub.subscribe(self.call_back, "pic")


if __name__ == '__main__':
    # 获取界面数据库
    with open('facedb.db', 'rb') as f:
        face_database_all = pickle.loads(f.read())
    fr = FaceRec(manager(), face_database_all, '3.wlfj.fun:8000', 7)
    app = wx.App()
    frame = Interface()
    frame.Show()
    app.MainLoop()
