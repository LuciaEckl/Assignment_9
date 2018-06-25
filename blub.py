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
        self.wm = None
        self.setGeometry(0, 0, 1280, 720)
        self.connect_wiimote()
        self.show()

    def connect_wiimote(self):
        self.wm = wiimote.connect("B8:AE:6E:1B:AD:A0")

        if self.wm is not None:
            self.wm.ir.register_callback(self.process_wiimote_ir_data)

    def process_wiimote_ir_data(self,event):
        if len(event) == 4:
            leds = []

            for led in event:
                leds.append((led["x"], led["y"]))
            P, DEST_W, DEST_H = (1024 /2, 768/2), 1024, 768
            try:
            #print("dest", DEST_H)
                # x,y = Transform.projective_transform(P, leds, DEST_W, DEST_H)

                x, y = Transform().transform(P, leds, DEST_W, DEST_H)
            except Exception as e:
                print(e)
                x = y = -1

            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x,y)))

            
class Transform():


    #https://stackoverflow.com/questions/37111798/how-to-sort-a-list-of-x-y-coordinates
    def transform(self, P, leds, W, H):
        WIIMOTE_IR_CAM_WIDTH, WIIMOTE_IR_CAM_HEIGHT = 1024, 768
        # A = kleinesx, kleines y, B = kleines x, großes Y, C = großes X, großes Y, D= großes X, kleines Y
        A = leds[0]
        B = leds[1]
        C = leds[2]
        D = leds[3]

        points = [A, B, C, D]
        print(points)
        points = sorted(points, key=lambda k: k[0])

        if points[0][1] < points[1][1]:
            A = points[0]
            B = points[1]
        else:
            A = points[1]
            B = points[0]

        if points[2][1] < points[3][1]:
            D = points[2]
            C = points[3]
        else:
            D = points[3]
            C = points[2]


        #print(points)
        scoords = [points[0], points[1], points[2], points[3]]
        self.source_points_123 = np. matrix([[A[0], B[0], C[0]],
                                             [A[1], B[1], C[1]],
                                             [ 1,   1,   1]])
        self.source_point_4 = [[D[0]],
                              [D[1]],
                              [1]]

        scale_to_source = np.linalg.solve(self.source_points_123, self.source_point_4)
        l, m, t = [float(x) for x in scale_to_source]

        unit_to_source = np.matrix([[l * A[0], m * B[0], t * C[0]],
                         [l * A[1], m * B[1], t* C[1]],
                         [ l, m, t]])

        DESTINATION_SCREEN_WIDTH = W
        DESTINATION_SCREEN_HEIGHT = H

        A2 = 0, DESTINATION_SCREEN_HEIGHT
        B2 = 0, 0
        C2 = DESTINATION_SCREEN_WIDTH, 0
        D2 = DESTINATION_SCREEN_WIDTH, DESTINATION_SCREEN_HEIGHT

        dcoords = [A2, B2, C2, D2]

        dest_points_123 = np.matrix([[A2[0], B2[0], C2[0]],
                                 [A2[1], B2[1], C2[1]],
                                 [ 1,   1,   1]])

        dest_point_4 = np.matrix([[D2[0]],
                       [D2[1]],
                       [ 1 ]])

        scale_to_dest = np.linalg.solve(dest_points_123, dest_point_4)
        l,m,t = [float(x) for x in scale_to_dest]

        unit_to_dest = np.matrix([[l * A2[0], m * B2[0], t * C2[0]],
                       [l * A2[1], m * B2[1], t * C2[1]],
                       [ l,m ,      t ]])

        source_to_unit = np.linalg.inv(unit_to_source)
        source_to_dest = unit_to_dest @ source_to_unit

        x, y, z = [float(w) for w in (source_to_dest @ np.matrix([[512],
                                                     [384],
                                                     [ 1 ]]))]

        x = x / z
        y = y / z
        return x, y

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = QtGui.QD
    w = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
