import sys
import os
from PyQt6.QtWidgets import (
    QStyle, QApplication, QMainWindow, QToolBar, QSlider, QGridLayout, QFileDialog, QWidget,
    QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QLabel, QSizePolicy
)
from PyQt6.QtGui import QAction, QIcon, QPen
from PyQt6.QtCore import Qt

from db_controller import DatabaseConnection, PartDatabase, HoleDatabase
from dstv_decoder import SteelPart

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSTV-Peddimat Converter")

        basedir = os.path.dirname(__file__)
        self.database_connection = DatabaseConnection(os.path.join(basedir, "current_session.db"))

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

        test_icon = QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        test_action = QAction(test_icon, "&Remove selected", self)
        test_action.triggered.connect(self.test)
        toolbar.addAction(test_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.scale = 0.05
        toolbar.addWidget(QLabel("ZOOM"))
        scale_slider = QSlider(Qt.Orientation.Horizontal)
        scale_slider.setValue(50)
        scale_slider.setMinimum(20)
        scale_slider.setMaximum(80)
        scale_slider.setFixedWidth(100)
        scale_slider.valueChanged.connect(self.scale_slider_changed)
        toolbar.addWidget(scale_slider)

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

        self.showMaximized()
    
    def test(self):
        for item in self.top_scene.items():
            item.moveBy(50, 50)
    
    def scale_slider_changed(self, value):
        print(value)
        self.scale = value/1000
        if self.part_list_widget.currentItem():
            partmark = self.part_list_widget.currentItem().text()
            self.draw_part(partmark)
    
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
        else:
            self.clear_scenes()

    def create_hole_info_table(self):
        self.hole_info_table = QTableWidget(0, 4)
        self.hole_info_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.hole_info_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
            view.setMinimumSize(800, 200)

        for scene in self.scenes:
            scene.setBackgroundBrush(Qt.GlobalColor.black)
    
    def clear_scenes(self):
        self.top_scene.clear()
        self.front_scene.clear()
        self.bottom_scene.clear()
    
    def draw_part(self, partmark):
        self.clear_scenes()
        part_geometry = self.part_database.get_part_geometry(partmark)

        scene_width = 100 + part_geometry["length"]*self.scale
        for scene in self.scenes:
            scene.setSceneRect(0, 0, scene_width, scene.height())

        self.draw_part_top(partmark, part_geometry)
        self.draw_part_front(partmark, part_geometry)
        self.draw_part_bottom(partmark, part_geometry)

        # Offset graphic items from view border
        for item in self.top_scene.items():
            item.moveBy(50, 50)
        for item in self.front_scene.items():
            item.moveBy(50, 50)
        for item in self.bottom_scene.items():
            item.moveBy(50, 50)
    
    def draw_part_top(self, partmark, part_geometry):
        height = part_geometry["flange_height"]*self.scale
        length = part_geometry["length"]*self.scale

        self.draw_holes_top(partmark)

        outline = QGraphicsRectItem(0, 0, length, height)
        outline.setPen(self.solid_pen)
        self.top_scene.addItem(outline)

        web_thickness = part_geometry["web_thickness"]*self.scale

        if part_geometry["profile_type"] == "B":
            top_web_y = height/2 - web_thickness/2
            bottom_web_y = height/2 + web_thickness/2
            top_web = QGraphicsLineItem(0, top_web_y, length, top_web_y)
            bottom_web = QGraphicsLineItem(0, bottom_web_y, length, bottom_web_y)
            top_web.setPen(self.dashed_pen)
            bottom_web.setPen(self.dashed_pen)
            self.top_scene.addItem(top_web)
            self.top_scene.addItem(bottom_web)
        
        if part_geometry["profile_type"] == "C":
            web_y = web_thickness
            web = QGraphicsLineItem(0, web_y, length, web_y)
            web.setPen(self.dashed_pen)
            self.top_scene.addItem(web)

    def draw_part_front(self, partmark, part_geometry):
        depth = part_geometry["profile_depth"]*self.scale
        length = part_geometry["length"]*self.scale

        self.draw_holes_front(partmark)

        outline = QGraphicsRectItem(0, 0, length, depth)
        outline.setPen(self.solid_pen)
        self.front_scene.addItem(outline)

        flange_thickness = part_geometry["flange_thickness"]*self.scale
        top_flange_y = flange_thickness
        bottom_flange_y = depth - flange_thickness
        top_flange = QGraphicsLineItem(0, top_flange_y, length, top_flange_y)
        bottom_flange = QGraphicsLineItem(0, bottom_flange_y, length, bottom_flange_y)

        if part_geometry["profile_type"] == "B" or part_geometry["profile_type"] == "C":
            top_flange.setPen(self.solid_pen)
            bottom_flange.setPen(self.solid_pen)
            self.front_scene.addItem(top_flange)
            self.front_scene.addItem(bottom_flange)

        elif part_geometry["profile_type"] == "T":
            top_flange.setPen(self.dashed_pen)
            self.front_scene.addItem(top_flange)
            self.front_scene.addItem(bottom_flange)
        else:
            self.front_scene.clear()
            
        
    def draw_part_bottom(self, partmark, part_geometry):
        height = part_geometry["flange_height"]*self.scale
        length = part_geometry["length"]*self.scale

        self.draw_holes_bottom(partmark, height)

        outline = QGraphicsRectItem(0, 0, length, height)

        outline.setPen(self.solid_pen)
        self.bottom_scene.addItem(outline)

        web_thickness = part_geometry["web_thickness"]*self.scale

        if part_geometry["profile_type"] == "B":
            top_web_y = height/2 - web_thickness/2
            bottom_web_y = height/2 + web_thickness/2
            top_web = QGraphicsLineItem(0, top_web_y, length, top_web_y)
            bottom_web = QGraphicsLineItem(0, bottom_web_y, length, bottom_web_y)
            top_web.setPen(self.dashed_pen)
            bottom_web.setPen(self.dashed_pen)
            self.bottom_scene.addItem(top_web)
            self.bottom_scene.addItem(bottom_web)
        
        if part_geometry["profile_type"] == "C":
            web_y = height - web_thickness
            web = QGraphicsLineItem(0, web_y, length, web_y)
            web.setPen(self.dashed_pen)
            self.bottom_scene.addItem(web)

    def draw_holes_top(self, partmark):
        hole_geometry_list = self.hole_database.get_hole_geometry_list(partmark, "top")
        if hole_geometry_list:
            for hole_geometry in hole_geometry_list:
                x_diameter = (hole_geometry[0]+hole_geometry[1])*self.scale
                y_diameter = (hole_geometry[0]+hole_geometry[2])*self.scale
          
                # Distance measured to top left corner of ellipse rect
                x_distance = hole_geometry[3]*self.scale/100 - x_diameter/2
                y_distance = hole_geometry[4]*self.scale/100 - y_diameter/2

                hole = QGraphicsEllipseItem(x_distance, y_distance, x_diameter, y_diameter)
                hole.setPen(self.solid_pen)
                self.top_scene.addItem(hole)

    def draw_holes_front(self, partmark):
        hole_geometry_list = self.hole_database.get_hole_geometry_list(partmark, "front")
        if hole_geometry_list:
            for hole_geometry in hole_geometry_list:
                x_diameter = (hole_geometry[0]+hole_geometry[1])*self.scale
                y_diameter = (hole_geometry[0]+hole_geometry[2])*self.scale

                # Distance measured to top left corner of ellipse rect
                x_distance = hole_geometry[3]*self.scale/100 - x_diameter/2
                y_distance = hole_geometry[4]*self.scale/100 - y_diameter/2

                hole = QGraphicsEllipseItem(x_distance, y_distance, x_diameter, y_diameter)
                hole.setPen(self.solid_pen)
                self.front_scene.addItem(hole)

    def draw_holes_bottom(self, partmark, flange_height):
        hole_geometry_list = self.hole_database.get_hole_geometry_list(partmark, "bottom")
        if hole_geometry_list:
            for hole_geometry in hole_geometry_list:
                x_diameter = (hole_geometry[0]+hole_geometry[1])*self.scale
                y_diameter = (hole_geometry[0]+hole_geometry[2])*self.scale
          
                # Distance measured to top left corner of ellipse rect
                x_distance = hole_geometry[3]*self.scale/100 - x_diameter/2
                y_distance = flange_height - hole_geometry[4]*self.scale/100 - y_diameter/2

                hole = QGraphicsEllipseItem(x_distance, y_distance, x_diameter, y_diameter)
                hole.setPen(self.solid_pen)
                self.bottom_scene.addItem(hole)
    
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
