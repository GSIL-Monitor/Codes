# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import re


def edit_distance(s1, s2, weights=(1, 1, 2)):

    a, d, m = weights  # weight of add, delete, modify
    len1, len2 = len(s1), len(s2)
    status = [[0 for _ in xrange(len2+1)] for _ in xrange(len1+1)]
    for i in xrange(len1+1):
        status[i][0] = i*d
    for j in xrange(len2+1):
        status[0][j] = j*a
    for i in xrange(1, len1+1):
        for j in xrange(1, len2+1):
            status[i][j] = status[i-1][j-1] if s1[i-1] == s2[j-1] \
                else min(status[i-1][j]+d, status[i][j-1]+a, status[i-1][j-1]+m)
    return status[- 1][- 1]


def all_chinese(s):

    for c in s.decode('utf-8'):
        if c < u"\u4e00" or c > u"\u9fa6":
            return False
    return True


def infix2prefix(seq, prior_opt=[u'+', u'-'], post_opt=[u',']):

    operators, result = list(), list()
    legal_operators = set(prior_opt) | set(post_opt) | {u'(', u')'}
    productive_operators = set(prior_opt) | set(post_opt)
    # 字符串拆分成seq
    if isinstance(seq, str) or isinstance(seq, unicode):
        seq = [t.strip() for t in re.split('(%s)' % ('|'.join(['\%s' % c for c in legal_operators])), seq) if t.strip()]
    for c in seq:
        if c not in legal_operators:
            result.append(c)
        elif c in productive_operators:
            let_go = False
            while not let_go:
                if len(operators) == 0 or operators[-1] == u'(':
                    operators.append(c)
                    let_go = True
                elif c in prior_opt and operators[-1] in post_opt:
                    operators.append(c)
                    let_go = True
                else:
                    result.append(operators.pop(-1))
        else:
            if c == '(':
                operators.append(c)
            else:
                while True:
                    out = operators.pop(-1)
                    if out == '(':
                        break
                    else:
                        result.append(out)
    operators.reverse()
    result.extend(operators)
    return result


if __name__ == '__main__':

    print __file__

    # a = u'景驰科技天使轮融资3000万美元'
    # b = u'景驰科技天使轮融资3000万美元 将从硅谷搬回中国'
    # print edit_distance(a, b, (1, 1, 3))
    # print len(set(a) | set(b))

    query = u'(人工智能,机器学习)+(金融,理财)-保险'
    print infix2prefix(query)
    print infix2prefix(u'((a,b), (c, d), (e,f))+g')
    print infix2prefix(u'(a,b,c,d)')
    print infix2prefix(u'(a,b)+c-d')