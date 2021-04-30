import numpy as np
from itertools import combinations
from calc_utils import hand_length2_score, pip_convert
from lay_end_utils import score_master


def comp_hand_select(hand, box_flag):
    """Hand: list of strings of length 6 ['AH', '10D', ...etc]
       box_flag:  0 - computers's box
                  1 - player's box
       """
    b_com = []
    h_combo = list(combinations(hand, 4))
    for c in h_combo:
        bx = list(set(hand) - set(c))
        b_com.append(bx)
    h_pip = [pip_convert(x) for x in h_combo]
    b_pips = [pip_convert(x) for x in b_com]
    s_hnd = [sum(score_master(h_combo[x], score_only=1)) for x in range(len(h_combo))]
    s_box = [hand_length2_score(b_com[x]) for x in range(len(b_com))]
    s_hnd, h_combo, b_com, s_box, h_pip, b_pips = (list(t) for t in zip(*sorted(zip(s_hnd, h_combo, b_com, s_box,
                                                                                    h_pip, b_pips), reverse=True)))
    h_combo = [list(x) for x in h_combo]
    hnd_diffs = [abs(sum(np.diff(x))) for x in h_pip]
    box_diffs = [abs(x[0] - x[1]) for x in b_pips]
    score_max = s_hnd[0]
    last_idx_scor = len(s_hnd) - 1 - s_hnd[::-1].index(score_max)
    if sum(s_hnd) == 0:
        val = min(hnd_diffs[0:last_idx_scor])
        ind = hnd_diffs.index(val)
        return h_combo[ind], b_com[ind]
    elif s_hnd[0] - s_hnd[1] >= 2 and s_box[0] - s_box[1] == 0:
        return h_combo[0], b_com[0]
    elif not box_flag:                # computers box
        if last_idx_scor == 0:
            return h_combo[0], b_com[0]
        elif sum(s_box[0:last_idx_scor+1]) > 0 and sum(s_hnd[0:last_idx_scor+1]) > 0:
            idx = s_box.index(2)
            return h_combo[idx], b_com[idx]
        else:
            val = min(hnd_diffs[0:last_idx_scor+1])
            ind = hnd_diffs.index(val)
            return h_combo[ind], b_com[ind]
    else:
        if last_idx_scor == 0 and s_box[0] == 0:
            return h_combo[0], b_com[0]
        elif last_idx_scor == 0 and s_box[0] == 2 and s_hnd[0] - s_hnd[1] < 2:
            return h_combo[1], b_com[1]
        else:
            val = max(box_diffs[0:last_idx_scor + 1])
            ind = box_diffs.index(val)
            return h_combo[ind], b_com[ind]


if __name__ == '__main__':
    comp_hand = comp_hand_select(['AH', '2D', '3H', 'JD', '2H', '9C'], 1)
    print(comp_hand)
