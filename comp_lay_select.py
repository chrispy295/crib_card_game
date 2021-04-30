import random
import numpy as np
from calc_utils import lay_score_calc, pip_convert, face_convert


def lay_card_calc(l_pips, l_faces, hand):
    lay_tot = sum(l_faces)
    h_pips = pip_convert(hand)
    h_faces = face_convert(hand)
    if len(hand) == 1:
        card = hand[0]
        return card
    elif lay_tot == 0:              # 1 st lay
        pair_5_less = [hand[x] for x in range(len(hand)) if h_pips.count(h_pips[x]) > 1 and h_faces[x] < 5]
        pairs_all_not_5 = [hand[x] for x in range(len(hand)) if h_pips.count(h_pips[x]) > 1 and h_pips[x] != 5]
        no_5_pips = [x for x in h_pips if x != 5 and x < 10]
        diffs_no_5 = list(np.diff(no_5_pips))
        face_5_10_safe = [fce for fce in h_faces if fce != 5 and fce != 10]
        faces_5_10_only = [fce for fce in h_faces if fce == 5 or fce == 10]
        if pair_5_less:
            card = pair_5_less[0]
            return card
        elif 1 in diffs_no_5:
            diff_indx = diffs_no_5.index(1)
            val = no_5_pips[diff_indx]
            idx = h_pips.index(val)
            card = hand[idx]
            return card
        elif 2 in diffs_no_5:
            diff_indx = diffs_no_5.index(2)
            val = no_5_pips[diff_indx]
            idx = h_pips.index(val)
            card = hand[idx]
            return card
        elif face_5_10_safe:
            val = min(face_5_10_safe)
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif pairs_all_not_5:
            card = pairs_all_not_5[0]
            return card
        elif sum(h_faces) == len(hand) * 10:
            pairs_ten = [hand[x] for x in range(len(hand)) if h_pips.count(h_pips[x]) > 1]
            if pairs_ten:
                card = pairs_ten[0]
                return card
            else:
                card = random.choice(hand)
                return card
        elif len(faces_5_10_only) == len(hand):
            val = max(faces_5_10_only)
            idx = h_faces.index(val)
            card = hand[idx]
            return card
    else:
        sum_idx0_idx1 = 0
        sum_idx1_idx2 = 0
        sum_idx1_idx3 = 0
        runs_test_1 = 0
        runs_test_2 = 0
        pairs_max_31 = [hand[x] for x in range(len(hand)) if h_pips.count(h_pips[x]) > 1 and
                        (h_faces[x]*2) + lay_tot <= 31]
        pairs_max_31_safe = [hand[x] for x in range(len(hand)) if h_pips.count(h_pips[x]) > 1 and
                             (h_faces[x] * 2) + lay_tot <= 31 and h_faces[x] + lay_tot != 21 and
                             h_faces[x] + lay_tot != 5 and h_faces[x] + lay_tot != 10]
        twenty_21_safe_pips = [h_pips[x] for x in range(len(hand)) if lay_tot + h_faces[x] != 21]
        diffs_21 = list(np.diff(twenty_21_safe_pips))
        ten_safe_lay2 = [h_faces[x] for x in range(len(hand)) if lay_tot + h_faces[x] != 10]
        twenty_1_safe_lay2 = [h_faces[x] for x in range(len(hand)) if lay_tot + h_faces[x] != 21]
        if 1 in diffs_21:
            pip_diff_indx = diffs_21.index(1)
            pip_val = twenty_21_safe_pips[pip_diff_indx]  # should really use face value
            if lay_tot + (3*pip_val) + 1 <= 31:
                runs_test_1 = 1
        if 2 in diffs_21:
            pip_diff_indx = diffs_21.index(2)
            pip_val = twenty_21_safe_pips[pip_diff_indx]  # should really use face value
            if lay_tot + (3*pip_val) + 2 <= 31:
                runs_test_2 = 1
        if len(hand) == 3:
            sum_idx0_idx1 = h_faces[0] + h_faces[1]
            sum_idx1_idx2 = h_faces[1] + h_faces[2]
            sum_idx1_idx3 = h_faces[0] + h_faces[2]
        if len(hand) == 2:
            sum_idx0_idx1 = sum(h_faces)
        score_list = []
        for x in range(len(hand)):
            l_pips.append(h_pips[x])
            l_faces.append(h_faces[x])
            scores = lay_score_calc(l_pips, l_faces)
            score_list.append(scores)
            l_pips.pop(-1)
            l_faces.pop(-1)
        scores_sum_tots_per_card = [sum(x) for x in score_list]
        if sum(scores_sum_tots_per_card) > 0:
            val = max(scores_sum_tots_per_card)
            if val > 2:
                idx = scores_sum_tots_per_card.index(val)
                card = hand[idx]
                return card
            else:
                fifth_31_score_ind = [x for x in range(len(score_list)) if score_list[x][0] > 1 or score_list[x][3] > 1]
                if fifth_31_score_ind:
                    idx = fifth_31_score_ind[0]
                    card = hand[idx]
                    return card
                else:
                    idx = scores_sum_tots_per_card.index(val)
                    card = hand[idx]
                    return card
        elif lay_tot >= 20:
            if sum_idx0_idx1 + lay_tot == 31:
                card = hand[1]
                return card
            elif sum_idx1_idx2 + lay_tot == 31:
                card = hand[2]
                return card
            elif sum_idx1_idx3 + lay_tot == 31:
                card = hand[2]
                return card
            elif pairs_max_31:
                card = pairs_max_31[0]
                return card
            else:
                val = max(h_faces)
                idx = h_faces.index(val)
                card = hand[idx]
                return card
        elif pairs_max_31_safe:
            card = pairs_max_31_safe[0]
            return card
        elif twenty_21_safe_pips:
            if runs_test_1:
                pip_diff_indx = diffs_21.index(1)
                pip_val = twenty_21_safe_pips[pip_diff_indx]
                indx = h_pips.index(pip_val)
                card = hand[indx]
                return card
            elif runs_test_2:
                pip_diff_indx = diffs_21.index(2)
                pip_val = twenty_21_safe_pips[pip_diff_indx]
                indx = h_pips.index(pip_val)
                card = hand[indx]
                return card
            elif lay_tot < 10 and ten_safe_lay2:
                val = max(ten_safe_lay2)
                idx = h_faces.index(val)
                card = hand[idx]
                return card
            elif 10 <= lay_tot <= 19 and twenty_1_safe_lay2:
                val = max(twenty_1_safe_lay2)
                idx = h_faces.index(val)
                card = hand[idx]
                return card
            else:
                val = max(h_faces)
                idx = h_faces.index(val)
                card = hand[idx]
                return card
        else:
            val = max(h_faces)
            idx = h_faces.index(val)
            card = hand[idx]
            return card


if __name__ == '__main__':
    pass
