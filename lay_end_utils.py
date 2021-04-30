import os
from itertools import combinations
import numpy as np
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPixmap
from calc_utils import pip_convert, face_convert
from game_play_labels import main_labels as mwl


def score_master(hand, b_flag=0, score_only=0):       # score only flag set to 1 for summed scores only
    hand_2 = list(combinations(hand, 2))
    hand_3 = list(combinations(hand, 3))
    hand_4 = list(combinations(hand, 4))
    hand_5 = list(combinations(hand, 5))     # used when choosing intial comp hand
    hand_3_pips = [pip_convert(h) for h in hand_3]
    hand_4_pips = [pip_convert(h) for h in hand_4]
    hand_5_pips = [pip_convert(h) for h in hand_5]
    hand_2_faces = [face_convert(h) for h in hand_2]
    hand_3_faces = [face_convert(h) for h in hand_3]
    hand_4_faces = [face_convert(h) for h in hand_4]
    hand_5_faces = [face_convert(h) for h in hand_5]
    nob_score = []
    nob_cards = []
    hnd_master = hand_2 + hand_3 + hand_4 + hand_5
    faces_master = hand_2_faces + hand_3_faces + hand_4_faces + hand_5_faces
    hnd_runs_master = hand_3 + hand_4 + hand_5
    pips_runs = hand_3_pips + hand_4_pips + hand_5_pips
    pair_hands, pair_scores = pairs_score(hand)
    combos_15, score_15 = score_15_31(hnd_master, faces_master)
    combo_runs, combo_runs_scores = runs_calc(hnd_runs_master, pips_runs)
    flush_hand, flush_score = flush_calc(hand, b_flag)
    if len(hand) == 5:
        ref_suit = hand[-1][-1]
        for card in hand[:4]:
            if card[-1] == ref_suit and card[:-1] == 'J':
                nob_score.append(1)
                nob_cards.append((card, hand[-1]))
    if score_only:
        return sum(score_15), sum(pair_scores), sum(combo_runs_scores), sum(flush_score), sum(nob_score)
    else:
        return (score_15, pair_scores, combo_runs_scores, flush_score, nob_score), (combos_15, pair_hands, combo_runs,
                                                                                    flush_hand, nob_cards)


def pairs_score(hand):
    pair_values = {1: 0, 2: 2, 3: 6, 4: 12}
    pips = pip_convert(hand)
    pips, hand = (list(t) for t in zip(*sorted(zip(pips, hand))))
    set_pips = sorted(list(set(pips)))
    pair_scores = [pair_values[pips.count(x)] for x in set_pips if pips.count(x) >= 2]
    indxs = [x if pips.count(x) >= 2 else 0 for x in pips]
    pair_cards = [hand[x] for x in range(len(pips)) if indxs[x]]
    if not pair_scores:
        return [], []
    elif len(pair_scores) == 1:
        return [pair_cards], pair_scores
    else:
        if pair_scores[0] == 2:
            idx = 2
        else:
            idx = 3
        return [pair_cards[:idx], pair_cards[idx:]],  pair_scores


def runs_calc(hnd_combos, pips_combos):
    runs_combos = []
    run_scores = []
    idx = 0
    for x in range(len(pips_combos)):
        diffs = list(np.diff(sorted(pips_combos[x])))
        if len(diffs) == diffs.count(1):
            runs_combos.append(hnd_combos[x])
            run_scores.append(len(hnd_combos[x]))
    if run_scores:
        val_max = max(run_scores)
        idx = run_scores.index(val_max)
    return runs_combos[idx:], run_scores[idx:]


def score_15_31(hnd_combos, faces_combos):
    h_combos_15 = []
    score_combos_15 = []
    for x in range(len(faces_combos)):
        if not faces_combos[x]:
            continue
        if sum(faces_combos[x]) == 15:
            h_combos_15.append(hnd_combos[x])
            score_combos_15.append(2)
    return h_combos_15, score_combos_15


def flush_calc(hand, b_flag):
    """Calculates flushes for length of hand 4 or 5.
       Box flushes only score for a full flush of 5"""
    suits_4 = [x[-1] for x in hand[:-1]]
    suits_5 = [x[-1] for x in hand]
    flush_score_4 = [suits_4.count(x) if suits_4.count(x) == 4 else 0 for x in set(suits_4)]
    flush_score_5 = [suits_5.count(x) if suits_5.count(x) == 5 else 0 for x in set(suits_4)]
    if b_flag and 5 in flush_score_5:
        return [hand], [5]
    elif b_flag and 5 not in flush_score_5:
        return [], []
    elif 5 in flush_score_5:
        return [hand], [5]
    elif 4 in flush_score_4:
        return [hand[:4]], [4]
    else:
        return [], []


if __name__ == '__main__':
    pass
