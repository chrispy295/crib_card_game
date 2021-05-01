import random
from calc_utils import lay_score_calc, pip_convert, face_convert, define_deck


def lay_card_calc(l_pips, l_faces, hand):
    lt = sum(l_faces)       # lay cards sum total
    h_pips = pip_convert(hand)
    h_faces = face_convert(hand)
    if len(hand) == 1:
        card = hand[0]
        return card
    elif len(l_pips) == 0:
        list_4 = [fce for fce in h_faces if fce <= 4]
        pairs_4 = [fce for fce in list_4 if list_4.count(fce) >= 2]
        pairs_5_ex = [pip for pip in h_pips if pip != 5 and h_pips.count(pip) >= 2]
        list_6_10 = [fce for fce in h_faces if 5 < fce <= 9]
        pairs_6_10 = [fce for fce in h_faces if list_6_10.count(fce) >= 2]
        if pairs_4:
            val = pairs_4[0]
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif len(list_4) >= 2:
            val = random.choice(list_4)
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif pairs_6_10:
            val = pairs_6_10[0]
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif len(list_6_10) >= 2:
            val = random.choice(list_6_10)
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif list_4:
            val = list_4[0]
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif list_6_10:
            val = list_6_10[0]
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif pairs_5_ex:
            val = pairs_5_ex[0]
            idx = h_pips.index(val)
            card = hand[idx]
            return card
        else:
            card = random.choice(hand)
            return card
    else:
        list_safe = [fce for fce in h_faces if lt + fce != 5 and lt + fce != 10 and lt + fce != 21 and lt + fce != 26]
        list_safe_pairs = [fce for fce in list_safe if list_safe.count(fce) >= 2 and lt + (3 * fce) <= 31]
        list_safe_5 = [fce for fce in h_faces if lt + fce != 10 and lt + fce != 21 and lt + fce != 26 and fce <= 5]
        score_list = []
        for x in range(len(hand)):
            l_pips.append(h_pips[x])
            l_faces.append(h_faces[x])
            scores = lay_score_calc(l_pips, l_faces)
            score_list.append(scores)
            l_pips.pop(-1)
            l_faces.pop(-1)
        scores_sum_tots_per_card = [sum(x) for x in score_list]
        card_passive = card_select_brute(l_pips, l_faces, hand, h_pips, h_faces)
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
        elif list_safe_pairs:
            val = list_safe_pairs[0]
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif card_passive:
            return card_passive
        elif lt < 10 and len(list_safe_5) >= 2:
            val = random.choice(list_safe_5)
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        elif lt >= 10:
            val = max(list_safe)
            idx = h_faces.index(val)
            card = hand[idx]
            return card
        else:
            card = random.choice(hand)
            return card


def card_select_brute(l_pips, l_faces, hand, h_pips, h_faces):
    lt = sum(l_faces)
    scores = []
    scores_faces = []
    card_pips = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    card_faces = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    for x in range(len(h_pips)):
        sub_totals = []
        scores_faces.append(h_faces[x])
        for y in range(len(card_pips)):
            composite_pips = [l_pips[-1], h_pips[x], card_pips[y]]
            composite_faces = [l_faces[-1], h_faces[x], card_faces[y]]
            if sum(composite_faces) > 31 or h_faces[x] + lt == 10 and h_faces[x] + lt == 21:
                continue
            else:
                score = sum(lay_score_calc(composite_pips, composite_faces))
                sub_totals.append(score)
        scores.append(sum(sub_totals))
    if scores:
        low_val = min(scores)
        idx = scores.index(low_val)
        card = hand[idx]
        return card
    else:
        return None


if __name__ == '__main__':
    count = 0
    while count < 50:
        dek = define_deck()
        hnd = dek[:3]
        lp = [4, 10]
        lf = [4, 10]
        crd = lay_card_calc(lp, lf, hnd)
        print('choice ', crd)
        print('========================')
        count += 1
