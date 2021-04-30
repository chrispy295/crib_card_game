import random
import numpy as np


def define_deck():
    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['D', 'C', 'H', 'S']
    deck = [card+suit for suit in suits for card in cards]
    random.shuffle(deck)
    return deck


def lay_permit(hand, lay_total):
    lay_allow = []
    for card in hand:
        face_val = face_convert(card)
        if face_val + lay_total <= 31:
            lay_allow.append(card)
    return lay_allow


def dealer_select(play_cut, comp_cut):
    comp_pip = pip_convert(comp_cut)
    play_pip = pip_convert(play_cut)
    if comp_pip > play_pip:
        dealer_flag = 1
    elif comp_pip < play_pip:
        dealer_flag = 0
    else:
        dealer_flag = 2
    return dealer_flag


def deal_hands(deck):
    c_hand = deck[:6]
    del deck[:6]
    p_hand = deck[:6]
    del deck[:6]
    return p_hand, c_hand


def pip_convert(hand):
    str_flag = 0
    if isinstance(hand, str):        # takes care of single str instance
        hand = [hand]
        str_flag = 1
    val_dict = {'J': 11, 'Q': 12, 'K': 13, 'A': 1}
    suit_remove = [x[:-1] for x in hand]
    pips = [val_dict[val] if val in val_dict else int(val) for val in suit_remove]
    if str_flag:
        pips = pips[0]
    return pips


def face_convert(hand):
    str_flag = 0
    if isinstance(hand, str):        # takes care of single str instance
        hand = [hand]
        str_flag = 1
    val_dict = {'J': 10, 'Q': 10, 'K': 10, 'A': 1}
    suit_remove = [x[:-1] for x in hand]
    faces = [val_dict[val] if val in val_dict else int(val) for val in suit_remove]
    if str_flag:
        faces = faces[0]
    return faces


def hand_sort(hand):
    y = pip_convert(hand)
    hand = [x for _, x in sorted(zip(y, hand))]
    return hand


def hand_length2_score(hand):
    """ Used to calculate a score for a 2 card hand
        Only used in computer hand calculate"""
    score = 0
    rank = pip_convert(hand)
    faces = face_convert(hand)
    if rank[0] == rank[1]:
        score += 2
    if sum(faces) == 15:
        score += 2
    return score


def lay_score_calc(lay_pips, lay_faces):
    score_15 = 0
    score_31 = 0
    score_pair = 0
    score_run = 0
    run = []
    if sum(lay_faces) == 15:
        score_15 += 2
    if sum(lay_faces) == 31:
        score_31 += 2
    if len(lay_pips) >= 3:
        for x in range(-3, -(len(lay_pips))-1, -1):
            diff = list(np.diff(sorted(lay_pips[x:])))
            same = set(diff)
            if len(same) == 1 and 1 in same:
                run.append(abs(x))
            else:
                run.append(0)
        score_run = max(run)
    p = list(np.diff(lay_pips))
    count = 0
    for y in range(-1, -(len(p) + 1), -1):
        if p[y] == 0:
            count += 1
        else:
            break
    if count == 1:
        score_pair += 2
    elif count == 2:
        score_pair += 6
    elif count == 3:
        score_pair += 12
    return score_15, score_pair, score_run, score_31


def peg_board_outline():
    arr_y = np.linspace(start=0, stop=7, num=30)
    s_wav = np.sin(arr_y)
    line_cords1 = [(72, 40)]
    line_cords4 = []
    for x in range(len(arr_y)):
        line_cords1.append((int((s_wav[x] * 70) + 82), int((arr_y[x] * 90) + 50)))
        line_cords4.append((int((s_wav[x] * 70) + 237), int((arr_y[x] * 90) + 50)))
    polygon2 = line_cords1 + [(137, 700), (295, 700)] + line_cords4[::-1] + [(230, 40)]
    return polygon2


def peg_board_score_ref():
    p_peg_ref_1 = [(235, 710)]
    p_peg_ref_2 = [(265, 710)]
    c_peg_ref_1 = [(150, 710)]  # lists that hold image cordinates to move the game peg scores to
    c_peg_ref_2 = [(180, 710)]
    arr_y = np.linspace(start=0, stop=7, num=30)
    s_wav = np.sin(arr_y)
    for x in range(len(arr_y) - 1, -1, -1):
        px_cord = int((s_wav[x] * 70) + 216)
        cx_cord = int((s_wav[x] * 70) + 95)
        y_cord = int((arr_y[x] * 90) + 50)
        p_peg_ref_1.append((px_cord, y_cord))
        p_peg_ref_2.append((px_cord, y_cord))
        c_peg_ref_1.append((cx_cord, y_cord))
        c_peg_ref_2.append((cx_cord, y_cord))
    for x in range(len(arr_y)):
        px_cord = int((s_wav[x] * 70) + 180)
        cx_cord = int((s_wav[x] * 70) + 135)
        y_cord = int((arr_y[x] * 90) + 50)
        p_peg_ref_1.append((px_cord, y_cord))
        p_peg_ref_2.append((px_cord, y_cord))
        c_peg_ref_1.append((cx_cord, y_cord))
        c_peg_ref_2.append((cx_cord, y_cord))
    return p_peg_ref_1, p_peg_ref_2, c_peg_ref_1, c_peg_ref_2


if __name__ == '__main__':
    pass




