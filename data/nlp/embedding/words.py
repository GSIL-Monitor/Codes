# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil

from gensim.models import Word2Vec


w2v_loop_size = 30


class WordExtender(object):

    def __init__(self, num=1, word_similarity_threshold=0.4):

        self.db = dbcon.connect_torndb()
        self.w2v = Word2Vec.load(
            os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/online.binary.w2vmodel'))
        self.extend_count = num
        self.word_similarity_threshold = word_similarity_threshold

    def extend4tag(self, *tags):

        try:
            results = list(self.__extend_tag(tags))
            return results[0] if (results and len(results) == 1) else results
        except Exception, e:
            return []

    def __extend_tag(self, tags):

        global w2v_loop_size
        start, stop = 0, False
        num = self.extend_count
        while not stop:
            for item in self.w2v.most_similar(positive=tags, topn=start+w2v_loop_size)[start:]:
                if item[1] < self.word_similarity_threshold or num <= 0:
                    stop = True
                    break
                if dbutil.exist_tag(self.db, item[0]):
                    num -= 1
                    yield item[0]

            start += w2v_loop_size


if __name__ == '__main__':

    we = WordExtender(20)
    # db = dbcon.connect_torndb()
    # for item in db.query('select sectorName from sector where level=1;'):
    #     print item.sectorName, ';'.join(we.extend4tag(item.sectorName))
    print ';'.join(we.extend4tag(u'汽车'))
    # print ';'.join(we.extend4tag(u'电子商务'))
    # print ';'.join(we.extend4tag(u'医疗'))
