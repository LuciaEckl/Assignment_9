#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import wiimote
import time
import sys
import numpy as np
from PyQt5 import uic, QtWidgets, QtCore, QtGui, Qt
from transform import Transform
import math


class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.start_pos = (0, 0)
        self.mouseMovePos = (0, 0)
        self.draw = False
        self.coordinates = []
        self.pointNumber = 64
        self.pushButton = QtWidgets.QPushButton("Add Symbol")
        self.addGestureButton = QtWidgets.QPushButton("Add gesture/symbol")
        self.X = 0
        self.Y = 0
        self.resampledPoints = []
        self.square_size = 100
        self.drawNewPoints = False
        self.newPointsToDraw = []
        self.initUI()

# making Boxlayouts within a boxlayout
# https://stackoverflow.com/questions/49127653/align-every-widget-of-a-qhboxlayout-to-the-top-in-pyqt
# last accessed 25.06.2018
# line edit hint text:
# http://doc.qt.io/qt-5/qtwidgets-widgets-lineedits-example.html
# last access 25.06.2018
    def initUI(self):

        self.layout = QtWidgets.QVBoxLayout(self)



        self.dropdown = QtWidgets.QComboBox(self)
        self.exampleText = QtWidgets.QLabel(self)
        self.exampleText.setText("Add example of type")
        self.addExamplelayout = QtWidgets.QHBoxLayout()
        self.addExamplelayout.addWidget(self.exampleText)
        self.dropdown.addItem("Snake")
        self.dropdown.addItem("Rectangle")
        self.dropdown.addItem("Circle")
        self.addExamplelayout.addWidget(self.dropdown)
        self.addExamplelayout.addWidget(self.pushButton)


        self.addGestureText = QtWidgets.QLabel(self)
        self.addGestureText.setText("Add Gesture of type")
        self.addGestureLayout = QtWidgets.QHBoxLayout()
        self.addGestureLayout.addWidget(self.addGestureText)
        self.gestureInput = QtWidgets.QLineEdit()
        self.gestureInput.setPlaceholderText("Add symbol/gesture of type")
        self.addGestureLayout.addWidget(self.gestureInput)

        self.addGestureLayout.addWidget(self.addGestureButton)




        self.resultText = QtWidgets.QLabel(self)
        self.resultText.setText("Result: ")
        self.resultOutputText = QtWidgets.QLabel(self)
        self.resultLayout = QtWidgets.QHBoxLayout()
        self.resultLayout.addWidget(self.resultText)
        self.resultLayout.addWidget(self.resultOutputText)


        self.addExamplelayout.setAlignment(QtCore.Qt.AlignBottom)
        self.addGestureLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.resultLayout.setAlignment(QtCore.Qt.AlignBottom)

        self.layout.addLayout(self.addExamplelayout)

        self.layout.addLayout(self.addGestureLayout)
        self.layout.addLayout(self.resultLayout)
        self.layout.setAlignment(QtCore.Qt.AlignBottom)


        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle('$1 Recognizer')
        QtGui.QCursor.setPos(self.mapToGlobal(
            QtCore.QPoint(self.start_pos[0], self.start_pos[0])))
        self.show()




    def mousePressEvent(self, ev):
        #print("clicked")
        self.draw = True

    def mouseReleaseEvent(self, ev):
        #print("release")
        self.draw = False
        #print("relese", self.coordinates)
        self.resampledPoints = self.resample(self.coordinates, self.pointNumber)
        angle = self.indicativeAngle(self.resampledPoints)
        self.rotatedPoints = self.rotateBy(self.resampledPoints, -angle)
        #print(self.newPointsToDraw)
        self.drawNewPoints = True





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
            if self.drawNewPoints is True:
                print("Draw is True")
                self.drawNewTargetPoints(qp)
                self.drawNewPoints = False

            qp.end()

    def drawNewTargetPoints(self, qp):
        qp.setBrush(QtGui.QColor(0, 200, 0))
        for i in range(len(self.newPointsToDraw) - 1):
            qp.drawLine(self.newPointsToDraw[i][0], self.newPointsToDraw[i][1], self.newPointsToDraw[i + 1][0], self.newPointsToDraw[i +1][1])



    def drawtarget(self, qp):
        qp.setBrush(QtGui.QColor(0, 200, 0))
        for i in range(len(self.coordinates) - 1):
            qp.drawLine(self.coordinates[i][0], self.coordinates[i][1], self.coordinates[i + 1][0], self.coordinates[i +1][1])

    def resample(self, points, numberOfPoints):
        intervalLength = self.pathLength(points) / float(numberOfPoints -1)
        d = 0.0
        newpoints = [points[0]]
        newpoints.append(points[0])
        for i in range(1, len(points)):
           # print("punkte", points[i-1], points[i])
            distance = self.distance(points[i - 1], points[i])
           # print("distance", distance)
            if distance + d >= intervalLength:
            #    print("im if")
                self.q = [0.0, 0.0]
                self.q[0] = points[i-1][0] + float((intervalLength - d) / distance) * (points[i][0] - points[i-1][0])
                self.q[1] = points[i-1][1] + float((intervalLength - d) / distance) * (points[i][1] - points[i-1][1])
                newpoints.append(self.q)
                points.insert(i, self.q)
                d = 0.0
            else:
                d += distance

        if len(newpoints) == numberOfPoints -1:
            newpoints.append(points[0])

        print(len(newpoints), self.pointNumber)
        return newpoints


    def point(self, x, y):
        self.X = x
        self.Y = y

    def pathLength(self, points):
        d = 0.0
        for i in range(1, len(points)):
            d = d + self.distance(points[i - 1], points[i])
        return d

    def distance(self, p1, p2):
      #  print("fehlersuche", p1, p2)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return float(np.sqrt(dx * dx + dy * dy))

    def indicativeAngle(self, points):
        centroid = self.centroid(points)
        rotation_angle = np.arctan2(centroid[1] - points[0][1], centroid[0]-points[0][0])
        return rotation_angle

    def rotateBy(self, points, radians):
        centroid = self.centroid(points)
        cos = np.cos(radians)
        sin = np.sin(radians)
        newPoints = np.zeros((1,2))
        for i in range(len(points)):
            q = np.array([0.0, 0.0])
            q[0] = (points[i][0] - centroid[0]) * cos - (points[i][1] - centroid[1]) * sin + centroid[0]
            q[1] = (points[i][0] - centroid[0]) * sin + (points[i][1] - centroid[1]) * cos + centroid[1]
            newPoints = np.append(newPoints, [q], 0)

        print("newpoints", newPoints)
        return newPoints

    def rotate2D(self, points, count, ang=np.pi/4):
        return np.dot(np.array(points)-count, np.array([[np.cos(ang), np.sin(ang)], [-np.sin(ang), np.cos(ang)]])) + count


    def scaleToSquare(self, points):
        maxX, maxY = np.max(points, 0)
        minX, minY = np.min(points, 0)
        b_width = maxX - minX
        b_height = maxY - minY
        new_points = np.zeros((1,2))
        for point in points:
            q = np.array([0.0, 0.0])
            q[0] = point[0] * (self.square_size / b_width)
            q[1] = point[1] * (self.square_size / b_height)
            new_points = np.append(new_points, [q], 0)
        return new_points[1:]

    def centroid(self, points):
        centroid = np.mean(points,0)
        return centroid

def main():
    app = QtWidgets.QApplication(sys.argv)
    #application = QtGui.QD
    w = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
