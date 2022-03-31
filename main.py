title = "MNEMG by NVcoder, PLAYRU"
release = "v1"

import sys
import os
from PIL import Image
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QFormLayout,
    QFileDialog,
    QPushButton,
    QSlider,
    QCheckBox,
    QMessageBox,
    QSpinBox,
    QFrame,
    QLineEdit,
    QComboBox,
)

sides = (
    "top",
    "bottom",
    "left",
    "right",
    "front",
    "back",
)

colors = (
    "white",
    "orange",
    "magenta",
    "lightBlue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "lightGray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
)

ignore_color = (0, 0, 0)

func_template = "{fname}_panel.setColorRGB({color_xy})"

code_template = """
{fname}_panel = peripheral.wrap("{side}")
{fname}_panel.fill({ignore_color})
function {fname}_on()
    {fname}_panel.fill({ignore_color})
{stuff}
end
function {fname}_off()
    {fname}_panel.fill({ignore_color})
end
"""

def compile(img:Image, fname:str, side:str):
    img.convert('RGB')

    w, h = img.size

    pixels = []
    for x in range(w):
        for y in range(h):
            pos = (x, y)
            color = img.getpixel(pos)
            if color != ignore_color:
                pixels.append(color + pos)

    funcs = ""
    for color_xy in pixels:
        x = color_xy[3]
        y = color_xy[4]
        if len(color_xy) == 6:
            x = color_xy[4]
            y = color_xy[5]
        funcs += "    " + func_template.format(fname=fname, color_xy=f"{color_xy[0]}, {color_xy[1]}, {color_xy[2]}, {x}, {y}") + "\n"

    return code_template.format(fname=fname, side=side, ignore_color=f"{ignore_color[0]}, {ignore_color[1]}, {ignore_color[2]}", stuff=funcs)

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class FileDialog(QFileDialog):
    def __init__(self, title:str, type_name:str ,types:tuple) -> None:
        super().__init__()
        filter = f"{type_name} ({' '.join(['*.' + s for s in types])})"
        self.path = self.getOpenFileName(self, title, "C:/", filter)
    
    def __str__(self) -> str:
        return self.path[0]
    
    def get_tuple(self) -> tuple:
        return self.path

class Info(QMessageBox):
    def __init__(self, title:str, text:str, info:str):
        super().__init__()

        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)

        self.setText(text)
        self.setInformativeText(info)

        self.show()

        self.exec_()

class Error(QMessageBox):
    def __init__(self, title:str, text:str, info:str):
        super().__init__()

        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(title)

        self.setText(text)
        self.setInformativeText(info)

        self.show()

        self.exec_()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_path = None
        self.code_path = None

        self.setWindowTitle(f"{title} | {release}")

        # левая сторона
        self.img_prew = QGridLayout()
        self.img_prew_label = QLabel("Выберите файл картинки!")
        self.img_prew_label.setMinimumSize(300, 300)
        self.img_prew_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.img_prew.addWidget(self.img_prew_label)

        # правая сторона
        self.options = QFormLayout()

        # Выбрать файл картинки
        self.options_import_img_label = QLabel("*файл не выбран*")
        self.options_import_img_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.options_import_img_button = QPushButton("Выбрать файл")
        self.options_import_img_button.clicked.connect(self.open_image)

        self.options_import_img = QHBoxLayout()
        self.options_import_img.addWidget(self.options_import_img_button)
        self.options_import_img.addWidget(self.options_import_img_label)

        # Параметры кода
        self.options_fname_line_edit = QLineEdit()

        self.options_side_combo = QComboBox()
        self.options_side_combo.addItems(sides)

        self.options_colors_combo = QComboBox()
        self.options_colors_combo.addItems(colors)

        # Файл кода
        self.options_import_code_label = QLabel("*файл не выбран*")
        self.options_import_code_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.options_import_code_button = QPushButton("Выбрать файл")
        self.options_import_code_button.clicked.connect(self.open_code)

        self.options_import_code = QHBoxLayout()
        self.options_import_code.addWidget(self.options_import_code_button)
        self.options_import_code.addWidget(self.options_import_code_label)

        # Кнопка сохранить
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setFont(QFont("Arial", 20))
        self.save_btn.clicked.connect(self.save_code)

        # Добавляем элементы в QFormLayout
        self.options.addRow(QLabel("Импорт картинки:"))
        self.options.addRow(self.options_import_img)
        self.options.addRow(QLabel("Настройки кода:"))
        self.options.addRow("Название панели: ", self.options_fname_line_edit)
        self.options.addRow("Side: ", self.options_side_combo)
        self.options.addRow("Color: ", self.options_colors_combo)
        self.options.addRow(QLabel("Файл кода:"))
        self.options.addRow(self.options_import_code)
        self.options.addRow(self.save_btn)

        self.options_widget = QWidget()
        self.options_widget.setFixedWidth(250)
        self.options_widget.setLayout(self.options)

        # Виджэтс
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.img_prew)
        self.layout.addWidget(QVLine())
        self.layout.addWidget(self.options_widget)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def save_code(self):
        if self.image_path == None:
            Error("Ошиб-очка", "Выберите файл картинки", "")
            return
        
        if self.code_path == None:
            Error("Ошиб-очка", "Выберите файл кода", "")
            return

        if self.options_fname_line_edit.text() == "":
            Error("Недопустимое значение", "Впишите название панели", "")
            return

        try:
            code = compile(Image.open(self.image_path), self.options_fname_line_edit.text(), f"{self.options_side_combo.currentText()}:{self.options_colors_combo.currentText()}")
            with open(self.code_path, "w") as file:
                file.write(code)
                file.close()
            Info("Готово!", f"Файл сохранён в\n{os.path.basename(self.code_path)}", "")
        except Exception as e:
            Error("Ошиб-очка", "Не удалось сохранить код", "")
    
    def open_image(self):
        path = FileDialog("Открыть файл картинки", "Image", ("jpg", "png"))
        if str(path) != "":
            self.image_path = str(path)
            self.options_import_img_label.setText(os.path.basename(str(path)))
            self.set_preview_img()
    
    def open_code(self):
        path = FileDialog("Открыть файл кода", "Lua shit", ("lua", "txt"))
        if str(path) != "":
            self.code_path = str(path)
            self.options_import_code_label.setText(os.path.basename(str(path)))
        
    def set_preview_img(self):
        try:
            pixmap = QPixmap(self.image_path)
            self.img_prew_label.setPixmap(pixmap)
        except Exception as e:
            Error("Ошиб-очка", "Не удалось вывести картинку!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
