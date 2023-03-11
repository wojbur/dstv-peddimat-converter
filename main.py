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
    QStyle, QApplication, QMainWindow, QToolBar, QGridLayout, QFileDialog, QWidget, QListWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QAction, QIcon

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

        layout = QGridLayout()
        layout.addWidget(self.part_list_widget, 0, 0)
        layout.addWidget(self.hole_info_table, 0, 1)

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
