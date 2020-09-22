#!/bin/python

import cv2
import numpy as np

import pickle
from PyQt5.QtWidgets import QInputDialog


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

from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit,
    QInputDialog, QApplication)
import sys

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
        
