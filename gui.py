import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QListView, QAbstractItemView
from PyQt6.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")

        layout = QGridLayout()

        widget1 = Color('red')
        widget1.setFixedWidth(250)
        widget2 = Color('blue')
        widget2.setFixedWidth(250)
        widget4 = Color('pink')
        widget4.setMinimumSize(1100, 300)
        widget5 = Color('black')
        widget5.setMinimumSize(1100, 300)
        widget6 = Color('green')
        widget6.setMinimumSize(1100, 300)


        self.listView = QListView()
        self.model = QStandardItemModel()
        self.listView.setModel(self.model)
        self.listView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for i in range(200):
            i = str(i)
            item = QStandardItem(i)
            self.model.appendRow(item)
        
        self.listView.clicked[QModelIndex].connect(self.test)


        layout.addWidget(self.listView, 0, 0, 0, 1)
        layout.addWidget(widget2, 0, 1, 0, 1)
        layout.addWidget(widget4, 0, 2)
        layout.addWidget(widget5, 1, 2)
        layout.addWidget(widget6, 2, 2)


        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def test(self, index):

        item = self.model.itemFromIndex(index)
        print(item.text())


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class TodoModel(QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(TodoModel, self).__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            status, text = self.todos[index.row()]
            return text

    def rowCount(self, index):
        return len(self.todos)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()