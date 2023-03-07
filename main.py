import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtCore import Qt

import sqlite3

app = QApplication(sys.argv)

scene = QGraphicsScene(0, 0, 1100, 200)
solid_pen = QPen(Qt.GlobalColor.black)
solid_pen.setStyle(Qt.PenStyle.SolidLine)
solid_pen.setWidth(1)

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("SELECT profile_depth, length FROM part WHERE PartId=1")
dimensions = cursor.fetchone()
print(dimensions)

scale = 1000/dimensions[1]
depth = dimensions[0]*scale
length = dimensions[1]*scale

front_outline = QGraphicsRectItem(0, 0, length, depth)
front_outline.setPos(50, 50)
front_outline.setPen(solid_pen)

cursor.execute("SELECT flange_thickness FROM part WHERE PartId=1")
flange_thickness = cursor.fetchone()[0]*scale

top_flange = QGraphicsLineItem(0, 0, length, 0)
top_flange.setPos(70,70)
top_flange.setPen(solid_pen)


scene.addItem(front_outline)
scene.addItem(top_flange)




view = QGraphicsView(scene)
view.show()
app.exec()