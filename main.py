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
from PyQt6.QtWidgets import (
    QStyle, QApplication, QMainWindow, QToolBar, QGridLayout, QFileDialog, QWidget,
    QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
)
from PyQt6.QtGui import QAction, QIcon, QBrush, QPen
from PyQt6.QtCore import Qt

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

        export_icon = QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_peddimat_action = QAction(export_icon, "&export peddimat files", self)
        export_peddimat_action.triggered.connect(self.export_peddimat)
        toolbar.addAction(export_peddimat_action)

        remove_list_item_icon = QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        remove_list_item_action = QAction(remove_list_item_icon, "&Remove selected", self)
        remove_list_item_action.triggered.connect(self.remove_list_item)
        toolbar.addAction(remove_list_item_action)

        self.part_list_widget = QListWidget()
        self.part_list_widget.setFixedWidth(150)
        self.part_list_widget.currentItemChanged.connect(self.part_list_index_changed)

        self.create_hole_info_table()

        self.solid_pen = QPen(Qt.GlobalColor.white)
        self.solid_pen.setStyle(Qt.PenStyle.SolidLine)
        self.solid_pen.setWidth(1)

        self.dashed_pen = QPen(Qt.GlobalColor.white)
        self.dashed_pen.setStyle(Qt.PenStyle.DashLine)
        self.dashed_pen.setWidth(1)

        self.create_part_views()


        layout = QGridLayout()
        layout.addWidget(self.part_list_widget, 0, 0, 0, 1)
        layout.addWidget(self.hole_info_table, 0, 1, 0, 1)
        layout.addWidget(self.top_view, 0, 2)
        layout.addWidget(self.front_view, 1, 2)
        layout.addWidget(self.bottom_view, 2, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def populate_part_list_widget(self):
        self.part_list_widget.clear()
        partmarks = self.part_database.get_partmarks_list()
        self.part_list_widget.addItems(partmarks)
    
    def part_list_index_changed(self, index):
        if index:
            partmark = index.text()
            self.populate_hole_info_table(partmark)
            self.draw_part(partmark)
            print(partmark)
    
    def remove_list_item(self):
        current_item = self.part_list_widget.currentItem()
        if current_item:
            partmark = current_item.text()
            self.hole_database.remove_data(partmark)
            self.part_database.remove_data(partmark)
            self.part_list_widget.takeItem(self.part_list_widget.row(current_item))


    def create_hole_info_table(self):
        self.hole_info_table = QTableWidget(0, 4)
        self.hole_info_table.setFixedWidth(350)
        labels = ["Surface", "Size[mm*10]", "X[mm*1000]", "Y[mm*1000]"]
        self.hole_info_table.setHorizontalHeaderLabels(labels)
        for i, label in enumerate(labels):
            self.hole_info_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def populate_hole_info_table(self, partmark):
        self.hole_info_table.setRowCount(0)

        hole_info_list = self.hole_database.get_hole_info_list(partmark)
        if hole_info_list:
            for hole in hole_info_list:
                row_position = self.hole_info_table.rowCount()
                self.hole_info_table.insertRow(self.hole_info_table.rowCount())
                self.hole_info_table.setItem(row_position, 0, QTableWidgetItem(hole[0]))
                self.hole_info_table.setItem(row_position, 1, QTableWidgetItem(hole[1]))
                self.hole_info_table.setItem(row_position, 2, QTableWidgetItem(str(hole[2])))
                self.hole_info_table.setItem(row_position, 3, QTableWidgetItem(str(hole[3])))
    
    def create_part_views(self):
        self.top_scene = QGraphicsScene(0, 0, 1100, 300)
        self.front_scene = QGraphicsScene(0, 0, 1100, 300)
        self.bottom_scene = QGraphicsScene(0, 0, 1100, 300)

        self.top_view = QGraphicsView(self.top_scene)
        self.front_view = QGraphicsView(self.front_scene)
        self.bottom_view = QGraphicsView(self.bottom_scene)

        self.views = (self.top_view, self.front_view, self.bottom_view)
        self.scenes = (self.top_scene, self.front_scene, self.bottom_scene)

        for view in self.views:
            view.setMinimumSize(1110, 320)

        for scene in self.scenes:
            scene.setBackgroundBrush(Qt.GlobalColor.black)

    
    def draw_part(self, partmark):
        part_geometry = self.part_database.get_part_geometry(partmark)
        scale = 200/part_geometry["profile_depth"]

        scene_width = 100 + part_geometry["length"]*scale
        for scene in self.scenes:
            scene.setSceneRect(0, 0, scene_width, scene.height())

        self.draw_part_top(scale, part_geometry)
        self.draw_part_front(scale, part_geometry)
        self.draw_part_bottom(scale, part_geometry)
    
    def draw_part_top(self, scale, part_geometry):
        self.top_scene.clear()

        height = part_geometry["flange_height"]*scale
        length = part_geometry["length"]*scale
        outline = QGraphicsRectItem(0, 0, length, height)
        outline.setPos(50, 50)
        outline.setPen(self.solid_pen)
        self.top_scene.addItem(outline)

    def draw_part_front(self, scale, part_geometry):
        self.front_scene.clear()

        depth = part_geometry["profile_depth"]*scale
        length = part_geometry["length"]*scale

        outline = QGraphicsRectItem(0, 0, length, depth)
        outline.setPos(50, 50)
        outline.setPen(self.solid_pen)
        self.front_scene.addItem(outline)

        flange_thickness = part_geometry["flange_thickness"]*scale
        top_flange_y = 50 + flange_thickness
        bottom_flange_y = 50 + depth - flange_thickness
        top_flange = QGraphicsLineItem(50, top_flange_y, 50+length, top_flange_y)
        bottom_flange = QGraphicsLineItem(50, bottom_flange_y, 50+length, bottom_flange_y)
        top_flange.setPen(self.solid_pen)
        bottom_flange.setPen(self.solid_pen)
        self.front_scene.addItem(top_flange)
        self.front_scene.addItem(bottom_flange)



    def draw_part_bottom(self, scale, part_geometry):
        pass
    
    def save_to_database(self, filepaths):
        self.database_connection.delete_old()
        self.part_database = PartDatabase(self.database_connection)
        self.part_database.create_table()
        self.hole_database = HoleDatabase(self.database_connection)
        self.hole_database.create_table()

        for filepath in filepaths:
            steel_part = SteelPart(filepath)
            self.part_database.insert_data(steel_part)
            for hole in steel_part.holes:
                self.hole_database.insert_data(hole)

    def import_dstv(self):
        filepaths = QFileDialog.getOpenFileNames(self, caption="select .nc1 files", filter="*.nc1")[0]
        self.save_to_database(filepaths)
        self.populate_part_list_widget()

    def export_peddimat(self):
        print("export peddimat")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()


if __name__ == "__main__":
    main()
