import os
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from game_play_labels import main_labels


class LayEndScoreWindow:
    def __init__(self, parent, data, hnd_to_count):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.data = data
        self.main_widget = QWidget(parent)
        self.main_widget.setStyleSheet("background: #192642")
        self.main_widget.setGeometry(80, 205, 880, 370)
        btn_widget = QWidget(self.main_widget)
        btn_widget.setGeometry(260, 300, 200, 50)
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.next_btn = QPushButton("Next Scores")
        btn_layout.addWidget(self.next_btn)
        self.next_btn.clicked.connect(self.next_data)
        self.img_widget = QWidget(self.main_widget)
        self.img_widget.setGeometry(40, 85, 600, 200)
        self.txt_widget = QWidget(self.main_widget)
        self.txt_widget.setGeometry(680, 85, 150, 200)
        self.img_layout = QGridLayout(self.img_widget)
        self.img_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_layout = QGridLayout(self.txt_widget)
        self.txt_layout.setContentsMargins(0, 0, 0, 0)
        self.hnd_cnt = hnd_to_count
        self.step_indx = 0
        self.score_flag = -1
        self.flash_flag = 0
        self.set_data()

    def set_data(self):
        style = "color: {}; font-size: 18px;".format(self.data[1][self.step_indx])
        for x in range(5):
            path = os.path.join(self.base_dir, 'static/deck/{}.png'.format(self.data[2][self.step_indx][x]))
            pixmap = QPixmap(path)
            label = QLabel()
            label.setPixmap(pixmap)
            self.img_layout.addWidget(label, 0, x)
        title = QLabel()
        title.setText("{}".format(self.data[0][self.step_indx]))
        title.setAlignment(QtCore.Qt.AlignVCenter)
        title.setStyleSheet(style)
        self.txt_layout.addWidget(title, 0, 0, 1, 2)
        for x in range(6):
            label = QLabel()
            label2 = QLabel()
            txt = main_labels[1][x]
            txt2 = "{}".format(self.data[3][self.step_indx][x])
            label.setText(txt)
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            label2.setText(txt2)
            label.setStyleSheet(style)
            label2.setStyleSheet(style)
            label2.setAlignment(QtCore.Qt.AlignCenter)
            self.txt_layout.addWidget(label, x+1, 0)
            self.txt_layout.addWidget(label2, x+1, 1)

    def next_data(self):
        self.score_flag = self.step_indx
        if self.step_indx == self.hnd_cnt:
            self.next_btn.setText('Continue')
            self.next_btn.disconnect()
            self.next_btn.clicked.connect(self.close_continue)
            self.timer = QTimer(interval=400)
            self.timer.timeout.connect(self.flashing_btn)
            self.timer.start()
        else:
            self.step_indx += 1
            self.set_data()

    def close_continue(self):
        self.score_flag = 3
        self.main_widget.close()

    def flashing_btn(self):
        if self.flash_flag:
            self.next_btn.setStyleSheet("background-color: blue")
        else:
            self.next_btn.setStyleSheet("background-color: #464646")
        self.flash_flag = not self.flash_flag


if __name__ == '__main__':
    pass
