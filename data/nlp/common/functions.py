# -*- coding: utf-8 -*-
__author__ = 'victor'

from numpy import irr


def is_engish_word(w):

    return all(ord(c) < 128 for c in w)


def true_ratio(deposit, months, rate, downpay=0, cutoff=None):

    deposit = deposit * 10000
    rate = rate/1200
    monthly = round(deposit * rate * (1+rate)**months / ((1+rate)**months-1), 2)

    series = [downpay*10000-deposit]
    series.extend([monthly for _ in xrange(months)])
    true_irr = round(irr(series)*12*100, 2)

    cutoff = months if not cutoff else cutoff
    remain = deposit * (1+rate)**cutoff - monthly * ((1+rate)**cutoff - 1) / rate
    series = [downpay * 10000 - deposit]
    series.extend([monthly for _ in xrange(cutoff-1)])
    series.append(remain+monthly)
    cutoff_irr = round(irr(series)*12*100, 2)

    return monthly, true_irr, cutoff_irr


if __name__ == '__main__':

    print true_ratio(300, 240, 6.37, 3, 60)
    # print is_engish_word(u'Fintech金融科技')
