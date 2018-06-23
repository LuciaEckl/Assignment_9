#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import wiimote
import time
import sys
import numpy as np
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from transform import Transform


class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.start_pos = (0, 0)
        self.mouseMovePos = (0, 0)
        self.draw = False
        self.coordinates = []
        self.initUI()


    def initUI(self):

        self.pushButton = QtWidgets.QPushButton("Add Symbol")
        self.layout = QtWidgets.QHBoxLayout(self)

       # self.pushButton.move(50, 50)
        self.pushButton.setFixedWidth(50)
        self.pushButton.setFixedHeight(50)
        self.pushButton.pos().setY(100)
       # self.pushButton.setStyleSheet("align: right")
        self.layout.addWidget(self.pushButton)
        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle('1$ Recognizer')
        QtGui.QCursor.setPos(self.mapToGlobal(
            QtCore.QPoint(self.start_pos[0], self.start_pos[0])))
        self.show()

    def mousePressEvent(self, ev):
        print("clicked")
        self.draw = True

    def mouseReleaseEvent(self, ev):
        print("release")
        self.draw = False

    def mouseMoveEvent(self, ev):
        if self.draw is True:
            self.mouseMovePos = ev.x(), ev.y()
            self.coordinates.append(self.mouseMovePos)
            self.update()



    def paintEvent(self, event):
            qp = QtGui.QPainter()
            qp.begin(self)
            if self.draw is True:
                self.drawtarget(qp)


            qp.end()


    def drawtarget(self, qp):
        qp.setBrush(QtGui.QColor(0, 200, 0))
        for i in range(len(self.coordinates) - 1):
            qp.drawLine(self.coordinates[i][0], self.coordinates[i][1], self.coordinates[i + 1][0], self.coordinates[i +1][1])




def main():
    app = QtWidgets.QApplication(sys.argv)
    #application = QtGui.QD
    w = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
