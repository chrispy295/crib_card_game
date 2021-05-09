import os
from PyQt5.QtCore import QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QPointF, QTimeLine
import playsound


class GameAnimations:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))

    def cut_card_animation(self, deck_objs):
        x_offset = 0
        self.animation_groups = QParallelAnimationGroup()
        for obj in deck_objs:
            self.anim = QPropertyAnimation(obj, b'pos')
            self.anim.setEasingCurve(QEasingCurve.InCubic)
            self.anim.setDuration(1200)
            self.anim.setStartValue(QPointF(5, 240))
            self.anim.setEndValue(QPointF(30 + x_offset, 240))
            self.animation_groups.addAnimation(self.anim)
            x_offset += 19
        self.animation_groups.start()

    def cut_card_anim_remove(self, deck_objs):
        self.animation_groups = QParallelAnimationGroup()
        for obj in deck_objs:
            anim = QPropertyAnimation(obj, b'pos')
            anim.setEasingCurve(QEasingCurve.InCubic)
            anim.setDuration(1000)
            anim.setEndValue(QPointF(1400, 240))
            self.animation_groups.addAnimation(anim)
        self.animation_groups.start()

    def deal_animation(self, hand_obj, x_start, y_start, end_y):
        self.play_anim_groups = QParallelAnimationGroup()
        x_os = 0
        for obj in hand_obj:
            anim = QPropertyAnimation(obj, b'pos')
            anim.setEasingCurve(QEasingCurve.InCubic)
            anim.setDuration(1500)
            anim.setStartValue(QPointF(x_start, y_start))
            anim.setEndValue(QPointF(140 + x_os, end_y))
            self.play_anim_groups.addAnimation(anim)
            x_os += 135
        self.play_anim_groups.start()

    def box_cards_animation(self, card_objs, end_x, end_y):
        self.crib_group_anim = QParallelAnimationGroup()
        for obj in card_objs:
            anim = QPropertyAnimation(obj, b'pos')
            anim.setDuration(1500)
            anim.setEasingCurve(QEasingCurve.InCubic)
            anim.setKeyValueAt(0.2, QPointF(450, 240.0))
            anim.setKeyValueAt(0.7, QPointF(20, 240.0))
            anim.setEndValue(QPointF(end_x, end_y))
            self.crib_group_anim.addAnimation(anim)
        self.crib_group_anim.start()

    def move_lay_card_anim(self, obj, x, y_os):
        self.anim = QPropertyAnimation(obj, b'pos')
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.setEndValue(QPointF(280 + x, 240 + y_os))
        self.anim.start()

    def set_game_cards_anims(self, p_obj, c_obj):
        self.card_set_anim = QParallelAnimationGroup()
        x_os = 0
        for obj in p_obj:
            anim = QPropertyAnimation(obj, b'pos')
            anim.setDuration(700)
            anim.setEndValue(QPointF(300+x_os, 450))
            self.card_set_anim.addAnimation(anim)
            x_os += 135
        x_os = 0
        for obj in c_obj:
            anim = QPropertyAnimation(obj, b'pos')
            anim.setDuration(700)
            anim.setEndValue(QPointF(300+x_os, 20))
            self.card_set_anim.addAnimation(anim)
            x_os += 135
        self.card_set_anim.start()

    def peg_counter_move(self, counter_obj, end_cords, step_points, score_digits, start_score, end_score):
        time_step = 1 / (len(step_points) + 1)
        self.anim = QPropertyAnimation(counter_obj, b'pos')
        self.anim.setDuration(1000)
        for point in step_points:
            self.anim.setKeyValueAt(time_step, QPointF(point[0], point[1]))
            time_step += 1 / (len(step_points) + 1)
        self.anim.setEndValue(end_cords)
        self.anim.start()
        self.time_line = QTimeLine(1000)
        self.time_line.setEasingCurve(QEasingCurve.InCubic)
        self.time_line.setFrameRange(start_score, end_score)
        self.time_line.frameChanged[int].connect(lambda: score_digits.setText("{}"
                                                                              .format(self.time_line.currentFrame())))
        self.time_line.currentFrame()
        self.time_line.start()

    def lay_score_animations(self, labels):
        self.lay_anim_group = QParallelAnimationGroup()
        y_os = 0
        for x in range(len(labels)):
            anim = QPropertyAnimation(labels[x], b'pos')
            anim.setDuration(1000)
            anim.setEndValue(QPointF(820, 260 + y_os))
            anim.setEasingCurve(QEasingCurve.InCubic)
            self.lay_anim_group.addAnimation(anim)
            y_os += 40
        self.lay_anim_group.start()

    def game_over_anim(self, lbls):
        self.anim_group = QParallelAnimationGroup()
        end_vals = [QPointF(390, 380), QPointF(570, 380), QPointF(360, 280)]
        for x in range(3):
            anim = QPropertyAnimation(lbls[x], b'pos')
            anim.setDuration(2400)
            anim.setEasingCurve(QEasingCurve.OutBounce)
            anim.setEndValue(end_vals[x])
            self.anim_group.addAnimation(anim)
        self.anim_group.start()
