# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
import config as tsbconfig
from common import nlpconfig, dbutil
from common.dsutil import FixLenList
from common.zhtools.segment import Segmenter
from common.zhtools import stopword, word_filter
from score.completeness import ScorerCompleteness

import time
import datetime
import codecs
import fcntl
import json
import logging
import torndb
from random import randint
from itertools import chain
from abc import abstractmethod
from kafka import KafkaConsumer, KafkaClient, SimpleProducer
from gensim import corpora, models, similarities
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity

cach_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'cach')
stopwords = stopword.get_standard_stopwords()
simi_threshold = 0.25
complete_threshold = 0.25
description_len_threshold = 20
df_threshold_lower = 100
df_threshold_upper = 4000
num_topic = 100

# logging
logging.getLogger('rec').handlers = []
logger_nlp = logging.getLogger('rec')
logger_nlp.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_nlp.addHandler(stream_handler)


class Companies(object):

    def __init__(self):

        self.data_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../data/tsb/company/ltp_cut')
        self.segmenter = Segmenter()
        self.mapping_id2in = {}
        self.mapping_in2id = {}
        self.max_id = 0
        self.default_filter = word_filter.get_default_filter()

    def __iter__(self):

        global description_len_threshold, complete_threshold
        # db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        db = dbcon.connect_torndb()
        index = 0
        for result in iter(dbutil.get_all_company(db)):
            cid, desc = result.get('id'), result.get('context', '')
            score = dbutil.get_company_score(db, cid)
            if not (score and score > complete_threshold):
                continue
            if int(cid) > self.max_id:
                self.max_id = int(cid)
            if not os.path.exists(os.path.join(self.data_dir, str(cid))):
                words = list(self.segmenter.cut(desc))
            else:
                words = [line.split('\t')[0].strip()
                         for line in codecs.open(os.path.join(self.data_dir, str(cid)), encoding='utf-8')
                         if line.strip()]
            if not words:
                continue
            words = self.default_filter(words)
            if len(words) < description_len_threshold:
                continue

            self.mapping_id2in[cid] = index
            self.mapping_in2id[index] = cid
            index += 1
            yield [word.lower() for word in words]
        db.close()

    def get_mapping_id2in(self):
        return self.mapping_id2in

    def get_mapping_in2id(self):
        return self.mapping_in2id


class Companies_vec(Companies):

    def __init__(self, dictionary):

        Companies.__init__(self)
        self.dictionary = dictionary

    def __iter__(self):

        for doc in super(Companies_vec, self).__iter__():
            yield self.dictionary.doc2bow(doc)


if __name__ == '__main__':

    print __file__