from calc_utils import pip_convert, face_convert


class HandState:
    def __init__(self):
        self.score = 0
        self.hand_totals = 0
        self.box_totals = 0
        self.peg_total = 0
        self.hands_0 = 0
        self.box_0 = 0
        self.heels = []
        self.fifth = []
        self.pairs = []
        self.runs = []
        self.thirties = []
        self.nobs = []
        self.last = []
        self.hand_hi = 0
        self.box_hi = 0
        self.hand_num = 0
        self.first_crib = 0
        self.win = 0

    def add_hand(self, hand):
        self.hand_num += 1
        self.hand = hand
        self.hand_fin = self.hand[:]
        self.pips = pip_convert(hand)
        self.faces = face_convert(hand)

    def cut_card_add(self, card):
        self.hand_fin.append(card)

    def card_remove(self, card):
        idx = self.hand.index(card)
        self.hand.remove(card)
        self.pips.pop(idx)
        self.faces.pop(idx)

    def score_update(self, score):
        self.score += score

    def heel(self, val):                # all following func are for stats only
        self.heels.append(val)
        self.peg_total += val

    def lay_score_stats(self, scores):
        if scores[0]:
            self.fifth.append(2)
        if scores[1]:
            self.pairs.append(scores[1])
        if scores[2]:
            self.runs.append(scores[2])
        if scores[3]:
            self.thirties.append(2)
        self.peg_total += sum(scores)

    def last_crd(self, val):
        self.last.append(val)
        self.peg_total += val

    def hand_high_update(self, val):
        if val > self.hand_hi:
            self.hand_hi = val
        self.hand_totals += val

    def box_high_update(self, val):
        self.box_totals += val
        if val > self.box_hi:
            self.box_hi = val

    def hand_zero(self):
        self.hands_0 += 1

    def box_zero(self):
        self.box_0 += 1

    def crib_first(self):
        self.first_crib = 1

    def win_game(self):
        self.win = 1


class LayCards:
    def __init__(self):
        self.cards = []
        self.pips = []
        self.faces = []
        self.lay_total = 0

    def add_card(self, card):
        self.cards.append(card)
        pip = pip_convert(card)
        face = face_convert(card)
        self.pips.append(pip)
        self.faces.append(face)
        self.lay_total = sum(self.faces)

    def lay_allow(self, hnd, faces):
        lay_allow = [hnd[x] for x in range(len(hnd)) if faces[x] + self.lay_total <= 31]
        lay_indx = [x for x in range(len(hnd)) if faces[x] + self.lay_total <= 31]
        return lay_allow, lay_indx


if __name__ == '__main__':
    pass
