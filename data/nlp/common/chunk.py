# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))


punc1 = [u'。']
punc2 = [u'，', u'、', u'；']


class SentenceChunker(object):

    def __init__(self, su=120, sl=4, pl=60):

        self.sentence_len_upper = su
        self.sentence_len_lower = sl
        self.paragrahp_len_lower = pl

    def chunk(self, *docs):

        global punc2
        for doc in docs:
            for paragraph in doc.split('\n'):
                if not paragraph.strip():
                    continue
                if len(paragraph) < self.paragrahp_len_lower:
                    yield paragraph
                    continue
                for sentence_l1 in paragraph.split(u'。'):
                    if len(sentence_l1) < self.sentence_len_lower:
                        continue
                    if len(sentence_l1) < self.sentence_len_upper:
                        yield sentence_l1
                    else:
                        for punc in punc2[1:]:
                            sentence_l1 = sentence_l1.replace(punc, punc2[0])
                        for sentence_l2 in sentence_l1.split(punc2[0]):
                            if len(sentence_l2) > self.sentence_len_lower:
                                yield sentence_l2