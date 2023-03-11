# import sys
# from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
# from PyQt6.QtGui import QBrush, QPen
# from PyQt6.QtCore import Qt

# import sqlite3

# app = QApplication(sys.argv)

# scene = QGraphicsScene(0, 0, 1100, 200)
# scene.setBackgroundBrush(Qt.GlobalColor.black)
# solid_pen = QPen(Qt.GlobalColor.white)
# solid_pen.setStyle(Qt.PenStyle.SolidLine)
# solid_pen.setWidth(1)

# connection = sqlite3.connect("database.db")
# cursor = connection.cursor()

# cursor.execute("SELECT profile_depth, length FROM part WHERE PartId=1")
# dimensions = cursor.fetchone()
# print(dimensions)

# scale = 1000/dimensions[1]
# depth = dimensions[0]*scale
# length = dimensions[1]*scale

# front_outline = QGraphicsRectItem(0, 0, length, depth)
# front_outline.setPos(50, 50)
# front_outline.setPen(solid_pen)

# cursor.execute("SELECT flange_thickness FROM part WHERE PartId=1")
# flange_thickness = cursor.fetchone()[0]*scale

# top_flange = QGraphicsLineItem(0, 0, length, 0)
# top_flange.setPos(70,70)
# top_flange.setPen(solid_pen)


# scene.addItem(front_outline)
# scene.addItem(top_flange)




# view = QGraphicsView(scene)
# view.show()
# app.exec()

import sys
from PyQt6.QtWidgets import QStyle, QApplication, QMainWindow, QFileDialog, QWidget, QToolBar, QGridLayout, QListView, QAbstractItemView
from PyQt6.QtGui import QAction, QStandardItem, QStandardItemModel, QIcon
from PyQt6.QtCore import QAbstractListModel

from db_controller import DatabaseConnection, PartDatabase, HoleDatabase
from dstv_decoder import SteelPart


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSTV-Peddimat Converter")
        self.show()

        self.database_connection = DatabaseConnection()

        toolbar = QToolBar("Import NC1")
        self.addToolBar(toolbar)

        import_icon = QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        import_dstv_action = QAction(import_icon, "&import dstv files", self)
        import_dstv_action.triggered.connect(self.import_dstv)
        toolbar.addAction(import_dstv_action)

        export_icon = QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        export_peddimat_action = QAction(export_icon, "&export peddimat files", self)
        export_peddimat_action.triggered.connect(self.export_peddimat)
        toolbar.addAction(export_peddimat_action)

        part_list_view = ListView()
        for i in range(100):
            text = str(i)
            item = QStandardItem(text)
            part_list_view.list_model.appendRow(item)

        layout = QGridLayout()
        layout.addWidget(part_list_view, 0, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def import_dstv(self):
        self.database_connection.delete_old()
        part_database = PartDatabase(self.database_connection)
        hole_database = HoleDatabase(self.database_connection)

        part_database.create_table()
        hole_database.create_table()

        filepaths = QFileDialog.getOpenFileNames(self, caption="select .nc1 files", filter="*.nc1")[0]
        for filepath in filepaths:
            steel_part = SteelPart(filepath)
            part_database.insert_data(steel_part)
            for hole in steel_part.holes:
                hole_database.insert_data(hole)

    def export_peddimat(self):
        print("export peddimat")

class ListView(QListView):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(250)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.list_model = QStandardItemModel()
        self.setModel(self.list_model)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()


if __name__ == "__main__":
    main()
