# 窗口1---主窗口代码，这个代码比较长

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


# 主窗口1
class main_w1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_UI()
        self.button_UI()

    def main_UI(self):
        # 设置窗口大小
        self.setFixedSize(400, 400)
        # 设置窗口名称
        self.setWindowTitle("窗口1")
        # 设置窗口的图片
        # self.setWindowIcon(QIcon("xxx.png"))
        # 设置一个主窗口
        self.main_wight = QWidget()
        # 设置一个主窗口布局--我比较喜欢网格布局
        self.main_layout = QGridLayout()
        # 将窗口加入布局
        self.main_wight.setLayout(self.main_layout)
        # 将这个主窗口设置成窗口主部件
        self.setCentralWidget(self.main_wight)

    def button_UI(self):
        # 在这里设置窗口的内容
        self.button_widght1 = QWidget()
        self.button_widght2 = QWidget()
        # 设置一个水平布局
        self.button_layout1 = QHBoxLayout()
        self.button_layout2 = QHBoxLayout()
        # 将窗口加入布局
        self.button_widght1.setLayout(self.button_layout1)
        self.button_widght2.setLayout(self.button_layout2)
        # 设置几个按钮用做调用其他窗口
        self.button1 = QPushButton("调用窗口1")
        self.button2 = QPushButton("调用窗口2")

        # 将按钮加入布局
        self.button_layout1.addWidget(self.button1)
        self.button_layout1.addWidget(self.button2)

        # 将两个按钮窗口加入主窗口
        self.main_layout.addWidget(self.button_widght1)
        self.main_layout.addWidget(self.button_widght2)

        # 按钮链接函数--不链接的按钮没有用处，如下2个按钮是动不了的
        self.button1.clicked.connect(self.Tow1)
        self.button1.clicked.connect(self.close)  # 这个是顺便关闭原来的窗口，
        # self.button2.clicked.connect(self.Tow2)
        self.button2.clicked.connect(self.close)  # 不加则原来的窗口不会关闭

    def Tow1(self):
        # 做好其他窗口后先import进来后就简单调用就ok了
        self.w1 = main_w1()
        self.w1.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = main_w1()
    gui.show()
    sys.exit(app.exec_())