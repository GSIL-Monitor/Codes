# coding=utf-8
__author__ = 'victor'

import logging
from copy import deepcopy
from datetime import datetime

import numpy as np
from pymongo import DESCENDING
from gensim.models import Word2Vec
from sklearn.externals import joblib
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../search'))

import db as dbcon
from common import dbutil
from common.feed import Feeder, NewsFeeder


word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                              '../embedding/models/s400w3min20_yitai.binary.w2vmodel')


# logging
logging.getLogger('batch').handlers = []
logger_batch = logging.getLogger('batch')
logger_batch.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_batch.addHandler(stream_handler)


class BatchTagger(object):

    def __init__(self):

        global word2vec_model
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.feeder = Feeder()
        self.nfeeder = NewsFeeder()
        self.w2v = Word2Vec.load(word2vec_model)

        self.auto_f1_threshold = 0.8

    def train(self):

        global logger_batch
        date_mark = datetime.now().strftime('%Y%m%d')
        current_dir = os.path.split(os.path.realpath(__file__))[0]
        clf = self.valid(175747)
        joblib.dump(clf, os.path.join(current_dir, 'models/%s.%s.model' % (175747, date_mark)))
        # for tid in dbutil.get_verified_tags(self.db):
        #     if dbutil.get_tag_info(self.db, tid, 'type') < 11011:
        #         continue
        #     logger_batch.info('Processing %s', tid)
        #     clf = self.valid(tid)
        #     if clf:
        #         joblib.dump(clf, os.path.join(current_dir, 'models/%s.%s.model' % (tid, date_mark)))

    def test(self):

        clf = joblib.load('models/175747.20180311.model')
        truth_cids = [t[0] for t in dbutil.get_company_from_tag(self.db, 175747, True) if t[1] == 'Y']
        standard = [list(self.feeder.feed_seged(cid)) for cid in truth_cids]
        standard = [[self.w2v[w] for w in t if w in self.w2v] for t in standard if t]
        standard = [np.mean(t, axis=0) for t in standard if t]
        predict = clf.predict_proba(standard)
        for i in range(len(truth_cids)):
            if predict[i][0] > 1 - self.auto_f1_threshold:
                print dbutil.get_company_name(self.db, truth_cids[i]), predict[i][0]
        # for p1, p2 in clf.predict_proba(standard)[:20]:
        #     print p1, p2

    def valid(self, tid):

        global logger_batch
        # prepare gold standard
        truth_cids = [t[0] for t in dbutil.get_company_from_tag(self.db, tid, True) if t[1] == 'Y']
        standard = [list(self.feeder.feed_seged(cid)) for cid in truth_cids]
        standard = [[self.w2v[w] for w in t if w in self.w2v] for t in standard if t]
        standard = [np.mean(t, axis=0) for t in standard if t]
        standard_labels = [1 for _ in xrange(len(standard))]
        # false_cids = dbutil.random_company_ids(self.db, truth_cids, 200)
        false_cids = [rel.cid for rel in self.db.query('select companyId cid from company_tag_rel '
                                                       'where companyId not in %s and (active="Y" or active is null) '
                                                       'and verify="Y" and createTime>"2017-10-01" '
                                                       'and tagid=65 order by rand() '
                                                       'limit %s;', truth_cids, 1000)]
        sample_false = [list(self.feeder.feed_seged(cid)) for cid in false_cids]
        sample_false = [[self.w2v[w] for w in t if w in self.w2v] for t in sample_false if t]
        sample_false = [np.mean(t, axis=0) for t in sample_false if t]
        standard.extend(sample_false)
        standard_labels.extend([0 for _ in xrange(len(sample_false))])

        # prepare news
        train_news, labels_news = [], []
        for news in self.mongo.article.news.find({"features": tid, "processStatus": 1}).limit(3000):
            if len(news.get('sectors')) > 3:
                continue
            news = self.nfeeder.feed(news)
            if not news:
                continue
            train_news.append(np.mean([self.w2v[w] for w in news if w in self.w2v], axis=0))
            labels_news.append(1)
        if labels_news:
            for news in self.mongo.article.news.find({"features": {'$ne': tid, '$in': [65]},
                                                      "processStatus": 1}).\
                    sort('_id', DESCENDING).limit(min(2000, len(labels_news) * 3)):
                news = self.nfeeder.feed(news)
                if not news:
                    continue
                train_news.append(np.mean([self.w2v[w] for w in news if w in self.w2v], axis=0))
                labels_news.append(0)
        trainX, trainY = deepcopy(train_news), deepcopy(labels_news)
        trainX.extend(standard)
        trainY.extend(standard_labels)

        clfsvm = SVC(probability=True)
        scores = cross_validate(clfsvm, trainX, trainY, cv=5, scoring='f1')
        logger_batch.info('Cross validation score for %s, %s. Total sample %s',
                          tid, np.mean(scores.get('test_score')), len(trainY))
        if np.mean(scores.get('test_score')) > self.auto_f1_threshold:
            return self.__fit_param(standard, standard_labels, train_news, labels_news)
        else:
            return False
        # clf.fit(train_news, labels)
        # y_pred = clf.predict(test)
        # y_prob = clf.predict_proba(test)
        # y_prob = [prob[1] for prob in y_prob]
        # print clf.score(test, y_true)
        # print f1_score(y_true, y_pred)
        # print roc_auc_score(y_true, y_prob)

    def __fit_param(self, validationX, validationY, trainX, trainY):

        validationX.extend(trainX)
        validationY.extend(trainY)
        clf = SVC(probability=True)
        clf.fit(validationX, validationY)
        return clf


if __name__ == '__main__':

    bt = BatchTagger()
    # bt.train()
    bt.test()
