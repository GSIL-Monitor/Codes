# coding=utf-8
__author__ = 'victor'

import db as dbcon
from w2v import News, SourceCompany

import logging
import multiprocessing
from gensim.models import FastText

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

program = os.path.basename(__file__)
logger_tmp = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)


def try_embbeding_tag():

    global logger_tmp
    contents = list(SourceCompany(100))
    model = FastText(word_ngrams=2, size=400, window=3, min_count=20, workers=multiprocessing.cpu_count(), hs=1)
    model.build_vocab(contents)
    model.train(contents, total_examples=model.corpus_count, epochs=model.iter)
    model.save('models/gensim.tmp.model')
    print model[u'金融']


if __name__ == '__main__':

    try_embbeding_tag()
