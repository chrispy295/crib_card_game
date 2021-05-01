import sys
import os
import random
from PyQt5.QtWidgets import QMainWindow, QFrame, QLabel, QHBoxLayout, QPushButton, QMessageBox, QApplication
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QColor, QPainter, QPixmap
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QTimer
from game_animations import GameAnimations
from calc_utils import peg_board_outline, peg_board_score_ref
from game_play_labels import main_labels


class BoxSelectSignals(QLabel):
    l_click = pyqtSignal()
    r_click = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.l_click.emit()
        if event.button() == Qt.RightButton:
            self.r_click.emit()


class PlayCardSignals(QLabel):
    l_click = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.l_click.emit()


class MainGui(QMainWindow):
    def ui_setup(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        main_bg_path = os.path.join(self.base_dir, 'static/main_bg.jpg')
        self.setStyleSheet("background-image: url({}); background-repeat: no-repeat; "
                           "background-position: center;".format(main_bg_path))
        self.setFixedWidth(1366)    # need to make this scalable
        self.setFixedHeight(768)
        self.main_brd = QFrame(self)
        self.main_brd.setGeometry(20, 80, 1000, 650)
        self.main_brd.setStyleSheet("background: transparent"
                                    ";")
        self.main_brd.setLineWidth(5)
        self.timer = QTimer()
        self.cut_box_flag = 0
        self.box_confirm_flag = 0
        self.p_crib_cards = []  # player crib cards
        self.p_crib_refs = []  # screen obj reference
        self.lay_x_offset = 0
        self.play_lay_permit = []
        self.p_lay_flag = 0
        self.obj_lay_refs = []
        self.play_lay_select = ''

    def menu_set(self):
        self.help_win = QFrame(self)
        self.help_win.setGeometry(40, 70, 500, 300)
        self.help_win.setStyleSheet("background:#84446C;")
        self.help_win.setFrameStyle(QFrame.Panel | QFrame.Raised)
        h_box = QHBoxLayout(self.help_win)
        text_edit = QPlainTextEdit()
        text_edit.move(20, 20)
        text_edit.resize(360, 260)
        text = os.path.join(self.base_dir, 'help_txt.txt')
        with open(text, "r") as rf:
            lines = rf.read()
        text_edit.setPlainText(lines)
        rf.close()
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.help_win.close)
        h_box.addWidget(text_edit)
        h_box.addWidget(close_btn)
        self.help_win.show()

    def set_menu_btns(self):
        self.menu_frm = QFrame(self)
        self.menu_frm.setGeometry(40, 10, 940, 60)
        self.menu_frm.setStyleSheet("background:#84446C;")
        self.menu_frm.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.menu_frm.setLineWidth(3)
        h_box = QHBoxLayout(self.menu_frm)
        s_sheet = "font-size: 18px"
        lbl = QLabel('Player:')
        lbl.setFixedWidth(49)
        lbl.setStyleSheet(s_sheet)
        self.cur_user = QLabel('')
        self.cur_user.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.cur_user.setStyleSheet(s_sheet)
        self.game_btn = QPushButton('New Game')
        self.p_select_btn = QPushButton('Change Player')
        self.add_new_btn = QPushButton('Player Add')
        self.remove_btn = QPushButton('Delete Player')
        self.stats_btn = QPushButton('Stats Overview')
        self.graph_btn = QPushButton('Graph Stats')
        self.inst_btn = QPushButton('Help')
        self.exit_btn = QPushButton('Exit')
        h_box.addWidget(lbl)
        h_box.addWidget(self.cur_user)
        h_box.addWidget(self.game_btn)
        h_box.addWidget(self.p_select_btn)
        h_box.addWidget(self.add_new_btn)
        h_box.addWidget(self.remove_btn)
        h_box.addWidget(self.stats_btn)
        h_box.addWidget(self.graph_btn)
        h_box.addWidget(self.inst_btn)
        h_box.addWidget(self.exit_btn)
        self.menu_frm.setLayout(h_box)
        self.btn_objs = [self.game_btn, self.p_select_btn, self.add_new_btn, self.remove_btn, self.stats_btn,
                         self.graph_btn]
        self.exit_btn.clicked.connect(self.on_exit)
        self.menu_frm.show()

    def btns_set_enable(self, flag_list):
        for x in range(len(flag_list)):
            self.btn_objs[x].setEnabled(flag_list[x])

    def set_single_image(self, card, x, y):
        path = os.path.join(self.base_dir, 'static/deck/{}.png'.format(card))
        img = QLabel(self.main_brd)
        pixmap = QPixmap(path)
        img.setPixmap(pixmap)
        img.move(x, y)
        img.raise_()
        img.resize(pixmap.width(), pixmap.height())
        img.show()
        return img

    def add_lbl_single(self, text, colour, x, y, p_size=20, size_os_wid=0, hgt_os=0):
        lbl = QLabel()
        lbl.setText('{}'.format(text))
        lbl.setParent(self.main_brd)
        lbl.move(x, y)
        lbl.setFixedWidth(200 + size_os_wid)
        lbl.setFixedHeight(40 + hgt_os)
        lbl.adjustSize()
        lbl.setStyleSheet("color: {}; font-size: {}px; background: transparent".format(colour, p_size))
        lbl.show()
        return lbl

    def cut_for_box_anim(self, p_card, c_card):
        self.p_cut = p_card
        self.c_cut = c_card
        self.cut_box_cards_ref = []
        path = os.path.join(self.base_dir, 'static/deck/bk.png')
        self.cut_box_anim = GameAnimations()
        x = 0
        while x < 44:
            p_img_lbl = PlayCardSignals()
            pixmap = QPixmap(path)
            p_img_lbl.setPixmap(pixmap)
            p_img_lbl.setParent(self.main_brd)
            p_img_lbl.resize(pixmap.width(), pixmap.height())
            p_img_lbl.show()
            self.cut_box_cards_ref.append(p_img_lbl)
            x += 1
        for ref in self.cut_box_cards_ref:
            self.cut_box_set_slots(ref)
        self.cut_box_anim.cut_card_animation(self.cut_box_cards_ref)

    def cut_select(self, obj):
        px = obj.x()
        py = obj.y() + 200
        obj.close()
        self.cut_box_cards_ref.remove(obj)
        c_ref = random.choice(self.cut_box_cards_ref)
        self.cut_box_cards_ref.remove(c_ref)
        cx = c_ref.x()
        cy = c_ref.y() - 200
        c_ref.close()
        self.p_cut_img = self.set_single_image(self.p_cut, px, py)
        self.c_cut_img = self.set_single_image(self.c_cut, cx, cy)
        self.timer.singleShot(500, lambda: self.cut_box_anim.cut_card_anim_remove(self.cut_box_cards_ref))
        self.timer.singleShot(2500, self.cut_clean_up)

    def cut_clean_up(self):
        self.cut_box_flag = 1
        for obj in self.cut_box_cards_ref:
            obj.close()
        self.p_cut_img.close()
        self.c_cut_img.close()
        self.cut_box_cards_ref = []

    def cut_box_set_slots(self, deck_img):
        deck_img.l_click.connect(lambda: self.cut_select(deck_img))

    def set_comp_cards_initial(self, idx1, idx2):
        self.comp_animations = GameAnimations()
        self.c_img_obj_ref = []
        path = os.path.join(self.base_dir, 'static/deck/bk.png')
        x = 0
        while x < 6:
            c_img_lbl = QLabel()
            pixmap = QPixmap(path)
            c_img_lbl.setPixmap(pixmap)
            c_img_lbl.setParent(self.main_brd)
            c_img_lbl.resize(pixmap.width(), pixmap.height())
            c_img_lbl.show()
            self.c_img_obj_ref.append(c_img_lbl)
            x += 1
        self.comp_animations.deal_animation(self.c_img_obj_ref, 0, 650, 20)
        self.timer.singleShot(1600, lambda: self.move_comp_crib_cards(idx1, idx2))

    def move_comp_crib_cards(self, idx1, idx2):
        self.c_crib_ref = []
        ref1 = self.c_img_obj_ref[idx1]
        ref2 = self.c_img_obj_ref[idx2]
        cx1 = ref1.x()
        cy1 = ref1.y() + 40
        cx2 = ref2.x()
        cy2 = ref2.y() + 40
        ref1.move(cx1, cy1)
        ref2.move(cx2, cy2)
        self.c_crib_ref.append(ref1)
        self.c_crib_ref.append(ref2)

    def set_player_cards_initial(self, cards):
        self.cards = cards
        self.player_animations = GameAnimations()
        self.p_img_obj_ref = []
        self.cards_connect = []
        for crd in cards:
            path = os.path.join(self.base_dir, 'static/deck/{}.png'.format(crd))
            p_img_lbl = BoxSelectSignals()
            pixmap = QPixmap(path)
            p_img_lbl.setPixmap(pixmap)
            p_img_lbl.setParent(self.main_brd)
            p_img_lbl.resize(pixmap.width(), pixmap.height())
            p_img_lbl.show()
            self.p_img_obj_ref.append(p_img_lbl)
        self.player_animations.deal_animation(self.p_img_obj_ref, 0, 0, 460)
        for x in range(len(self.p_img_obj_ref)):
            self.set_crib_select_slots(self.p_img_obj_ref[x], self.cards[x])

    def set_crib_select_slots(self, p_img_obj, card):
        p_img_obj.l_click.connect(lambda: self.box_card_select(p_img_obj, card))
        p_img_obj.r_click.connect(lambda: self.box_card_deselect(p_img_obj, card))

    @staticmethod
    def slot_disconnect(obj_ref):
        obj_ref.l_click.disconnect()
        obj_ref.r_click.disconnect()

    def box_card_select(self, obj_ref, card):
        if obj_ref not in self.p_crib_refs and len(self.p_crib_refs) < 2:
            self.p_crib_refs.append(obj_ref)
            self.p_crib_cards.append(card)
            x = obj_ref.x()
            y = obj_ref.y()
            obj_ref.move(x, y-40)
        if len(self.p_crib_refs) == 2:
            self.crib_confirm()

    def box_card_deselect(self, obj_ref, card):
        if obj_ref in self.p_crib_refs:
            self.p_crib_refs.remove(obj_ref)
            self.p_crib_cards.remove(card)
            x = obj_ref.x()
            y = obj_ref.y()
            obj_ref.move(x, y + 40)

    def crib_confirm(self):
        reply = QMessageBox.question(None, "Box Confirm", "Are the Cards Correct ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.move_crib_cards()
        else:
            for ref in self.p_crib_refs:
                x = ref.x()
                y = ref.y()
                ref.move(x, y + 40)
            self.p_crib_cards = []
            self.p_crib_refs = []

    def move_crib_cards(self):
        self.cards_connect = []
        self.box_anim = GameAnimations()
        self.card_anim = GameAnimations()
        end_x = 20
        if self.d_flag == 1:
            end_y = 460
        else:
            end_y = 20
        px1 = self.p_crib_refs[0].x()
        py1 = self.p_crib_refs[0].y()
        px2 = self.p_crib_refs[1].x()
        py2 = self.p_crib_refs[1].y()
        p_ref1 = self.p_crib_refs[0]
        p_ref2 = self.p_crib_refs[1]
        idx1 = self.p_img_obj_ref.index(p_ref1)
        idx2 = self.p_img_obj_ref.index(p_ref2)
        p1 = self.cards[idx1]
        p2 = self.cards[idx2]
        self.p_img_obj_ref.remove(p_ref1)
        self.p_img_obj_ref.remove(p_ref2)
        self.cards.remove(p1)
        self.cards.remove(p2)
        c_ref1 = self.c_crib_ref[0]
        c_ref2 = self.c_crib_ref[1]
        self.c_img_obj_ref.remove(c_ref1)
        self.c_img_obj_ref.remove(c_ref2)
        p_ref1.close()
        p_ref2.close()
        p_ref1 = self.set_single_image('bk', px1, py1)
        p_ref2 = self.set_single_image('bk', px2, py2)
        self.crib_imgs = (p_ref1, p_ref2, c_ref1, c_ref2)
        for x in range(len(self.p_img_obj_ref)):
            self.p_img_obj_ref[x].disconnect()
            self.play_game_set_slots(self.p_img_obj_ref[x], self.cards[x])
        self.box_anim.box_cards_animation(self.crib_imgs, end_x, end_y)
        self.card_anim.set_game_cards_anims(self.p_img_obj_ref, self.c_img_obj_ref)
        self.timer.singleShot(1600, lambda: self.box_clean_up(self.crib_imgs))

    def box_clean_up(self, objs):
        self.box_confirm_flag = 1
        self.crib_bk = objs[0]
        for obj in objs[1:]:
            obj.close()

    def play_game_set_slots(self, p_img_obj, card):
        p_img_obj.l_click.connect(lambda: self.move_player_card(p_img_obj, card))

    def move_player_card(self, p_img_obj, card):
        if card not in self.play_lay_permit or not self.p_lay_flag:
            return
        else:
            self.play_lay_select = card
            self.obj_lay_refs.append(p_img_obj)
            p_img_obj.disconnect()
            p_img_obj.raise_()
            self.player_animations = GameAnimations()
            self.player_animations.move_lay_card_anim(p_img_obj, self.lay_x_offset, 10)
            self.lay_x_offset += 60

    def move_comp_card(self, obj, card):
        self.c_img_obj_ref.remove(obj)
        x = obj.x()
        y = obj.y()
        obj.close()
        c_obj = self.set_single_image(card, x, y)
        self.obj_lay_refs.append(c_obj)
        self.comp_animations = GameAnimations()
        self.comp_animations.move_lay_card_anim(c_obj, self.lay_x_offset, -10)
        self.lay_x_offset += 60

    def pegging_scores(self, scores, colour):
        self.lay_anim = GameAnimations()
        self.lbl_ref = []
        if colour == 'green':
            start_y = 610
        else:
            start_y = 40
        for x in range(len(scores)):
            if scores[x] > 0:
                txt = main_labels[0][x].format(scores[x])
                lbl = self.add_lbl_single(txt, colour, 880, start_y, p_size=22)
                self.lbl_ref.append(lbl)
        self.lay_anim.lay_score_animations(self.lbl_ref)
        self.timer.singleShot(1200, self.label_lay_clear)

    def go_heel_pegging(self, colour, txt_flag):
        self.lay_anim2 = GameAnimations()
        if not txt_flag:
            txt = '2 For Heels'
        else:
            txt = '1 For Last'
        if colour == 'green':
            start_y = 610
        else:
            start_y = 40
        lbl = self.add_lbl_single(txt, colour, 880, start_y, p_size=22)
        self.lay_anim2.lay_score_animations([lbl])
        self.timer.singleShot(2300, lbl.close)

    def label_lay_clear(self):
        for obj in self.lbl_ref:
            obj.close()

    def game_over_animinations(self, p_score, c_score):
        self.game_over_ani = GameAnimations()
        if p_score > c_score:
            txt = 'You Won'
            colour = 'green'
            txt_split = txt.split()
        else:
            txt = 'You Lost'
            colour = 'red'
            txt_split = txt.split()
        lb1 = self.add_lbl_single(txt_split[0], colour, 60, -100, 70, hgt_os=20)
        lb2 = self.add_lbl_single(txt_split[1], colour, 1100, 750, 70, hgt_os=20)
        lb3 = self.add_lbl_single('Game Over', colour, 530, -100, 70, size_os_wid=200, hgt_os=20)
        self.lbls = [lb1, lb2, lb3]
        self.game_over_ani.game_over_anim(self.lbls)
        self.timer.singleShot(6000, self.clear_game_over_lbls)

    def clear_game_over_lbls(self):
        for lbl in self.lbls:
            lbl.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.on_exit()

    @staticmethod
    def on_exit():
        reply = QMessageBox.question(None, "Exit", "Are You Sure",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit()


class CribBrd(QFrame):
    def set_brd(self, parent):
        self.p_anim = GameAnimations()
        self.c_anim = GameAnimations()
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.setParent(parent)
        self.setGeometry(1020, 10, 320, 730)
        self.setStyleSheet("background: transparent")
        self.p1_peg_scores = [0]
        self.p2_peg_scores = [0]
        self.c1_peg_scores = [0]
        self.c2_peg_scores = [0]
        self.c_score_master = [0]
        self.p_score_master = [0]
        self.p_p_1_cords, self.p_p_2_cords, self.c_p_1_cords, self.c_p_2_cords = peg_board_score_ref()
        self.polygon = peg_board_outline()
        s_sheet = "color: red; font-size: 25px; background: transparent"
        lbl = QLabel(self)
        lbl.setText('Comp Score')
        lbl.move(0, 170)
        lbl.setStyleSheet(s_sheet)
        self.c_s_lbl = QLabel(self)
        self.c_s_lbl.setText('0')
        self.c_s_lbl.setFixedWidth(45)
        self.c_s_lbl.move(55, 205)
        self.c_s_lbl.setStyleSheet(s_sheet)
        s_sheet = "color: green; font-size: 25px; background: transparent"
        lbl = QLabel(self)
        lbl.setText('Play Score')
        lbl.move(180, 440)
        lbl.setStyleSheet(s_sheet)
        self.p_s_lbl = QLabel(self)
        self.p_s_lbl.setText('0')
        self.p_s_lbl.setFixedWidth(45)
        self.p_s_lbl.move(215, 475)
        self.p_s_lbl.setStyleSheet(s_sheet)
        self.p_peg_turn = 0
        self.c_peg_turn = 0

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHints(QPainter.Antialiasing)
        brd = QPolygonF()
        for point in self.polygon:
            cords = QPointF(point[0], point[1])
            brd.append(cords)
        qp.setPen(QPen(QColor(99, 30, 41), 2, Qt.SolidLine))
        qp.drawPolygon(brd)
        qp.end()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHints(QPainter.Antialiasing)
        for cord in self.p_p_1_cords[1:]:
            qp.setPen(QPen(QColor(53, 209, 10), 2, Qt.SolidLine))
            qp.setBrush(QBrush(QColor(53, 209, 10)))
            qp.drawEllipse(cord[0], cord[1], 5, 5)
        for cord in self.c_p_1_cords[1:]:
            qp.setPen(QPen(QColor(235, 22, 15), 2, Qt.SolidLine))
            qp.setBrush(QBrush(QColor(235, 22, 15)))
            qp.drawEllipse(cord[0], cord[1], 5, 5)
        qp.end()

    def set_game_counters(self):
        self.p1_peg_scores = [0]
        self.p2_peg_scores = [0]
        self.c1_peg_scores = [0]
        self.c2_peg_scores = [0]
        path = os.path.join(self.base_dir, 'static/p_peg_img.png')
        path2 = os.path.join(self.base_dir, 'static/c_peg_img.png')
        self.c_peg_1 = QLabel(self)
        self.c_peg_1.setAttribute(Qt.WA_TranslucentBackground, True)
        self.c_peg_1.setPixmap(QPixmap(path2))
        self.c_peg_1.move(self.c_p_1_cords[0][0] - 10, self.c_p_1_cords[0][1] - 14)
        self.c_peg_2 = QLabel(self)
        self.c_peg_2.setAttribute(Qt.WA_TranslucentBackground, True)
        self.c_peg_2.setPixmap(QPixmap(path2))
        self.c_peg_2.move(self.c_p_2_cords[0][0] - 10, self.c_p_2_cords[0][1] - 14)
        self.p_peg_1 = QLabel(self)
        self.p_peg_1.setAttribute(Qt.WA_TranslucentBackground, True)
        self.p_peg_1.setPixmap(QPixmap(path))
        self.p_peg_1.move(self.p_p_1_cords[0][0] - 10, self.p_p_1_cords[0][1] - 14)
        self.p_peg_2 = QLabel(self)
        self.p_peg_2.setAttribute(Qt.WA_TranslucentBackground, True)
        self.p_peg_2.setPixmap(QPixmap(path))
        self.p_peg_2.move(self.p_p_2_cords[0][0] - 10, self.p_p_2_cords[0][1] - 14)

    def play_move_peg_icon(self, p_score):
        if p_score > 120:
            self.p_s_lbl.setText("{}".format(p_score))
            return
        else:
            end_indx = p_score
            if end_indx > 60:
                end_indx = p_score - 60
            if self.p_peg_turn:
                self.p1_peg_scores.append(end_indx)
                start_indx = self.p1_peg_scores[0]
                cords = self.p_p_1_cords[end_indx]
                if end_indx > start_indx:
                    inter_cords = self.p_p_1_cords[start_indx + 1:end_indx]
                else:
                    inter_cords = self.p_p_1_cords[start_indx:] + self.p_p_1_cords[:end_indx]
                self.p_anim.peg_counter_move(self.p_peg_1, QPointF(cords[0] - 10, cords[1] - 15), inter_cords,
                                             self.p_s_lbl, self.p_score_master[-1], p_score)
                if len(self.p1_peg_scores) == 2:
                    self.p1_peg_scores.pop(0)
                self.p_peg_turn = 0
                self.p_score_master.append(p_score)
            else:
                self.p2_peg_scores.append(end_indx)
                start_indx = self.p2_peg_scores[0]
                cords = self.p_p_2_cords[end_indx]
                if end_indx > start_indx:
                    inter_cords = self.p_p_2_cords[start_indx + 1:end_indx]
                else:
                    inter_cords = self.p_p_2_cords[start_indx:] + self.p_p_2_cords[:end_indx]
                self.p_anim.peg_counter_move(self.p_peg_2, QPointF(cords[0] - 10, cords[1] - 15), inter_cords,
                                             self.p_s_lbl, self.p_score_master[-1], p_score)
                if len(self.p2_peg_scores) == 2:
                    self.p2_peg_scores.pop(0)
                self.p_peg_turn = 1
                self.p_score_master.append(p_score)

    def comp_move_peg_icon(self, c_score):
        if c_score > 120:
            self.c_s_lbl.setText("{}".format(c_score))
            return
        else:
            end_indx = c_score
            if end_indx > 60:
                end_indx = c_score - 60
            if self.c_peg_turn:
                self.c1_peg_scores.append(end_indx)
                start_indx = self.c1_peg_scores[0]
                cords = self.c_p_1_cords[end_indx]
                if end_indx > start_indx:
                    inter_cords = self.c_p_1_cords[start_indx + 1:end_indx]
                else:
                    inter_cords = self.c_p_1_cords[start_indx:] + self.c_p_1_cords[:end_indx]
                self.c_anim.peg_counter_move(self.c_peg_1, QPointF(cords[0] - 10, cords[1] - 15), inter_cords,
                                             self.c_s_lbl, self.c_score_master[-1], c_score)
                if len(self.c1_peg_scores) == 2:
                    self.c1_peg_scores.pop(0)
                self.c_peg_turn = 0
                self.c_score_master.append(c_score)
            else:
                self.c2_peg_scores.append(end_indx)
                start_indx = self.c2_peg_scores[0]
                cords = self.c_p_2_cords[end_indx]
                if end_indx > start_indx:
                    inter_cords = self.c_p_2_cords[start_indx + 1:end_indx]
                else:
                    inter_cords = self.c_p_2_cords[start_indx:] + self.c_p_2_cords[:end_indx]
                self.c_anim.peg_counter_move(self.c_peg_2, QPointF(cords[0] - 10, cords[1] - 15), inter_cords,
                                             self.c_s_lbl, self.c_score_master[-1], c_score)
                if len(self.c2_peg_scores) == 2:
                    self.c2_peg_scores.pop(0)
                self.c_peg_turn = 1
                self.c_score_master.append(c_score)

    def peg_reset(self):
        self.p_peg_1.move(self.p_p_1_cords[0][0], self.p_p_1_cords[0][1])
        self.p_peg_2.move(self.p_p_2_cords[0][0], self.p_p_2_cords[0][1])
        self.c_peg_1.move(self.c_p_1_cords[0][0], self.c_p_1_cords[0][1])
        self.c_peg_2.move(self.c_p_2_cords[0][0], self.c_p_2_cords[0][1])
        self.c_score_master = [0]
        self.p_score_master = [0]
        self.p1_peg_scores = [0]
        self.p2_peg_scores = [0]
        self.c1_peg_scores = [0]
        self.c2_peg_scores = [0]
        self.p_s_lbl.setText('0')
        self.c_s_lbl.setText('0')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    width, height = size.width(), size.height()
    main = MainGui()
    main.ui_setup()
    main.showMaximized()
    peg = CribBrd()
    peg.set_brd(main)
    peg.set_game_counters()
    peg.show()
    peg.play_move_peg_icon(40)
    peg.comp_move_peg_icon(50)
    sys.exit(app.exec_())
