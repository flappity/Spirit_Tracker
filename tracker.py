from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QFrame, QWidget, QMenu, QFileDialog, QHBoxLayout
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QPushButton
from PyQt5.QtWidgets import QDialogButtonBox, QGroupBox, QSizePolicy, QGridLayout, QFormLayout
from PyQt5.QtGui import QIcon, QWindow, QPixmap, QDrag, QPainter, QColor, QPalette, QCursor
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QPoint, Qt, QMimeData, QDir
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
        # The overarching layout for this window
        main_layout = QVBoxLayout()

        # The upper half
        upper_layout = QVBoxLayout()

        # Row containing Element Name: and the QLineEdit for it
        name_txt = QLabel('Element name')
        name_edit = QLineEdit()
        name_edit.setText(parent.name)

        # Building the above row
        name_entry = QHBoxLayout()
        name_entry.addWidget(name_txt)
        name_entry.addWidget(name_edit)

        # Elements for the row containing X, Y, Layer and QLineEdits
        x_txt = QLabel('X')
        x_edit = QLineEdit()
        x_edit.setText(str(parent.x))

        y_txt = QLabel('Y')
        y_edit = QLineEdit()
        y_edit.setText(str(parent.y))

        layer_txt = QLabel('Layer')
        layer_edit = QLineEdit()
        layer_edit.setText(str(parent.layer))

        # Laying out x, y, and layer text/boxes
        xy_layer_row = QHBoxLayout()
        xy_layer_row.addWidget(x_txt)
        xy_layer_row.addWidget(x_edit)
        xy_layer_row.addWidget(y_txt)
        xy_layer_row.addWidget(y_edit)
        xy_layer_row.addWidget(layer_txt)
        xy_layer_row.addWidget(layer_edit)

        # Putting together the rows above
        upper_layout.addLayout(name_entry)
        upper_layout.addLayout(xy_layer_row)

        # Creating the Add/Edit/Delete buttons...
        add_image = QPushButton('Add', self)
        edit_image = QPushButton('Edit Selected', self)
        delete_image = QPushButton('Delete Selected', self)

        # ..and laying them out together
        add_edit_cancel = QHBoxLayout()
        add_edit_cancel.addWidget(add_image)
        add_edit_cancel.addWidget(edit_image)
        add_edit_cancel.addWidget(delete_image)

        # The layout for the bottom half of the window, including push buttons and table
        lower_layout = QVBoxLayout()

        # The table in the lower half of the image
        image_table = QTableWidget()
        image_table.setColumnCount(2)
        image_table.setRowCount(len(parent.images))
        image_table.verticalHeader().hide()
        image_table.setHorizontalHeaderLabels(["Name", "Image File"])
        image_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        image_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        image_table.setFrameShape(QFrame.WinPanel)
        image_table.setFrameShadow(QFrame.Plain)
        image_table.setAlternatingRowColors(True)
        image_table.setShowGrid(False)
        image_table.horizontalHeader().setStretchLastSection(True)

        for image in parent.images:
            idx = parent.images.index(image)
            image_table.setItem(0 + idx, 0, QTableWidgetItem(parent.images[idx][0]))
            image_table.setItem(0 + idx, 1, QTableWidgetItem(parent.images[idx][1]))

        # Putting together the list view + its buttons
        lower_layout.addLayout(add_edit_cancel)
        lower_layout.addWidget(image_table)

        # Building OK/Cancel/Apply buttons
        ok_btn = QPushButton('OK', self)
        cancel_btn = QPushButton('Cancel', self)
        apply_btn = QPushButton('Apply', self)

        # Putting together buttons
        dialog_buttons_layout = QHBoxLayout()
        dialog_buttons_layout.addWidget(ok_btn)
        dialog_buttons_layout.addWidget(cancel_btn)
        dialog_buttons_layout.addWidget(apply_btn)

        # Building separator lines
        hline = QFrame(self)
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)

        hline2 = QFrame(self)
        hline2.setFrameShape(QFrame.HLine)
        hline2.setFrameShadow(QFrame.Sunken)

        main_layout.addLayout(upper_layout)
        main_layout.addWidget(hline)
        main_layout.addLayout(lower_layout)
        main_layout.addWidget(hline2)
        main_layout.addLayout(dialog_buttons_layout)

        # Defining button functions down here because FML
        edit_image.clicked.connect(functools.partial(self.edit_sel_image, image_table.selectedItems))

        self.setLayout(main_layout)
        self.setGeometry(300, 300, 250, 250)
        self.setWindowTitle('Options')
        self.show()

    def edit_sel_image(self, selected_items=None):
        if selected_items:
            print(selected_items()[0].text())
            print(selected_items()[1].text())
        change_selection = ImageWindow(self, selected_items)


class ImageWindow(QDialog):
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        self.setGeometry(400, 400, 500, 100)

        # Store relevant variables to pull up later
        if items:
            self.img_name = items()[0].text()
            self.img_file = items()[1].text()
            self.items = items

        # Create name/filename text and QLineEdit fields
        self.name_txt = QLabel('Name')
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.img_name)

        self.file_txt = QLabel('File')
        self.file_edit = QLineEdit()
        self.file_edit.setText(self.img_file)

        # Arrange name/filename rows in a form layout
        form = QFormLayout()
        form.addRow(self.name_txt, self.name_edit)
        form.addRow(self.file_txt, self.file_edit)

        choose_file = QPushButton('Choose File')
        choose_file.setMaximumWidth(100)
        choose_file.clicked.connect(self.choose_new_image)

        image_preview_label = QLabel()
        image_preview_label.setText('Image Preview:')
        image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setPixmap(QPixmap(self.img_file))

        image_preview_layout = QVBoxLayout()
        image_preview_layout.addWidget(image_preview_label)
        image_preview_layout.addWidget(self.image_preview)
        image_preview_box = QGroupBox()
        image_preview_box.setLayout(image_preview_layout)

        ok_btn = QPushButton('Fine')
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.set_info)
        cancel_btn = QPushButton('Dammit')
        ok_cancel_row = QHBoxLayout()
        ok_cancel_row.addWidget(ok_btn)
        ok_cancel_row.addWidget(cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addWidget(choose_file, alignment=Qt.AlignCenter)
        main_layout.addWidget(image_preview_box)
        main_layout.addLayout(ok_cancel_row)

        self.setLayout(main_layout)
        self.show()

    # Opens a file dialogue, lets user choose an image. Puts relative path in filename box, updates image preview.
    def choose_new_image(self):
        dir = QDir()
        filename, _ = QFileDialog.getOpenFileName(self, 'Choose Layout', ":/", "Image Files (*.png)")
        if filename:
            self.file_edit.setText(dir.relativeFilePath(filename))
            self.image_preview.setPixmap(QPixmap(filename))

    # Once user is happy with image and image name, this applies the changes to the table in parent ElementProps window.
    def set_info(self):
        self.items()[0].setText(self.name_edit.text())
        self.items()[1].setText(self.file_edit.text())
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Tracker()
    sys.exit(app.exec_())
