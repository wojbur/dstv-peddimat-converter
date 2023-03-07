import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtCore import Qt

import sqlite3

app = QApplication(sys.argv)

scene = QGraphicsScene(0, 0, 1100, 200)
pen = QPen(Qt.GlobalColor.black)
pen.setStyle(Qt.PenStyle.SolidLine)


connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("SELECT profile_depth, length FROM part WHERE PartId=1")
dimensions = cursor.fetchone()
print(dimensions)

scale = 1000/dimensions[1]
depth = dimensions[0]*scale
length = dimensions[1]*scale

rect = QGraphicsRectItem(0, 0, length, depth)
rect.setPos(50, 50)

# brush = QBrush(Qt.GlobalColor.red)
# rect.setBrush(brush)

pen = QPen(Qt.GlobalColor.black)
pen.setStyle(Qt.PenStyle.DashLine)
pen.setWidth(1)
rect.setPen(pen)

scene.addItem(rect)





view = QGraphicsView(scene)
view.show()
app.exec()