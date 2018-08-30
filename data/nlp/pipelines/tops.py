# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
from collections import Counter

lowidf_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../keywords/thesaurus/source.1000.lowidf')


class Topper(object):

    def __init__(self):

        global lowidf_path
        self.lowidf = set(line.strip() for line in codecs.open(lowidf_path, encoding='utf-8'))

    def extract_top(self, words, topn=50, with_freq=False):

        counter = Counter(filter(lambda x: x not in self.lowidf, words)).most_common(topn)
        if with_freq:
            return counter
        return [x[0] for x in counter]