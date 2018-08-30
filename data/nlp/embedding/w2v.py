# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
from common.zhtools import word_filter
from common.zhtools.segment import Segmenter
from recommend.company import Companies

import datetime
import logging
import multiprocessing
from pymongo import DESCENDING
from gensim.models import Word2Vec


program = os.path.basename(__file__)
logger_w2v = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)


class Company_Sentences(Companies):

    def __iter__(self):
        for item in super(Company_Sentences, self).__iter__():
            yield ' '.join(item)


class SourceCompany(object):

    def __init__(self, size_limit=None):

        self.db = dbcon.connect_torndb()
        self.seg = Segmenter(tag=True)
        self.wfilter = word_filter.get_default_filter()
        self.size_limit = size_limit

    def __iter__(self):

        if not self.size_limit:
            sql2use = 'select * from source_company where active is null or active="Y";'
        else:
            sql2use = 'select * from source_company where active is null or active="Y" ' \
                      'order by rand() limit %s;' % self.size_limit
        for result in self.db.iter(sql2use):
            content = []
            if result.brief and result.brief.strip():
                content.extend(self.wfilter(self.seg.cut(result.brief)))
            if result.description and result.description.strip():
                content.extend(self.wfilter(self.seg.cut(result.description.strip())))
            if len(content) > 10:
                yield content


class News(object):

    def __init__(self):

        self.mongo = dbcon.connect_mongo()
        self.db = dbcon.connect_torndb()
        self.seg = Segmenter(tag=True)
        self.wfilter = word_filter.get_default_filter()

    def __iter__(self):

        for news in self.mongo.article.news.find({'processStatus': 1}).sort('_id', DESCENDING).limit(200000):
            try:
                content = []
                content.extend(self.wfilter(self.seg.cut4search(news.get('title', ''))))
                for piece in news.get('contents', []):
                    content.extend(self.wfilter(self.seg.cut(piece.get('content', ''))))
                if len(content) > 10:
                    yield content
            except Exception, e:
                continue
        for c in self.db.query('select description from company where verify="Y" and modifyTime>"2016-06-01";'):
            try:
                if len(c.description) > 10:
                    yield self.wfilter(self.seg.cut4search(c.description))
            except:
                continue


def train(outdir=None):

    global logger_w2v

    # dates = datetime.datetime.now().strftime('%Y%m%d')
    name = 's400w3min20_20170117'
    outdir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/') if not outdir else outdir
    bioutpath = os.path.join(outdir, '%s.binary.w2vmodel' % name)
    vecoutpath = os.path.join(outdir, '%s.vector.w2vmodel' % name)

    # contents = Companies()
    # contents = SourceCompany()
    contents = News()
    logger_w2v.info('Start to train model')
    model = Word2Vec(contents, size=400, window=3, min_count=20, workers=multiprocessing.cpu_count())
    model.save(bioutpath)
    model.save_word2vec_format(vecoutpath, binary=False)


if __name__ == '__main__':

    train()
