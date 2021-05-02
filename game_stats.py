import sqlite3
import os
from PyQt5.QtWidgets import QDialog, QPushButton, QGridLayout, QLabel, QWidget, QMainWindow, QDockWidget,  QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from game_play_labels import main_labels as mwl


# noinspection PyTypeChecker
class GameStats:
    def __init__(self, parent, user):
        self.master = parent
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.user_db = sqlite3.connect(os.path.join(self.base_dir, 'databases/{}_stats.db').format(user))

    def db_check(self):
        cur = self.user_db.cursor()
        cur.execute("SELECT max(rowid) from player")
        num = cur.fetchone()[0]
        cur.close()
        return num

    def game_summary(self, p_obj, c_obj):
        self.p_obj = p_obj
        self.c_obj = c_obj
        self.p_stats = [self.p_obj.score, self.p_obj.hand_totals, self.p_obj.box_totals, self.p_obj.peg_total,
                        sum(self.p_obj.heels), sum(self.p_obj.fifth), sum(self.p_obj.pairs), sum(self.p_obj.runs),
                        sum(self.p_obj.thirties), sum(self.p_obj.last), self.p_obj.win, self.p_obj.hand_num,
                        self.p_obj.hand_hi, self.p_obj.box_hi, self.p_obj.hands_0, self.p_obj.box_0,
                        self.p_obj.first_crib]
        self.c_stats = [self.c_obj.score, self.c_obj.hand_totals, self.c_obj.box_totals, self.c_obj.peg_total,
                        sum(self.c_obj.heels), sum(self.c_obj.fifth), sum(self.c_obj.pairs), sum(self.c_obj.runs),
                        sum(self.c_obj.thirties), sum(self.c_obj.last), self.c_obj.win, self.c_obj.hand_num,
                        self.c_obj.hand_hi, self.c_obj.box_hi, self.c_obj.hands_0, self.c_obj.box_0,
                        self.c_obj.first_crib]
        cur = self.user_db.cursor()
        cur.execute('''INSERT INTO player(Score, Hand_Total, Box_Total, Peg_Total, Heels, Fifth, Pairs, Runs, Thirty,
                                       Last, Wins, Num_Hands, Hand_Hi, Box_Hi, H_Zero, B_zero, No_Crib)
                                          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?, ?)''', self.p_stats)
        cur.execute('''INSERT INTO comp(Score, Hand_Total, Box_Total, Peg_Total, Heels, Fifth, Pairs, Runs, Thirty,
                                               Last, Wins, Num_Hands, Hand_Hi, Box_Hi, H_Zero, B_zero, No_Crib)
                                                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?, ?)''', self.c_stats)
        self.user_db.commit()
        cur.close()
        self.game_summary_win()

    def game_summary_win(self):
        titles = ['Stats', 'Player', 'Comp']
        win = QDialog(self.master)
        win.setWindowTitle('Games Summary Table')
        win.setGeometry(1020, 30, 300, 500)
        win.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        win.setStyleSheet("background: #3f434a")
        close_btn = QPushButton('Close')
        grid = QGridLayout()
        win.setLayout(grid)
        for y in range(3):
            lbl = QLabel(titles[y], alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lbl, 0, y)
        for x in range(17):
            lbl1 = QLabel(mwl[2][x], alignment=QtCore.Qt.AlignRight)
            grid.addWidget(lbl1, x + 1, 0)
            lb2 = QLabel(str(self.p_stats[x]), alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lb2, x + 1, 1)
            lb2 = QLabel(str(self.c_stats[x]), alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lb2, x + 1, 2)
        grid.addWidget(close_btn, 18, 1)
        close_btn.clicked.connect(win.close)
        win.show()

    def data_format(self):
        cur = self.user_db.cursor()
        play = cur.execute('''SELECT SUM(Score), SUM(Hand_Total), SUM(Box_Total), SUM(Peg_Total), SUM(Heels),
         SUM(Fifth), SUM(Pairs), SUM(Runs), SUM(Thirty), SUM(Last), SUM(H_Zero), SUM(B_Zero),SUM(No_Crib), SUM(Wins),
         SUM(Num_Hands),  MAX(Hand_Hi), MAX(Box_Hi) FROM player''')
        self.p_data = list(play.fetchone())
        comp = cur.execute('''SELECT SUM(Score), SUM(Hand_Total), SUM(Box_Total), SUM(Peg_Total), SUM(Heels),
        SUM(Fifth), SUM(Pairs), SUM(Runs), SUM(Thirty), SUM(Last), SUM(H_Zero), SUM(B_Zero),SUM(No_Crib), SUM(Wins),
        SUM(Num_Hands),  MAX(Hand_Hi), MAX(Box_Hi) FROM comp''')
        self.c_data = list(comp.fetchone())
        cur.close()
        cur = self.user_db.cursor()
        play = cur.execute(''' SELECT * FROM player''')
        self.g_tot = len(play.fetchall())
        cur.close()

    def stats_overview(self):
        self.data_format()
        titles = ['Stats', 'Player', 'Comp']
        win = QWidget(self.master)
        win.setWindowTitle('Games Smmary Table')
        win.setGeometry(40, 80, 280, 510)
        win.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        win.setStyleSheet("background: #3f434a")
        grid = QGridLayout()
        win.setLayout(grid)
        close_btn = QPushButton('Close')
        for y in range(3):
            lbl = QLabel(titles[y], alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lbl, 0, y)
        for x in range(10):
            lbl1 = QLabel(mwl[3][x], alignment=QtCore.Qt.AlignRight)
            grid.addWidget(lbl1, x+1, 0)
            lb2 = QLabel(str(round(self.p_data[x] / self.g_tot, 2)), alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lb2, x+1, 1)
            lb2 = QLabel(str(round(self.c_data[x] / self.g_tot, 2)), alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lb2, x + 1, 2)
        for x in range(10, 17):
            lbl1 = QLabel(mwl[3][x], alignment=QtCore.Qt.AlignRight)
            grid.addWidget(lbl1, x + 1, 0)
            lb2 = QLabel(str(self.p_data[x]), alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lb2, x + 1, 1)
            lb2 = QLabel(str(self.c_data[x]), alignment=QtCore.Qt.AlignCenter)
            grid.addWidget(lb2, x + 1, 2)
        grid.addWidget(close_btn, 18, 1)
        close_btn.clicked.connect(win.close)
        win.show()

    def graphs(self):
        self.flash_flag = 0
        self.data_format()
        self.x_lbl = list(range(1, self.g_tot + 1))
        self.graph_window = QMainWindow(self.master)
        self.graph_window.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.graph_window.setGeometry(40, 100, 1140, 510)
        self.graph_window.setStyleSheet("background: #3f434a")
        self.graph_widget = pg.PlotWidget(self.graph_window)
        self.graph_widget.setBackground('#433840')
        self.graph_window.setCentralWidget(self.graph_widget)
        dock = QDockWidget(self.graph_window)
        dock.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.graph_window.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)
        widget = QWidget()
        self.close_btn = QPushButton('Close Graphs')
        self.clear_btn = QPushButton('Clear Graph')
        self.game_tots_btn = QPushButton('Game Totals')
        self.hand_tots_btn = QPushButton('Hand Totals')
        self.box_tots_btn = QPushButton('Box Totals')
        self.peg_tots_btn = QPushButton('Peg_Totals')
        self.clear_btn.clicked.connect(self.clear_plot)
        self.close_btn.clicked.connect(self.graph_window.close)
        self.game_tots_btn.clicked.connect(self.game_score_tots)
        self.hand_tots_btn.clicked.connect(self.hand_score_tots)
        self.box_tots_btn.clicked.connect(self.box_score_tots)
        self.peg_tots_btn.clicked.connect(self.peg_score_tots)
        self.clear_btn.setEnabled(False)
        h_box = QHBoxLayout()
        h_box.addWidget(self.game_tots_btn)
        h_box.addWidget(self.hand_tots_btn)
        h_box.addWidget(self.box_tots_btn)
        h_box.addWidget(self.peg_tots_btn)
        h_box.addWidget(self.clear_btn)
        h_box.addWidget(self.close_btn)
        widget.setLayout(h_box)
        dock.setWidget(widget)
        styles = {'color': '#df6f14', 'font-size': '16px'}
        self.graph_widget.setLabel('left', 'Score', **styles)
        self.graph_widget.setLabel('bottom', 'Game No', **styles)
        pg.setConfigOptions(antialias=True)
        self.pc = pg.mkPen(color=(84, 179, 30))
        self.cc = pg.mkPen(color=(229, 0, 0))
        self.graph_window.show()

    def flashing_btn(self):
        if self.flash_flag:
            self.clear_btn.setStyleSheet("background-color: blue")
        else:
            self.clear_btn.setStyleSheet("background-color:  #433840")
        self.flash_flag = not self.flash_flag

    def clear_plot(self):
        self.timer.stop()
        self.graph_widget.removeItem(self.plot1)
        self.graph_widget.removeItem(self.plot2)
        self.game_tots_btn.setEnabled(True)
        self.hand_tots_btn.setEnabled(True)
        self.box_tots_btn.setEnabled(True)
        self.peg_tots_btn.setEnabled(True)
        self.clear_btn.setEnabled(False)

    def game_score_tots(self):
        self.clear_btn.setEnabled(True)
        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.flashing_btn)
        self.timer.start()
        self.game_tots_btn.setEnabled(False)
        self.hand_tots_btn.setEnabled(False)
        self.box_tots_btn.setEnabled(False)
        self.peg_tots_btn.setEnabled(False)
        cur = self.user_db.cursor()
        txt = 'Score Totals Per Game'
        play = cur.execute('''SELECT Score FROM player''')
        p_data = [x[0] for x in play.fetchall()]
        comp = cur.execute('''SELECT Score FROM comp''')
        c_data = [x[0] for x in comp.fetchall()]
        self.graph_widget.addLegend(offset=(10, 10), width=30)
        self.plot1 = self.graph_widget.plot(self.x_lbl, p_data, pen=self.pc, symbol='o', name='Play')
        self.plot2 = self.graph_widget.plot(self.x_lbl, c_data, pen=self.cc, symbol='o', name='Comp')
        cur.close()

    def hand_score_tots(self):
        self.clear_btn.setEnabled(True)
        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.flashing_btn)
        self.timer.start()
        self.game_tots_btn.setEnabled(False)
        self.hand_tots_btn.setEnabled(False)
        self.box_tots_btn.setEnabled(False)
        self.peg_tots_btn.setEnabled(False)
        cur = self.user_db.cursor()
        txt = 'Hand Totals Per Game'
        play = cur.execute('''SELECT Hand_Total FROM player''')
        p_data = [x[0] for x in play.fetchall()]
        comp = cur.execute('''SELECT Hand_Total FROM comp''')
        c_data = [x[0] for x in comp.fetchall()]
        self.plot1 = self.graph_widget.plot(self.x_lbl, p_data, pen=self.pc, symbol='o', name='Play')
        self.plot2 = self.graph_widget.plot(self.x_lbl, c_data, pen=self.cc, symbol='o', name='Comp')
        cur.close()

    def box_score_tots(self):
        self.clear_btn.setEnabled(True)
        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.flashing_btn)
        self.timer.start()
        self.game_tots_btn.setEnabled(False)
        self.hand_tots_btn.setEnabled(False)
        self.box_tots_btn.setEnabled(False)
        self.peg_tots_btn.setEnabled(False)
        cur = self.user_db.cursor()
        txt = 'Box Totals Per Game'
        play = cur.execute('''SELECT Box_Total FROM player''')
        p_data = [x[0] for x in play.fetchall()]
        comp = cur.execute('''SELECT Box_Total FROM comp''')
        c_data = [x[0] for x in comp.fetchall()]
        self.plot1 = self.graph_widget.plot(self.x_lbl, p_data, pen=self.pc, symbol='o', name='Play')
        self.plot2 = self.graph_widget.plot(self.x_lbl, c_data, pen=self.cc, symbol='o', name='Comp')
        cur.close()

    def peg_score_tots(self):
        self.clear_btn.setEnabled(True)
        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.flashing_btn)
        self.timer.start()
        self.game_tots_btn.setEnabled(False)
        self.hand_tots_btn.setEnabled(False)
        self.box_tots_btn.setEnabled(False)
        self.peg_tots_btn.setEnabled(False)
        cur = self.user_db.cursor()
        txt = 'Peg Totals Per Game'
        play = cur.execute('''SELECT Peg_Total FROM player''')
        p_data = [x[0] for x in play.fetchall()]
        comp = cur.execute('''SELECT Peg_Total FROM comp''')
        c_data = [x[0] for x in comp.fetchall()]
        self.plot1 = self.graph_widget.plot(self.x_lbl, p_data, pen=self.pc, symbol='o', name='Play')
        self.plot2 = self.graph_widget.plot(self.x_lbl, c_data, pen=self.cc, symbol='o', name='Comp')
        cur.close()


if __name__ == '__main__':
    pass

