# coding=utf-8
__author__ = 'victor'

import codecs
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re


def __load_hants_dict():

    hants, hanst = {}, {}
    dir = os.path.dirname(os.path.realpath(__file__))
    for line in codecs.open(os.path.join(dir, u'简繁体字典'), encoding='utf-8'):
        hants[ord(unicode(line.split('\t')[1].strip()))] = line.split('\t')[0].strip()
        hanst[ord(unicode(line.split('\t')[0].strip()))] = line.split('\t')[1].strip()

    return hants, hanst

hants, hanst = __load_hants_dict()


def translate(s, direction='t2s'):

    global hants, hanst
    if not isinstance(s, unicode):
        return s
    return s.translate(hants) if direction == 't2s' else s.translate(hanst)


def all_eng(u):

    """
    determin where an unicode string is all english
    """
    return len(re.findall(r'[a-zA-Z]', u)) == len(u)


if __name__ == '__main__':
    print translate(unicode(u'我們是台灣人'))
    print translate(u'我們是台灣人')