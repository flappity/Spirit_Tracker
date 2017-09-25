from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QFrame, QWidget, QMenu, QFileDialog, QHBoxLayout
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QPushButton
from PyQt5.QtGui import QIcon, QWindow, QPixmap, QDrag, QPainter, QColor, QPalette, QCursor
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QPoint, Qt, QMimeData, QAbstractItemModel
import functools, json
import sys

# The main window holding everything else.
class Tracker(QMainWindow):
    def __init__(self):
        super().__init__()

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_layout = QAction('Open Layout', self)
        open_layout.triggered.connect(self.choose_layout)
        file_menu.addAction(open_layout)

        open_editor = QAction('Layout Editor', self, )
        open_editor.setShortcut('F3')
        open_editor.triggered.connect(self.open_editor)
        file_menu.addAction(open_editor)

        self.zone = TrackerZone(self)
        self.zone.show()

        self.setGeometry(400, 500, 400, 300)
        self.setWindowTitle('Spirit Tracker')
        # self.setStyleSheet("Tracker_Zone { background-color:black}")
        self.show()

    def choose_layout(self):
        filename, _ = QFileDialog.getOpenFileName(QFileDialog(), 'Choose Layout', ":/", "Layout Files(*.layout)")
        if filename:
            self.zone.open_layout(filename)

    def open_editor(self):
        editor = LayoutEditor(self)
        editor.show()



# The actual "zone" where the tracker icons sit
# Essentially an area inside Tracker covering the window except the menubar/statusbar
class TrackerZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.elements = []
        self.setGeometry(0, 20, 800, 600)

        # Test element

        # hammer = Tracker_Item(self, image_list=[['hammer', 'icons/hammer.png'], ['mirror', 'icons/mirror.png'],
        #                                         ['chest', 'icons/chest0.png']], name='hammirror', x=50, y=50)
        # self.elements.append(hammer.data)
        # self.elements.append(hammer.data)

    def open_layout(self, filename):
        for element in self.elements:
            element.hide()
            element.destroy()
        self.elements = []
        with open(filename) as json_data:
            d = json.load(json_data)
            for entry in d:
                element = TrackerItem(self, image_list=entry['images'], name=entry['name'], x=entry['coords'][0],
                                      y=entry['coords'][1], layer=entry['layer'])
                self.elements.append(element)
                element.show()


# Any layout element is one of these
class TrackerItem(QLabel):
    def __init__(self, parent=None, image_list=None, name='default', x=0, y=0, layer=1):
        super().__init__(parent)

        self.coords = [x, y]
        self.move(x, y)
        self.name = name
        self.images = image_list
        self.num_images = len(self.images)
        self.im_idx = 0

        self.current_icon = QPixmap(self.images[0][1])
        self.setPixmap(self.current_icon)
        self.setMinimumWidth(self.current_icon.width())
        self.setMinimumHeight(self.current_icon.height())
        self.data = {'name': self.name, "coords": self.coords, 'images': self.images, "layer": layer}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == Qt.LeftButton:
            self.cycle_image()

    def cycle_image(self):
        if self.im_idx + 1 == self.num_images:
            self.im_idx = 0
        else:
            self.im_idx += 1
        self.current_icon = QPixmap(self.images[self.im_idx][1])
        self.setMinimumWidth(self.current_icon.width())
        self.setMinimumHeight(self.current_icon.height())
        self.setPixmap(self.current_icon)

    def context_menu(self, pos):
        menu = QMenu(self)
        for x in self.images:
            entry = QAction(x[0], self)
            entry.triggered.connect(functools.partial(self.set_image, x[0]))
            menu.addAction(entry)
        menu.exec_(self.mapToGlobal(pos))

    def set_image(self, image):
        print('yes')
        for x in self.images:
            if x[0] == image:
                self.current_icon = QPixmap(x[1])
                self.setMinimumWidth(self.current_icon.width())
                self.setMinimumHeight(self.current_icon.height())
                self.setPixmap(self.current_icon)
                self.im_idx = self.images.index([x[0], x[1]])


class LayoutEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_layout = QAction('Open Layout', self)
        open_layout.setShortcut('F4')
        open_layout.triggered.connect(self.choose_layout)
        file_menu.addAction(open_layout)

        self.zone = EditZone(self)
        self.zone.show()

        self.setGeometry(600, 600, 400, 300)
        self.setWindowTitle('Spirit Editor')
        self.show()

    def choose_layout(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Choose Layout', ":/", "Layout Files(*.layout)")
        if filename:
            self.zone.open_layout(filename)


class EditZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.elements = []
        self.setGeometry(0, 20, 800, 600)

    def open_layout(self, filename):
        for element in self.elements:
            element.hide()
            element.destroy()
        self.elements = []
        with open(filename) as json_data:
            d = json.load(json_data)
            for entry in d:
                element = EditorItem(self, image_list=entry['images'], name=entry['name'], x=entry['coords'][0],
                                     y=entry['coords'][1], layer=entry['layer'])
                self.elements.append(element)
                element.show()


class EditorItem(QLabel):
    def __init__(self, parent=None, image_list=None, name='default', x=0, y=0, layer=1):
        super().__init__(parent)

        self.coords = [x, y]
        self.move(x, y)
        self.name = name
        self.images = image_list
        self.num_images = len(self.images)
        self.im_idx = 0
        self.layer = layer
        self.x = x
        self.y = y

        self.current_icon = QPixmap(self.images[0][1])
        self.setPixmap(self.current_icon)
        self.setMinimumWidth(self.current_icon.width())
        self.setMinimumHeight(self.current_icon.height())
        self.data = {'name': self.name, "coords": self.coords, 'images': self.images, "layer": layer}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def context_menu(self, pos):
        menu = QMenu(self)
        cycle = QAction('Cycle Image')
        cycle.triggered.connect(self.cycle_image)
        element_list = QMenu('Choose Image', self)
        for x in self.images:
            entry = QAction(x[0], self)
            # entry.triggered.connect(functools.partial(self.set_image, x[0]))
            element_list.addAction(entry)
        show_props = QAction('Properties')
        show_props.triggered.connect(self.show_options)
        menu.addAction(cycle)
        menu.addMenu(element_list)
        menu.addAction(show_props)
        menu.exec_(self.mapToGlobal(pos))

    def show_options(self):
        prop_window = ElementProps(self)

    def set_options(self, options):
        a = 1

    def cycle_image(self):
        if self.im_idx + 1 == self.num_images:
            self.im_idx = 0
        else:
            self.im_idx += 1
        self.current_icon = QPixmap(self.images[self.im_idx][1])
        self.setMinimumWidth(self.current_icon.width())
        self.setMinimumHeight(self.current_icon.height())
        self.setPixmap(self.current_icon)


class ElementProps(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setContextMenuPolicy(Qt.NoContextMenu)
        main_layout = QVBoxLayout()
        upper_layout = QVBoxLayout()

        name_txt = QLabel('Element name')
        name_edit = QLineEdit()
        name_edit.setText(parent.name)

        name_entry = QHBoxLayout()
        name_entry.addWidget(name_txt)
        name_entry.addWidget(name_edit)

        x_txt = QLabel('X')
        x_edit = QLineEdit()
        x_edit.setText(str(parent.x))

        y_txt = QLabel('Y')
        y_edit = QLineEdit()
        y_edit.setText(str(parent.y))

        layer_txt = QLabel('Layer')
        layer_edit = QLineEdit()
        layer_edit.setText(str(parent.layer))

        xy_layer_row = QHBoxLayout()
        xy_layer_row.addWidget(x_txt)
        xy_layer_row.addWidget(x_edit)
        xy_layer_row.addWidget(y_txt)
        xy_layer_row.addWidget(y_edit)
        xy_layer_row.addWidget(layer_txt)
        xy_layer_row.addWidget(layer_edit)

        upper_layout.addLayout(name_entry)
        upper_layout.addLayout(xy_layer_row)

        image_table = QTableWidget()
        image_table.setColumnCount(2)
        image_table.setRowCount(len(parent.images))
        image_table.verticalHeader().hide()
        image_table.setHorizontalHeaderLabels(["Name", "Image File"])
        image_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        image_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        print(parent.images)
        print(parent.images[0][0])
        print(parent.images[0][1])
        for image in parent.images:
            idx = parent.images.index(image)
            image_table.setItem(0 + idx, 0, QTableWidgetItem(parent.images[idx][0]))
            image_table.setItem(0 + idx, 1, QTableWidgetItem(parent.images[idx][1]))
        edit_image = QPushButton('Edit', self)
        main_layout.addLayout(upper_layout)
        main_layout.addWidget(image_table)
        main_layout.setAlignment(Qt.AlignTop)

        self.setLayout(main_layout)
        self.setGeometry(300, 300, 250, 250)
        self.setWindowTitle('Options')
        self.show()

    def changeitem(self):
        # print([item.tableWidget().selectedItems()[0].text(), item.tableWidget().selectedItems()[1].text()])
        print('!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Tracker()
    sys.exit(app.exec_())
