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
from operator import itemgetter


class Window(QtWidgets.QWidget):

    def __init__(self, app):
        super().__init__()
        self.start_pos = (0, 0)
        self.mouseMovePos = (0, 0)
        self.draw = False
        self.coordinates = []
        self.pointNumber = 64
        self.X = 0
        self.Y = 0
        self.resampledPoints = []
        self.square_size = 100
        self.drawNewPoints = False
        self.rotatedPoints = []
        self.scale = []
        self.origin = (100,100)
        self.toOrigin = []
        self.addNewDefinedGetureButtonText = "Add gesture/symbol"
        self.addExistingGestureButtonText = "Add Symbol"
        self.resultButtonText = "Result"
        self.gestureInputText = ""
        self.dropdown = ""
        self.points = []
        self.transform = Transform()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.gestures = []
        self.gestureName = []
        self.gestureInput = ""
        self.resultOutputText = ""
        self.angle_range = 45
        self.angle_step = 2.0
        self.category = -1
        self.wm = 0
        self.checkDraw = False
        self.app = app
        self.resultButtonValues = []
        self.addSymbolButtonValues = []
        self.addGestureButtonValues = []
        self.dropdownValue = []
        self.initUI()

        try:
            self.connect_wiimote()
        except:
            print("not connected To Wiimote")


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
        self.pushButton = QtWidgets.QPushButton(self.addExistingGestureButtonText)
        self.addGestureButton = QtWidgets.QPushButton(self.addNewDefinedGetureButtonText)
        self.resultButton = QtWidgets.QPushButton(self.resultButtonText)
        self.exampleText.setText("Add example of type")
        self.addExamplelayout = QtWidgets.QHBoxLayout()
        self.addExamplelayout.addWidget(self.exampleText)
        self.dropdown.addItem("Snake")
        self.dropdown.addItem("Rectangle")
        self.dropdown.addItem("Circle")
        self.addExamplelayout.addWidget(self.dropdown)
        self.addExamplelayout.addWidget(self.pushButton)
        self.pushButton.clicked.connect(self.clickedButton)
        self.dropdown.activated.connect(self.getTextFromDropdown)
        self.addGestureText = QtWidgets.QLabel(self)
        self.addGestureText.setText("Add Gesture of type")
        self.addGestureLayout = QtWidgets.QHBoxLayout()
        self.addGestureLayout.addWidget(self.addGestureText)
        self.gestureInput = QtWidgets.QLineEdit("", self)
        self.gestureInput.setPlaceholderText("Add symbol/gesture of type")

        self.gestureInput.selectAll()
        self.gestureInput.setFocus()
        #print(self.gestureInput.focusPolicy())


        self.addGestureLayout.addWidget(self.gestureInput)

        self.addGestureLayout.addWidget(self.addGestureButton)
        self.addGestureButton.clicked.connect(self.addNewGesture)



        self.resultText = QtWidgets.QLabel(self)
        self.resultText.setText("Result: ")
        self.resultOutputText = QtWidgets.QLabel(self)
        self.resultLayout = QtWidgets.QHBoxLayout()

        self.resultLayout.addWidget(self.resultText)
        self.resultLayout.addWidget(self.resultOutputText)
        self.resultLayout.addWidget(self.resultButton)
        self.resultButton.clicked.connect(self.resultClicked)

        self.addGestureButtonValues.append(self.addGestureButton.pos().x())
        self.addGestureButtonValues.append(self.addGestureButton.pos().y())
        self.addGestureButtonValues.append(self.addGestureButton.width())
        self.addGestureButtonValues.append(self.addGestureButton.height())
        self.addSymbolButtonValues.append(self.pushButton.pos().x())
        self.addSymbolButtonValues.append(self.pushButton.pos().y())
        self.addSymbolButtonValues.append(self.pushButton.width())
        self.addSymbolButtonValues.append(self.pushButton.height())
        self.resultButtonValues.append(self.resultButton.pos().x())
        self.resultButtonValues.append(self.resultButton.pos().y())
        self.resultButtonValues.append(self.resultButton.width())
        self.resultButtonValues.append(self.resultButton.height())
        self.dropdownValue.append(self.dropdown.pos().x())
        self.dropdownValue.append(self.dropdown.pos().y())
        self.dropdownValue.append(self.dropdown.width())
        self.dropdownValue.append(self.dropdown.height())

        print(self.addGestureButton.pos())

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


    def getTextFromDropdown(self):
        self.gestureInput.selectAll()
        self.gestureInput.setFocus()



    def connect_wiimote(self):
        self.wm = wiimote.connect("B8:AE:6E:1B:AD:A0")

        if self.wm is not None:
            self.wm.ir.register_callback(self.process_wiimote_ir_data)
            self.wm.buttons.register_callback(self.getpressedButton)
            #self.wm.buttons.unregister_callback(self.getReleasedButton)

   # def getReleasedButton(self, ev):
      #  if self.wm.buttons["B"]:



    def getpressedButton(self, ev):
        x = QtGui.QCursor.pos().x()
        y = QtGui.QCursor.pos().y()
        if self.wm.buttons["B"]:
            if self.draw is False:
                self.coordinates = []
                self.update()
                self.gestureInput.selectAll()
                self.gestureInput.setFocus()
            self.draw = True
            if self.draw is True:

                self.mouseMovePos = x, y
                self.coordinates.append(self.mouseMovePos)
                self.update()
                self.checkDraw = True

        else:
            if len(self.coordinates) > 0 and self.checkDraw is True:
                self.draw = False
                self.points = self.resample(self.coordinates, self.pointNumber)
                angle = self.indicativeAngle(self.points)
                self.points = self.rotateBy(self.points, -angle)
                self.points = self.scaleToSquare(self.points)
                self.points = self.translateTo(self.points, self.origin)
                self.points = self.points
                self.update()
                self.checkDraw = False

        if self.wm.buttons["A"]:
            print(x, self.resultButtonValues[0], self.resultButtonValues[2])
           # self.addGestureButton.clicked.connect(self.clickedButton)
            self.app.postEvent(self.addGestureButton, QtGui.QMouseEvent(QtGui.QMouseEvent.MouseButtonPress, QtCore.QPoint(x, y), QtCore.Qt.LeftButton, QtCore.Qt.NoButton, QtCore.Qt.NoModifier))
            #self.resultButtonValues = []
            #self.addSymbolButtonValues = []
            #self.addGestureButtonValues = []
            #self.dropdownValue = []
            if x > self.resultButtonValues[0] and x < self.resultButtonValues[0] + self.resultButtonValues[2] and y > self.resultButtonValues[1] and y < self.resultButtonValues[1] + self.resultButtonValues[3]:
                print("result")
                self.resultClicked
            if x > self.addSymbolButtonValues[0] and x < self.addSymbolButtonValues[0] + self.addSymbolButtonValues[2] and y > self.addSymbolButtonValues[1] and y < self.addSymbolButtonValues[1] + self.addSymbolButtonValues[3]:
                print("addNewGesture")
                self.pushButton
            if x > self.addGestureButtonValues[0] and x < self.addGestureButtonValues[0] + self.addGestureButtonValues[2] and y > self.addGestureButtonValues[1] and y < self.addGestureButtonValues[1] + self.addGestureButtonValues[3]:
                print("Symbol")
                self.addNewGesture()

               # QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x,y)))


    def process_wiimote_ir_data(self,event):
        if len(event) == 4:
            leds = []

            for led in event:
                leds.append((led["x"], led["y"]))
            P, DEST_W, DEST_H = (1024 /2, 768/2), 1024, 768

        #while True:
         #   if self.wm.buttons["B"]:
          #      print("Gedrückt")

            try:
                # x,y = Transform.projective_transform(P, leds, DEST_W, DEST_H)

                x, y = Transform().transform(P, leds, DEST_W, DEST_H)
            except Exception as e:
                print(e)
                x = y = -1

            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x,y)))

    def resultClicked(self, ev):
        # Wir müssen noch abfragen, ob schon eine Geste Trainiert wurde
        if len(self.points) > 0 and len(self.gestures) > 0:
            self.category = self.recognize(self.points, self.gestures)
            self.category = sorted(self.category, key=itemgetter(0))[0][1]
            self.prediction()
           # print(self.category)
        elif len(self.points) == 0:
            self.resultOutputText.setText("no Gesture found")
        elif len(self.gestures) == 0:
            self.resultOutputText.setText("no Gestures trained")


    def addNewGesture(self, ev):
        self.gestureInput.selectAll()
        self.gestureInput.setFocus()
        #if (sender.text() == self.addNewDefinedGetureButtonText) and (len(self.gestureInput.text()) > 0):
            # die neu Erstellte Kategorie in die Dropdownliste hinzufügen
            # die neue Geste zu der neuen Kategorie anlegen
            #self.dropdown.addItem("Geschaft")
            # text aus dem Textfeld rausholen mit self.gestureInput.text()
            # hinzufügen der neuen Kategrie in die Dropdownliste

          #  print("Neue Kategorie hinzufügen")
          #  self.gestures.append([self.points])
           # print(self.gestures, "Gesten", "länge Gesten", len(self.gestures))
           # self.gestureName.append(self.gestureInput.text())
        if self.gestureInput.text() not in self.gestureName:
            self.gestureName.append(self.gestureInput.text())
            self.gestures.append([self.points])
            self.dropdown.addItem(self.gestureInput.text())
        else:

            index = self.gestureName.index(self.gestureInput.text())

            self.gestures[index].append(self.points)
        #    print("Index", index, self.gestures[index], len(self.gestures[index]), len(self.gestures))




    def clickedButton(self, ev):
        #print("geklickt")
        #sender = self.sender()
        self.gestureInput.selectAll()
        self.gestureInput.setFocus()
        #if sender.text() == self.addExistingGestureButtonText:
            # hier soll die Geste zu den bestehenden Kategrorien in der Dropdownliste Hinzugefügt werden
            # aktueller Text der Dropdownliste self.dropdown.currentText()
            # self.points ist das gekürzte Array
           # print("Geste zu bestehender Kategorie hinzufügen", self.dropdown.currentText())
        if self.dropdown.currentText() not in self.gestureName:
            self.gestureName.append(self.dropdown.currentText())
            self.gestures.append([self.points])
        else:

            index = self.gestureName.index(self.dropdown.currentText())

            self.gestures[index].append(self.points)
           # print("Index", index, self.gestures[index], len(self.gestures[index]), len(self.gestures))

           # print(self.gestures, self.gestureName)






    def prediction(self):
        #print("predict")
        result = self.gestureName[self.category]
        self.resultOutputText.setText(result)



    def mousePressEvent(self, ev):
        self.coordinates = []
        #self.gestureInput.selectAll()
        #self.gestureInput.setFocus()
        self.update()
        self.gestureInput.selectAll()
        self.gestureInput.setFocus()
        self.draw = True

    def mouseReleaseEvent(self, ev):
        self.draw = False
        self.points = self.resample(self.coordinates, self.pointNumber)
        angle = self.indicativeAngle(self.points)
        self.points = self.rotateBy(self.points, -angle)
        self.points = self.scaleToSquare(self.points)
        self.points = self.translateTo(self.points, self.origin)
        self.points = self.points
        self.update()






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
            elif self.drawNewPoints is True:
                self.drawNewTargetPoints(qp)
                self.drawNewPoints = False

            qp.end()

    def drawNewTargetPoints(self, qp):
        qp.setBrush(QtGui.QColor(0, 200, 0))
        for i in range(len(self.points) - 1):
            qp.drawLine(self.points[i][0], self.points[i][1], self.points[i + 1][0], self.points[i +1][1])



    def drawtarget(self, qp):
        qp.setBrush(QtGui.QColor(0, 200, 0))
        for i in range(len(self.coordinates) - 1):
            qp.drawLine(self.coordinates[i][0], self.coordinates[i][1], self.coordinates[i + 1][0], self.coordinates[i +1][1])


    def recognize(self, points, templates):
        b = math.inf
        selected_template = None
        resultArray = []
        for i in range(len(templates)):
            for j in range(len(templates[i])):
                #print(templates[i][j], len(templates), len(templates[i][j]))
                d = self.distanceAtBestAngle(points, templates[i][j], -self.angle_range, self.angle_range, self.angle_step)
                if(d < b):
                    b = d
                    #print("D", d, i, j)
                    resultArray.append([d, i])

        return resultArray

    def distanceAtBestAngle(self, points, T, a, b, threshold):
        phi = (-1 + 5**0.5)/2
        x1 = phi * a + (1.0 - phi) * b
        f1 = self.distanceAtAngle(points, T, x1)
        x2 = (1.0 - phi) * a + phi * b
        f2 = self.distanceAtAngle(points, T, x2)
        while (abs(b - a) > threshold):
            if f1 < f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = phi * a + (1.0 - phi) * b
                f1 = self.distanceAtAngle(points, T, x1)
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = (1.0 - phi) * a + phi * b
                f2 = self.distanceAtAngle(points, T, x2)
        return min(f1, f2)
            #int(f1 if f1 < f2 else f2)

    def distanceAtAngle(self, points, T, radians):
        newpoints = self.rotateBy(points, radians)
        return self.pathDistance(newpoints, T)


    def pathDistance(self, pts1, pts2):
        d = 0.0
        for i in range(len(pts1)):
            d += self.distance(pts1[i], pts2[i])
        return d/len(pts1)

    def resample(self, points, numberOfPoints):
        intervalLength = self.pathLength(points) / float(numberOfPoints -1)
        D = 0.0
        newpoints = [points[0]]
       # newpoints.append(points[0])
        i = 1
        while i < len(points):
            point = points[i -1]
            next_point = points[i]
            d = self.distance(point, next_point)
            if d + D >= intervalLength:
                delta_distance = float((intervalLength - D) / d)
                self.q = [0.0, 0.0]
                self.q[0] = points[i-1][0] + delta_distance * (points[i][0] - points[i-1][0])
                self.q[1] = points[i-1][1] + delta_distance * (points[i][1] - points[i-1][1])
                newpoints.append(self.q)
                points.insert(i, self.q)
                D = 0.0
            else:
                D += d
            i +=1

        if len(newpoints) == numberOfPoints -1:
            newpoints.append(points[-1])

        return newpoints


    def point(self, x, y):
        self.X = x
        self.Y = y

    def pathLength(self, points):
        d = 0.0
        for i in range(1, len(points)):
            d += self.distance(points[i - 1], points[i])
        return d

    def distance(self, p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return float(math.sqrt(dx * dx + dy * dy))

    def indicativeAngle(self, points):
        centroid = self.centroid(points)
        rotation_angle = math.atan2(centroid[1] - points[0][1], centroid[0]-points[0][0])
        return rotation_angle

    def rotateBy(self, points, radians):
        centroid = self.centroid(points)

        cos = math.cos(radians)
        sin = math.sin(radians)
        newPoints = []
        for i in range(len(points)):
            #q = [0.0, 0.0]
            qx = (points[i][0] - centroid[0]) * cos - (points[i][1] - centroid[1]) * sin + centroid[0]
            qy = (points[i][0] - centroid[0]) * sin + (points[i][1] - centroid[1]) * cos + centroid[1]

            newPoints.append([qx, qy])


        return newPoints


    def scaleToSquare(self, points):
        b = self.boundingBox(points)
        newpoints = []
        for i in range(len(points)):
            qx = points[i][0] * (self.square_size / b[2])
            qy = points[i][1] * (self.square_size / b[3])
            newpoints.append([qx, qy])
        return newpoints

    #    minX = float(math.inf)
    #    maxX = float(-math.inf)
    #    minY = float(math.inf)
    #    maxY = float(-math.inf)

    #    for i in range(len(points)):
    #        minX = min(minX, points[i][0])
    #        minY = min(minY, points[i][1])
     #       maxX = max(maxX, points[i][0])
     #       maxY = max(maxY, points[i][1])
     #   new_points = []
      #  b_width = maxX - minX
      #  b_height = maxY - minY
      #  for point in points:
      #      #q = [0.0, 0.0]
      #      qx = point[0] * (self.square_size / b_width)
       #     qy = point[1] * (self.square_size / b_height)
       #     new_points.append([qx, qy])

     #   return new_points[1:]

    def boundingBox(self, points):
        minX = +math.inf
        maxX = -math.inf
        minY = +math.inf
        maxY = -math.inf
        for i in range(len(points)):
            minX = min(minX, points[i][0])
            minY = min(minY, points[i][1])
            maxX = max(maxX, points[i][0])
            maxY = max(maxY, points[i][1])

        return [minX, minY, maxX - minX, maxY - minY]

    def centroid(self, points):
        #xs, ys = zip(*points)

        #return [sum(xs) / len(xs), sum(ys) / len(ys)]
        x = 0.0
        y = 0.0
        for i in range(len(points)):
            x += points[i][0]
            y += points[i][1]

        x = x / len(points)
        y = y / len(points)
        return [x, y]


    def translateTo(self, points, origin):

        centroid = self.centroid(points)
        newpoints = []
        for i in range(len(points)):
            qx = points[i][0] + origin[0] - centroid[0]
            qy = points[i][1] + origin[1] - centroid[1]
            newpoints.append([qx, qy])
        self.drawNewPoints = True
        return newpoints




def main():
    app = QtWidgets.QApplication(sys.argv)
    #application = QtGui.QD
    w = Window(app)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
