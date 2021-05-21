import sys
import random
import pickle
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from db_manage import UserManage
from gui_main import MainGui, CribBrd
from game_classes import HandState, LayCards
from calc_utils import define_deck, dealer_select, hand_sort, lay_score_calc
from lay_end_utils import score_master
from lay_end_score_window import LayEndScoreWindow
from comp_lay_select import lay_card_calc
from comp_hand_calc import comp_hand_select
from game_stats import GameStats


class MainCtl:
    def set_ui(self):
        self.flag_reset = 0
        self.timer = QTimer()
        self.main_gui = MainGui()
        self.main_gui.ui_setup(self)
        self.main_gui.set_menu_btns()
        self.peg_brd = CribBrd()  # scores and moves crib counters
        self.peg_brd.set_brd(self.main_gui)
        self.peg_brd.set_game_counters()
        self.db_initial_update()
        self.main_gui.showMaximized()
        self.btn_define_connect()

    def btn_define_connect(self):
        self.main_gui.game_btn.clicked.connect(self.game_initial)
        self.main_gui.add_new_btn.clicked.connect(self.main_gui.new_user)
        self.main_gui.p_select_btn.clicked.connect(lambda: self.main_gui.player_manage(0))
        self.main_gui.remove_btn.clicked.connect(lambda: self.main_gui.player_manage(1))
        self.main_gui.stats_btn.clicked.connect(self.show_game_stats)
        self.main_gui.graph_btn.clicked.connect(self.show_graphs)
        self.main_gui.inst_btn.clicked.connect(self.main_gui.menu_help)

    def db_initial_update(self):
        file = open('last_user.pkl', 'rb')
        last_user = pickle.load(file)
        file.close()
        self.db_users = UserManage()
        self.user_list = self.db_users.user_read()
        if not self.user_list:
            self.main_gui.btns_set_enable([0, 0, 1, 0, 0, 0])    # set menu buttons enable/disable needs len 6
            self.main_gui.cur_user.setText('')
        else:
            if len(self.user_list) < 2:
                self.main_gui.btns_set_enable([1, 0, 1, 1, 1, 1])
            else:
                self.main_gui.btns_set_enable([1]*6)
            if last_user in self.user_list:
                player = last_user
                self.main_gui.cur_user.setText(player)
            else:
                player = self.user_list[0]
                self.main_gui.cur_user.setText(player)
            self.game_stats = GameStats(self.main_gui, player)
            db_check = self.game_stats.db_check()
            if not db_check and len(self.user_list) < 2:
                self.main_gui.btns_set_enable([1, 0, 1, 1, 0, 0])
            if not db_check and len(self.user_list) > 1:
                self.main_gui.btns_set_enable([1, 1, 1, 1, 0, 0])

    def db_change_confirm(self, flag):
        player = self.main_gui.users_combo.currentItem().text()
        if flag:
            reply = QMessageBox.question(None, "Delete User", "Delete user {} and his Database?\nThis Cannot Be Undone"
                                         .format(player))
        else:
            reply = QMessageBox.question(None, "Switch User", "Switch to  user {}".format(player))
        if flag and reply == QMessageBox.Yes:
            self.main_gui.p_manage_win.close()
            self.delete_user(player)
        elif not flag and reply == QMessageBox.Yes:
            self.main_gui.p_manage_win.close()
            file = open('last_user.pkl', 'wb')
            pickle.dump(player, file)
            file.close()
            self.db_initial_update()
            self.main_gui.p_manage_win.close()
        else:
            self.main_gui.p_manage_win.close()

    def add_new_user(self, name):
        self.db_users.user_add(name)
        player = '{}'.format(name)
        file = open('last_user.pkl', 'wb')
        pickle.dump(player, file)
        file.close()
        self.main_gui.add_new_btn.setEnabled(True)
        self.db_initial_update()

    def delete_user(self, name):
        self.db_users.user_delete(name)
        self.db_initial_update()

    def new_user_cancel(self):
        self.main_gui.new_user_win.close()
        self.db_initial_update()

    def new_user_confirm(self):
        player = self.main_gui.play_ent.text()
        if not player:
            QMessageBox.information(None, "Info", "Please enter a Name", QMessageBox.Ok)
            self.main_gui.play_ent.clear()
        else:
            if player[0].isdigit():
                QMessageBox.information(None, "Info", "Name can't Start With a Number", QMessageBox.Ok)
                self.main_gui.play_ent.clear()
            else:
                player = player.replace(" ", "")
                self.add_new_user(player)
                self.main_gui.new_user_win.close()

    def show_game_stats(self):
        self.game_stats.stats_overview()

    def show_graphs(self):
        self.game_stats.graphs()

    def game_initial(self):
        self.flag_reset = 1
        self.main_gui.menu_frm.close()
        self.p_hnd_obj = HandState()  # holds hand cards, score and peg values etc
        self.c_hnd_obj = HandState()
        self.lay_initial()
        self.dealer_select()

    def lay_initial(self):
        self.deck = define_deck()
        self.p_go_flag = 0
        self.c_go_flag = 0
        self.flag_31 = 0

    def dealer_select(self):
        self.deck = define_deck()
        p_crd = random.choice(self.deck)
        c_crd = random.choice(self.deck)
        self.d_flag = dealer_select(p_crd, c_crd)
        if self.d_flag == 1:
            self.p_hnd_obj.crib_first()
            self.main_gui.cut_for_box_anim(p_crd, c_crd)
            self.cut_flag()
        elif self.d_flag == 0:
            self.c_hnd_obj.crib_first()
            self.main_gui.cut_for_box_anim(p_crd, c_crd)
            self.cut_flag()
        else:
            self.dealer_select()

    def cut_flag(self):             # waits for users click for cut card
        if self.main_gui.cut_box_flag == 1:
            self.deal_hands()
        else:
            self.timer.singleShot(100, self.cut_flag)

    def deal_hands(self):
        self.deck_bk_img = self.main_gui.set_single_image('bk', 20, 265)
        self.main_gui.cut_box_flag = 0
        if self.d_flag == 1:
            self.deal_box_msg = self.main_gui.add_lbl_single('Your Box', '#32a852', 500, 320)
        else:
            self.deal_box_msg = self.main_gui.add_lbl_single('Computer Box', '#32a852', 470, 320)
        self.select_msg = self.main_gui.add_lbl_single('Select Box Cards', '#32a852', 460, 290)
        self.p_hand_6 = hand_sort(self.deck[:6])
        self.c_hand_6 = hand_sort(self.deck[6:12])
        self.c_hand, self.c_crib = comp_hand_select(self.c_hand_6, self.d_flag)
        self.main_gui.set_player_cards_initial(self.p_hand_6)
        ind1 = self.c_hand_6.index(self.c_crib[0])
        ind2 = self.c_hand_6.index(self.c_crib[1])
        self.main_gui.set_comp_cards_initial(ind1, ind2, self.c_hand_6)
        self.main_gui.d_flag = self.d_flag
        self.get_p_crib()

    def get_p_crib(self):
        if self.main_gui.box_confirm_flag == 1:
            self.hand_set()
        else:
            self.timer.singleShot(20, self.get_p_crib)

    def hand_set(self):
        self.main_gui.box_confirm_flag = 0
        self.select_msg.close()
        self.deal_box_msg.close()
        self.p_crib = self.main_gui.p_crib_cards[:]
        self.crib_final = self.p_crib + self.c_crib
        self.main_gui.p_crib_cards = []
        self.main_gui.p_crib_refs = []
        self.p_hnd_obj.add_hand(self.p_hand_6)
        self.c_hnd_obj.add_hand(self.c_hand)
        self.game_cut = random.choice(self.deck[12:])
        self.game_cut_img = self.main_gui.set_single_image(self.game_cut, 20, 265)
        self.p_hnd_obj.cut_card_add(self.game_cut)
        self.c_hnd_obj.cut_card_add(self.game_cut)
        self.crib_final.append(self.game_cut)
        self.lb_lay = self.main_gui.add_lbl_single('Lay Total:', '#32a852', 142, 380)
        self.lt_tot_lbl = self.main_gui.add_lbl_single('0', '#32a852', 240, 380)
        self.timer.singleShot(1000, self.lay_start)

    def lay_start(self):
        self.lc = LayCards()
        if self.game_cut[0] == 'J' and self.d_flag:
            self.main_gui.go_heel_pegging('green', 0)
            self.p_hnd_obj.score_update(2)
            self.p_hnd_obj.heel(2)
            self.peg_brd.play_move_peg_icon(self.p_hnd_obj.score)
        if self.game_cut[0] == 'J' and not self.d_flag:
            self.c_hnd_obj.score_update(2)
            self.c_hnd_obj.heel(2)
            self.main_gui.go_heel_pegging('red', 0)
            self.peg_brd.comp_move_peg_icon(self.c_hnd_obj.score)
        self.turn_flag = self.d_flag
        self.timer.singleShot(1500, self.lay_ctl)

    def lay_ctl(self):
        self.main_gui.p_permit_imgs = []
        if self.p_hnd_obj.score > 120 or self.c_hnd_obj.score > 120:
            self.timer.singleShot(1000, self.game_over)
        elif not self.c_hnd_obj.hand and not self.p_hnd_obj.hand:
            self.timer.singleShot(900, self.lay_end)
        elif self.flag_31 or (self.c_go_flag == 1 and self.p_go_flag == 1):
            self.timer.singleShot(1000, self.lay_reset)
        elif self.p_go_flag and not self.c_go_flag:
            self.timer.singleShot(400, self.comp_lay)
        elif self.c_go_flag and not self.p_go_flag:
            self.main_gui.mef = 2
            self.p_go_check()
        elif self.turn_flag:
            self.timer.singleShot(400, self.comp_lay)
        elif not self.turn_flag:
            self.main_gui.mef = 2
            self.p_go_check()

    def p_go_check(self):
        p_permit, self.p_permit_idxs = self.lc.lay_allow(self.p_hnd_obj.hand, self.p_hnd_obj.faces)
        self.main_gui.play_lay_permit = p_permit
        if not p_permit and not self.flag_31 and not self.p_go_flag:
            self.p_go_flag = 1
            self.p_go_lbl = self.main_gui.add_lbl_single('- Go -', 'green', 840, 570, 23)
            self.timer.singleShot(700, self.lay_ctl)
        else:
            self.main_gui.p_lay_flag = 1
            self.lay_rem_msg = self.main_gui.add_lbl_single('Your Lay', 'green', 490, 350, 29)
            self.p_card_capture()

    def p_card_capture(self):
        card = self.main_gui.play_lay_select
        if card:
            self.main_gui.p_lay_flag = 0
            self.player_lay(card)
        else:
            self.timer.singleShot(100, self.p_card_capture)

    def player_lay(self, card):
        self.lay_rem_msg.close()
        self.main_gui.play_lay_select = ''
        self.lc.add_card(card)
        self.lt_tot_lbl.setText('{}'.format(self.lc.lay_total))
        self.p_hnd_obj.card_remove(card)
        self.turn_flag = 1
        l_score = lay_score_calc(self.lc.pips, self.lc.faces)
        if sum(l_score) > 0:
            self.p_hnd_obj.score_update(sum(l_score))
            self.p_hnd_obj.lay_score_stats(l_score)
            self.main_gui.player_pegging_scores(l_score)
            self.peg_brd.play_move_peg_icon(self.p_hnd_obj.score)
            if l_score[3] > 0:
                self.flag_31 = 1
        self.timer.singleShot(1000, self.lay_ctl)

    def comp_lay(self):
        self.c_permit, self.c_permit_idx = self.lc.lay_allow(self.c_hnd_obj.hand, self.c_hnd_obj.faces)
        if not self.c_permit and not self.flag_31 and not self.c_go_flag:
            self.c_go_flag = 1
            self.c_go_lbl = self.main_gui.add_lbl_single('- Go -', 'red', 840, 20, 23)
        else:
            self.main_gui.mef = 0
            c_l_crd = lay_card_calc(self.lc.pips, self.lc.faces, self.c_permit)
            idx = self.c_hand.index(c_l_crd)
            img = self.main_gui.c_img_obj_ref[idx]
            self.c_hnd_obj.card_remove(c_l_crd)
            self.main_gui.move_comp_card(img, c_l_crd)
            self.lc.add_card(c_l_crd)
            self.lt_tot_lbl.setText('{}'.format(self.lc.lay_total))
            self.turn_flag = 0
            l_score = lay_score_calc(self.lc.pips, self.lc.faces)
            if sum(l_score) > 0:
                self.c_hnd_obj.score_update(sum(l_score))
                self.c_hnd_obj.lay_score_stats(l_score)
                self.main_gui.comp_pegging_scores(l_score)
                self.peg_brd.comp_move_peg_icon(self.c_hnd_obj.score)
                if l_score[3] > 0:
                    self.flag_31 = 1
        self.timer.singleShot(900, self.lay_ctl)

    def go_last_card(self):
        if self.turn_flag == 0:
            self.c_hnd_obj.score_update(1)
            self.c_hnd_obj.last_crd(1)
            self.main_gui.go_heel_pegging('red', 1)
            self.peg_brd.comp_move_peg_icon(self.c_hnd_obj.score)
        else:
            self.p_hnd_obj.score_update(1)
            self.p_hnd_obj.last_crd(1)
            self.main_gui.go_heel_pegging('green', 1)
            self.peg_brd.play_move_peg_icon(self.p_hnd_obj.score)

    def lay_reset(self):
        self.main_gui.lbl_pegging_ref = []
        if not self.flag_31:
            self.go_last_card()
        for img in self.main_gui.obj_lay_refs:
            img.close()
        self.main_gui.obj_lay_refs = []
        self.flag_31 = 0
        self.lc = LayCards()
        self.lt_tot_lbl.setText('0')
        if self.p_go_flag:
            self.p_go_lbl.close()
        if self.c_go_flag:
            self.c_go_lbl.close()
        self.p_go_flag = 0
        self.c_go_flag = 0
        self.main_gui.lay_x_offset = 0
        self.timer.singleShot(1500, self.lay_ctl)

    def lay_end(self):
        self.main_gui.lbl_pegging_ref = []
        if self.p_go_flag:
            self.p_go_lbl.close()
        if self.c_go_flag:
            self.c_go_lbl.close()
        if self.flag_31 == 0:
            self.go_last_card()
        if self.p_hnd_obj.score > 120 or self.c_hnd_obj.score > 120:
            self.timer.singleShot(2000, self.game_over)
        else:
            for img in self.main_gui.obj_lay_refs:
                img.close()
            self.main_gui.crib_imgs[0].close()
            self.main_gui.lay_x_offset = 0
            self.game_cut_img.close()
            self.deck_bk_img.close()
            self.lt_tot_lbl.close()
            self.lb_lay.close()
            self.timer.singleShot(2500, self.lay_end_count)

    def lay_end_count(self):
        p_scores = list(score_master(self.p_hnd_obj.hand_fin, 0, score_only=1))
        c_scores = list(score_master(self.c_hnd_obj.hand_fin, 0, score_only=1))
        crib_scores = list(score_master(self.crib_final, 1, score_only=1))
        if self.d_flag:
            self.hand_objs = [self.c_hnd_obj, self.p_hnd_obj, self.p_hnd_obj]
            title = ['Comp Hand', 'Player Hand', 'Player Box']
            fills = ['red', 'green', 'green']
            self.peg_flags = [0, 1, 1]
            cards = [self.c_hnd_obj.hand_fin, self.p_hnd_obj.hand_fin, self.crib_final]
            score_hnd = [self.c_hnd_obj.score, self.p_hnd_obj.score, self.p_hnd_obj.score]
            self.score_order = [c_scores, p_scores, crib_scores]
            data = (title, fills, cards, self.score_order)
        else:
            self.hand_objs = [self.p_hnd_obj, self.c_hnd_obj, self.c_hnd_obj]
            title = ['Player Hand', 'Comp Hand', 'Comp Box']
            fills = ['green', 'red', 'red']
            self.peg_flags = [1, 0, 0]
            cards = [self.p_hnd_obj.hand_fin, self.c_hnd_obj.hand_fin, self.crib_final]
            score_hnd = [self.p_hnd_obj.score, self.c_hnd_obj.score, self.c_hnd_obj.score]
            self.score_order = [p_scores, c_scores, crib_scores]
            data = (title, fills, cards, self.score_order)
        hnds_to_cnt = [x for x in range(3) if sum(self.score_order[x]) + score_hnd[x] > 120]
        if not hnds_to_cnt:
            cnt_idx = 2
        else:
            cnt_idx = hnds_to_cnt[0]
        p_scores.append(sum(p_scores))
        c_scores.append(sum(c_scores))
        crib_scores.append(sum(crib_scores))
        self.lsc = LayEndScoreWindow(self.main_gui, data, cnt_idx)
        self.lsc.main_widget.show()
        self.score_update_loop()

    def score_update_loop(self):
        if self.lsc.score_flag == 0:
            score = sum(self.score_order[0][:4])
            self.hand_objs[0].score_update(score)
            self.hand_objs[0].hand_high_update(score)
            if score == 0:
                self.hand_objs[0].hand_zero()
            if score > 0:
                self.peg_brd_update(self.peg_flags[0])
            self.lsc.score_flag = -1
        if self.lsc.score_flag == 1:
            score = sum(self.score_order[1][:4])
            self.hand_objs[1].score_update(score)
            self.hand_objs[1].hand_high_update(score)
            if score > 0:
                self.peg_brd_update(self.peg_flags[1])
            if score == 0:
                self.hand_objs[1].hand_zero()
            self.lsc.score_flag = -1
        if self.lsc.score_flag == 2:
            score = sum(self.score_order[2][:4])
            self.hand_objs[2].score_update(score)
            self.hand_objs[2].box_high_update(score)
            if score > 0:
                self.peg_brd_update(self.peg_flags[2])
            self.lsc.score_flag = -1
            if score == 0:
                self.hand_objs[2].box_zero()
        if self.lsc.score_flag == 3:
            self.lay_initial()
            if self.d_flag:
                self.d_flag = 0
            else:
                self.d_flag = 1
            if self.p_hnd_obj.score > 120 or self.c_hnd_obj.score > 120:
                self.timer.singleShot(800, self.game_over)
            else:
                self.timer.singleShot(1500, self.deal_hands)
        else:
            self.timer.singleShot(60, self.score_update_loop)

    def peg_brd_update(self, flag):
        if flag:
            self.peg_brd.play_move_peg_icon(self.p_hnd_obj.score)
        else:
            self.peg_brd.comp_move_peg_icon(self.c_hnd_obj.score)

    def game_reset(self):
        reply = QMessageBox.question(None, "Reset Game ?", "Nothing will be written to database")
        if reply == QMessageBox.Yes:
            self.win_opac = 1
            self.timer.singleShot(200, self.fade_to_close)
            self.flag_reset = 0
        else:
            return

    def fade_to_close(self):
        self.win_opac -= 0.1
        if self.win_opac > 0:
            self.main_gui.setWindowOpacity(self.win_opac)
            self.timer.singleShot(100, self.fade_to_close)
        else:
            self.main_gui.close()
            self.set_ui()

    def game_over(self, reset_flag=0):
        for img in self.main_gui.obj_lay_refs:
            img.close()
        self.game_cut_img.close()
        self.deck_bk_img.close()
        self.main_gui.crib_imgs[0].close()
        self.lt_tot_lbl.close()
        self.lb_lay.close()
        self.main_gui.lay_x_offset = 0
        self.peg_brd.peg_reset()
        if self.main_gui.p_img_obj_ref:
            for img in self.main_gui.p_img_obj_ref:
                img.close()
        if self.main_gui.c_img_obj_ref:
            for img in self.main_gui.c_img_obj_ref:
                img.close()
        if not reset_flag:
            if self.p_hnd_obj.score > self.c_hnd_obj.score:
                self.main_gui.game_over_animinations(self.p_hnd_obj.score, self.c_hnd_obj.score)
                self.p_hnd_obj.win_game()
                self.game_stats.game_summary(self.p_hnd_obj, self.c_hnd_obj)
            else:
                self.main_gui.game_over_animinations(self.p_hnd_obj.score, self.c_hnd_obj.score)
                self.c_hnd_obj.win_game()
                self.game_stats.game_summary(self.p_hnd_obj, self.c_hnd_obj)
        self.main_gui.set_menu_btns()
        self.db_initial_update()
        self.btn_define_connect()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ctl = MainCtl()
    ctl.set_ui()
    sys.exit(app.exec_())
