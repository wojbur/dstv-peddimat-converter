import sys
import os
import subprocess

from PyQt6.QtWidgets import (
    QStyle, QApplication, QMainWindow, QToolBar, QStatusBar, QSlider, QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog, QWidget,
    QCheckBox, QComboBox, QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QLabel, QSizePolicy
)
from PyQt6.QtGui import QAction, QIcon, QPen, QPixmap
from PyQt6.QtCore import Qt, QModelIndex

from db_controller import DatabaseConnection, PartDatabase, HoleDatabase
from dstv_decoder import SteelPart
from peddimat_encoder import PeddimatEncoder

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSTV-Peddimat Converter")

        self.basedir = os.path.dirname(__file__)
        self.database_connection = DatabaseConnection(os.path.join(self.basedir, "current_session.db"))

        self.setWindowIcon(QIcon(os.path.join(self.basedir, "Icons", "converter.png")))

        toolbar = QToolBar("Import NC1")
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.addToolBar(toolbar)

        # import_icon = QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        import_icon = QIcon(os.path.join(self.basedir, "Icons", "dstv_import.png"))
        import_dstv_action = QAction(import_icon, "&import dstv files", self)
        import_dstv_action.triggered.connect(self.import_dstv)
        toolbar.addAction(import_dstv_action)

        export_icon = QIcon(os.path.join(self.basedir, "Icons", "peddimat_export.png"))
        export_peddimat_action = QAction(export_icon, "&export peddimat files", self)
        export_peddimat_action.triggered.connect(self.export_peddimat)
        toolbar.addAction(export_peddimat_action)

        remove_list_item_icon = QIcon(os.path.join(self.basedir, "Icons", "bin.png"))
        remove_list_item_action = QAction(remove_list_item_icon, "&remove selected", self)
        remove_list_item_action.triggered.connect(self.remove_list_item)
        toolbar.addAction(remove_list_item_action)

        toolbar.addSeparator()

        self.valid_profile_types = ["B", "C", "T", "t"]

        self.B_checkbox = QCheckBox(self)
        self.B_checkbox.setIcon(QIcon(os.path.join(self.basedir, "Icons", "profile_wf.png")))
        self.B_checkbox.setChecked(True)
        self.B_checkbox.stateChanged.connect(lambda checked: self.profile_checkbox_changed(checked, "B"))
        toolbar.addWidget(self.B_checkbox)
        self.C_checkbox = QCheckBox(self)
        self.C_checkbox.setIcon(QIcon(os.path.join(self.basedir, "Icons", "profile_c.png")))
        self.C_checkbox.setChecked(True)
        self.C_checkbox.stateChanged.connect(lambda checked: self.profile_checkbox_changed(checked, "C"))
        toolbar.addWidget(self.C_checkbox)
        self.T_checkbox = QCheckBox(self)
        self.T_checkbox.setIcon(QIcon(os.path.join(self.basedir, "Icons", "profile_tube.png")))
        self.T_checkbox.setChecked(True)
        self.T_checkbox.stateChanged.connect(lambda checked: self.profile_checkbox_changed(checked, "T"))
        toolbar.addWidget(self.T_checkbox)
        self.tee_checkbox = QCheckBox(self)
        self.tee_checkbox.setIcon(QIcon(os.path.join(self.basedir, "Icons", "profile_t.png")))
        self.tee_checkbox.setChecked(True)
        self.tee_checkbox.stateChanged.connect(lambda checked: self.profile_checkbox_changed(checked, "t"))
        toolbar.addWidget(self.tee_checkbox)

        toolbar.addSeparator()

        # self.ignore_parts_without_holes = False
        # self.ignore_parts_without_holes_checkbox = QCheckBox("ignore parts without holes", self)
        # self.ignore_parts_without_holes_checkbox.setChecked(False)
        # toolbar.addWidget(self.ignore_parts_without_holes_checkbox)



        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.scale = 0.05

        scale_slider = QSlider(Qt.Orientation.Horizontal)
        scale_slider.setValue(50)
        scale_slider.setMinimum(20)
        scale_slider.setMaximum(80)
        scale_slider.setFixedWidth(100)
        scale_slider.valueChanged.connect(self.scale_slider_changed)

        zoom_out_icon = QIcon(os.path.join(self.basedir, "Icons", "zoom_out.png"))
        zoom_out_action = QAction(zoom_out_icon, "&zoom out", self)
        zoom_out_action.triggered.connect(lambda: scale_slider.setValue(scale_slider.value()-1))

        zoom_in_icon = QIcon(os.path.join(self.basedir, "Icons", "zoom_in.png"))
        zoom_in_action = QAction(zoom_in_icon, "&zoom in", self)
        zoom_in_action.triggered.connect(lambda: scale_slider.setValue(scale_slider.value()+1))

        zoom_out_icon = QIcon(os.path.join(self.basedir, "Icons", "zoom_out.png"))

        toolbar.addAction(zoom_out_action)
        toolbar.addWidget(scale_slider)
        toolbar.addAction(zoom_in_action)

        self.part_list_widget = QListWidget()
        self.part_list_widget.setFixedWidth(150)
        self.part_list_widget.setAlternatingRowColors(True)
        self.part_list_widget.currentItemChanged.connect(self.part_list_index_changed)

        table_unit_label = QLabel("Table units:")
        table_unit_label.setFixedWidth(75)
        self.table_unit_combobox = QComboBox()
        self.table_unit_combobox.setFixedWidth(75)
        self.table_unit_combobox.addItems(["mm", "inch"])
        self.table_unit_combobox.currentIndexChanged.connect(self.table_unit_combobox_index_changed)
        self.create_part_info_table()
        self.create_hole_info_table()

        self.solid_pen = QPen(Qt.GlobalColor.white)
        self.solid_pen.setStyle(Qt.PenStyle.SolidLine)
        self.solid_pen.setWidth(1)

        self.dashed_pen = QPen(Qt.GlobalColor.white)
        self.dashed_pen.setStyle(Qt.PenStyle.DashLine)
        self.dashed_pen.setWidth(1)

        self.create_part_views()

        unit_layout = QHBoxLayout()
        unit_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        unit_layout.addWidget(table_unit_label)
        unit_layout.addWidget(self.table_unit_combobox)

        table_layout = QVBoxLayout()
        table_layout.addLayout(unit_layout)
        table_layout.addWidget(self.part_info_table)
        table_layout.addWidget(self.hole_info_table)

        layout = QGridLayout()
        layout.addWidget(self.part_list_widget, 0, 0, 0, 1)
        layout.addLayout(table_layout, 0, 1, 0, 1)
        layout.addWidget(self.top_view, 0, 2)
        layout.addWidget(self.front_view, 1, 2)
        layout.addWidget(self.bottom_view, 2, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # self.showMaximized()
        self.show()
    
    def profile_checkbox_changed(self, checked, profile_type):
        if checked:
            self.valid_profile_types.append(profile_type)
        else:
            self.valid_profile_types.remove(profile_type)
        print(self.valid_profile_types)
    
    def scale_slider_changed(self, value):
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
            self.populate_part_info_table(partmark)
            self.populate_hole_info_table(partmark)
            self.draw_part(partmark)
    
    def remove_list_item(self):
        current_item = self.part_list_widget.currentItem()
        if current_item:
            partmark = current_item.text()
            self.hole_database.remove_data(partmark)
            self.part_database.remove_data(partmark)
            self.part_list_widget.takeItem(self.part_list_widget.row(current_item))

        current_item = self.part_list_widget.currentItem()
        if not current_item:
            self.clear_scenes()
            self.hole_info_table.setRowCount(0)
            self.part_info_table.setRowCount(0)
    
    def table_unit_combobox_index_changed(self):
        current_item = self.part_list_widget.currentItem()
        if current_item:
            partmark = current_item.text()
            self.populate_part_info_table(partmark)
            self.populate_hole_info_table(partmark)
    
    def create_part_info_table(self):
        self.part_info_table = QTableWidget(0, 4)
        self.part_info_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.part_info_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.part_info_table.setFixedWidth(350)
        self.part_info_table.setFixedHeight(50)
        labels = ["Profile", "Length", "Height", "Width"]
        self.part_info_table.setHorizontalHeaderLabels(labels)
        for i, label in enumerate(labels):
            self.part_info_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.part_info_table.verticalHeader().setVisible(False)
    
    def populate_part_info_table(self, partmark):
        self.part_info_table.setRowCount(0)

        part_geometry = self.part_database.get_part_geometry(partmark)
        if part_geometry:
            if self.table_unit_combobox.currentText() == "mm":
                self.part_info_table.insertRow(0)
                self.part_info_table.setItem(0, 0, QTableWidgetItem(part_geometry["profile"]))
                self.part_info_table.setItem(0, 1, QTableWidgetItem(str(round(part_geometry["length"]/10, 1))))
                self.part_info_table.setItem(0, 2, QTableWidgetItem(str(round(part_geometry["profile_depth"]/10, 1))))
                self.part_info_table.setItem(0, 3, QTableWidgetItem(str(round(part_geometry["flange_height"]/10, 1))))
            elif self.table_unit_combobox.currentText() == "inch":
                self.part_info_table.insertRow(0)
                self.part_info_table.setItem(0, 0, QTableWidgetItem(part_geometry["profile"]))
                self.part_info_table.setItem(0, 1, QTableWidgetItem(str(round(part_geometry["length"]/254, 3))))
                self.part_info_table.setItem(0, 2, QTableWidgetItem(str(round(part_geometry["profile_depth"]/254, 3))))
                self.part_info_table.setItem(0, 3, QTableWidgetItem(str(round(part_geometry["flange_height"]/254, 3))))

    def create_hole_info_table(self):
        self.hole_info_table = QTableWidget(0, 4)
        self.hole_info_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.hole_info_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.hole_info_table.setFixedWidth(350)
        labels = ["Surface", "Size", "X distance", "Y distance"]
        self.hole_info_table.setHorizontalHeaderLabels(labels)
        for i, label in enumerate(labels):
            self.hole_info_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.hole_info_table.verticalHeader().setVisible(False)

    def populate_hole_info_table(self, partmark):
        self.hole_info_table.setRowCount(0)

        hole_info_list = self.hole_database.get_hole_info_list(partmark)
        if hole_info_list:
            for hole in hole_info_list:
                if self.table_unit_combobox.currentText() == "mm":
                    row_position = self.hole_info_table.rowCount()
                    self.hole_info_table.insertRow(self.hole_info_table.rowCount())
                    self.hole_info_table.setItem(row_position, 0, QTableWidgetItem(hole["surface"]))
                    self.hole_info_table.setItem(row_position, 1, QTableWidgetItem(hole["size_mm"]))
                    self.hole_info_table.setItem(row_position, 2, QTableWidgetItem(str(round(hole["x_distance"]/1000, 1))))
                    self.hole_info_table.setItem(row_position, 3, QTableWidgetItem(str(round(hole["y_distance"]/1000, 1))))
                elif self.table_unit_combobox.currentText() == "inch":
                    row_position = self.hole_info_table.rowCount()
                    self.hole_info_table.insertRow(self.hole_info_table.rowCount())
                    self.hole_info_table.setItem(row_position, 0, QTableWidgetItem(hole["surface"]))
                    self.hole_info_table.setItem(row_position, 1, QTableWidgetItem(hole["size_inch"]))
                    self.hole_info_table.setItem(row_position, 2, QTableWidgetItem(str(round(hole["x_distance"]/25400, 3))))
                    self.hole_info_table.setItem(row_position, 3, QTableWidgetItem(str(round(hole["y_distance"]/25400, 3))))
    
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
        top_y_offset = self.top_scene.height()/2 - part_geometry["flange_height"]/2 * self.scale
        front_y_offset = self.front_scene.height()/2 - part_geometry["profile_depth"]/2 * self.scale
        bottom_y_offset = self.bottom_scene.height()/2 - part_geometry["flange_height"]/2 * self.scale

        for item in self.top_scene.items():
            item.moveBy(50, top_y_offset)
        for item in self.front_scene.items():
            item.moveBy(50, front_y_offset)
        for item in self.bottom_scene.items():
            item.moveBy(50, bottom_y_offset)
    
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
        
        elif part_geometry["profile_type"] == "C":
            web_y = web_thickness
            web = QGraphicsLineItem(0, web_y, length, web_y)
            web.setPen(self.dashed_pen)
            self.top_scene.addItem(web)
        
        elif part_geometry["profile_type"] == "T":
            top_web_y = web_thickness
            bottom_web_y = height - web_thickness
            top_web = QGraphicsLineItem(0, top_web_y, length, top_web_y)
            bottom_web = QGraphicsLineItem(0, bottom_web_y, length, bottom_web_y)
            top_web.setPen(self.dashed_pen)
            bottom_web.setPen(self.dashed_pen)
            self.top_scene.addItem(top_web)
            self.top_scene.addItem(bottom_web)
        
        elif part_geometry["profile_type"] == "t":
            top_web_y = height/2 - web_thickness/2
            bottom_web_y = height/2 + web_thickness/2
            top_web = QGraphicsLineItem(0, top_web_y, length, top_web_y)
            bottom_web = QGraphicsLineItem(0, bottom_web_y, length, bottom_web_y)
            top_web.setPen(self.solid_pen)
            bottom_web.setPen(self.solid_pen)
            self.top_scene.addItem(top_web)
            self.top_scene.addItem(bottom_web)

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
            top_flange_y = flange_thickness
            bottom_flange_y = depth - flange_thickness
            top_web = QGraphicsLineItem(0, top_flange_y, length, top_flange_y)
            bottom_web = QGraphicsLineItem(0, bottom_flange_y, length, bottom_flange_y)
            top_web.setPen(self.dashed_pen)
            bottom_web.setPen(self.dashed_pen)
            self.front_scene.addItem(top_web)
            self.front_scene.addItem(bottom_web)
        
        elif part_geometry["profile_type"] == "t":
            bottom_flange.setPen(self.solid_pen)
            self.front_scene.addItem(bottom_flange)

            
        
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
        
        elif part_geometry["profile_type"] == "C":
            web_y = height - web_thickness
            web = QGraphicsLineItem(0, web_y, length, web_y)
            web.setPen(self.dashed_pen)
            self.bottom_scene.addItem(web)
        
        elif part_geometry["profile_type"] == "T":
            top_web_y = web_thickness
            bottom_web_y = height - web_thickness
            top_web = QGraphicsLineItem(0, top_web_y, length, top_web_y)
            bottom_web = QGraphicsLineItem(0, bottom_web_y, length, bottom_web_y)
            top_web.setPen(self.dashed_pen)
            bottom_web.setPen(self.dashed_pen)
            self.bottom_scene.addItem(top_web)
            self.bottom_scene.addItem(bottom_web)
        
        elif part_geometry["profile_type"] == "t":
            self.bottom_scene.clear()

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
            if steel_part.profile_type in self.valid_profile_types:
                self.part_database.insert_data(steel_part)
                for hole in steel_part.holes:
                    self.hole_database.insert_data(hole)

    def import_dstv(self):
        dialog = QFileDialog(self)
        openfile_dir = self.get_openfile_directory()
        dialog.setDirectory(openfile_dir)
        filepaths = dialog.getOpenFileNames(self, caption="select .nc1 files", filter="DSTV files (*.nc1)")[0]
        if filepaths:
            self.save_to_database(filepaths)
            self.save_openfile_directory(filepaths[0])
            self.populate_part_list_widget()
            if self.part_list_widget.count():
                self.part_list_widget.setCurrentItem(self.part_list_widget.item(0))
        
    def get_openfile_directory(self):
        if os.path.exists(os.path.join(self.basedir, "lastdir.txt")):
            with open(os.path.join(self.basedir, "lastdir.txt"), "r") as f:
                last_dir = f.read()
                if os.path.exists(last_dir):
                    return last_dir
        return os.path.expanduser("~")
    
    def save_openfile_directory(self, filepath):
        openfile_fir = os.path.dirname(filepath)
        with open(os.path.join(self.basedir, "lastdir.txt"), "w") as f:
            f.write(openfile_fir)

    def export_peddimat(self):
        partmarks = [self.part_list_widget.item(i).text() for i in range(self.part_list_widget.count())]

        if partmarks:
            output_directory = QFileDialog.getExistingDirectory(self, caption="select output directory")
            if output_directory:
                peddimat_encoder = PeddimatEncoder(self.database_connection)
                for partmark in partmarks:
                    peddimat_encoder.save_peddimat_file(partmark, output_directory)    
                os.startfile(output_directory)
    
    def closeEvent(self, event):
        if os.path.exists(self.database_connection.database_file):
            os.remove(self.database_connection.database_file)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()


if __name__ == "__main__":
    main()
