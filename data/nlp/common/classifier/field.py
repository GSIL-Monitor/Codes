# coding=utf-8
__author__ = 'victor'

import sys
reload(sys)
sys.path.append('..')
sys.setdefaultencoding('utf-8')

import os
import codecs
import json
import random
import multiprocessing
import logging
import torndb
import numpy as np
from math import ceil
from common import nlpconfig, dbutil
from common.zhtools.segment import Segmenter
from keywords.corpus import words_filtering
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import cross_validation
from gensim import models, corpora


# logging
logging.getLogger('classifier').handlers = []
logger_nlp = logging.getLogger('classifier')
logger_nlp.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_nlp.addHandler(stream_handler)


doc_len_threshold = 20


class FieldClassifier(object):

    def __init__(self, model='randomforest'):

        self.segmenter = nlpconfig.get_segmenter()
        self.dirpath = os.path.split(os.path.realpath(__file__))[0]
        self.fields = [line.strip().split() for line in
                       codecs.open(os.path.join(self.dirpath, 'thesaurus/fields.1'), encoding='utf-8')]
        self.vectorizer, self.dictionary, self.feature_size = self.init_vectorizer()
        self.clf = self.init_model(model)

    def init_vectorizer(self, model_name='lsi'):

        model = models.LsiModel.load(os.path.join(self.dirpath, 'models/online.lsimodel'))
        dictionary = corpora.Dictionary.load(os.path.join(self.dirpath, 'models/online.dict'))
        return model, dictionary, model.num_topics

    def init_model(self, model_name):

        if model_name == 'randomforest':
            return RandomForestClassifier(n_estimators=50, class_weight='auto', n_jobs=multiprocessing.cpu_count())
        elif model_name == 'lr':
            return LogisticRegression()

    def vectorize(self, doc):

        global doc_len_threshold
        words = words_filtering(self.segmenter.cut(doc))
        if len(words) < doc_len_threshold:
            return None
        bow = self.dictionary.doc2bow(words, allow_update=True)
        return self.vectorizer[bow]

    def vectorize4cid(self, db, cid):

        # return self.vectorize(dbutil.get_company_desc(db, cid))

        sql = 'select companyDesc from company where companyId=%s;'
        return self.vectorize(db.get(sql, cid).companyDesc)

    def train(self, fpath=None, training=None):

        global logger_nlp
        if not fpath:
            fpath = os.path.join(self.dirpath, 'cach/fields.1.data')
        if not training:
            x, y = [], []
            db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
            logger_nlp.info('DB connected')
            for index, line in enumerate(codecs.open(fpath, encoding='utf-8')):
                try:
                    label, cid = line.strip().split('#')[0], int(line.strip().split('#')[1])
                    item = self.vectorize4cid(db, cid)
                    if item:
                        item = dict(item)
                        x.append(np.array(map(lambda x: self.normalize_float(x),
                                              [item.get(i, 0) for i in xrange(self.feature_size)])))
                        y.append(label.strip())
                except Exception, e:
                    logger_nlp.error('Loading error#Line: %s # %s' % (index, e))
        else:
            x, y = training['x'], training['y']
        logger_nlp.info('Training data prepared')
        print 'data', len(x), len(y)
        # self.record_weka(x, y)
        self.clf.fit(x, y)
        # print 'rf', cross_validation.cross_val_score(self.clf, x, y, cv=10)
        # from sklearn.linear_model import LogisticRegression
        # lr1 = LogisticRegression()
        # print 'lr', cross_validation.cross_val_score(lr1, x, y, cv=10)
        # lr2 = LogisticRegression(class_weight='auto')
        # print 'lr', cross_validation.cross_val_score(lr2, x, y, cv=10)

    def predict(self, doc):

        x = self.vectorize(doc)
        if not x:
            return self.naive_classify(doc), None
        a = self.naive_classify(self.segmenter.cut(doc))
        b = self.clf.predict([[i[1] for i in x]])[0]
        return a, b

    def normalize_float(self, f):

        if abs(f) < 0.001:
            return 0
        elif f > 0:
            return min(round(f, 5), 10)
        else:
            return max(round(f, 5), -10)

    def build_labeled_corpus(self):

        data_dir = os.path.join(self.dirpath, '../../data/tsb/company/ltp_cut')
        db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        if not os.path.exists(os.path.join(self.dirpath, 'cach')):
            os.makedirs(os.path.join(self.dirpath, 'cach'))
        categories = {}
        for result in dbutil.get_all_company(db):
            cid, content = result.companyId, result.companyDesc
            if os.path.exists(os.path.join(data_dir, str(cid))):
                content = [line.split('\t')[0] for line in
                           codecs.open(os.path.join(data_dir, str(cid)), encoding='utf-8') if line.strip()]
            else:
                content = list(self.segmenter.cut(content.strip()))

            if len(content) < 10:
                continue
            label = self.naive_classify(content)
            if label and label[1] > 1.02:
                categories.setdefault(label[0], []).append((cid, label[1]))
        with codecs.open(os.path.join(self.dirpath, 'cach/fields.1.data'), 'w', 'utf-8') as fcach:
            for category in categories.iteritems():
                label, items = category[0], sorted(category[1], key=lambda x: x[1], reverse=True)
                print label, len(items)
                for item in items:
                    fcach.write('%s#%s#%s\n' % (label, int(item[0]), str(item[1])))

    def naive_classify(self, content):

        content = list(content)
        votes = dict.fromkeys(xrange(len(self.fields)), 0)
        for word in content:
            for index, field_names in enumerate(self.fields):
                votes[index] += (word in field_names)
        votes = filter(lambda x: x[1] > 0, sorted(votes.iteritems(), key=lambda x: x[1], reverse=True))
        if len(votes) > 1 or len(votes) == 0:
            return False
        return tuple([self.fields[votes[0][0]][0], round(1+float(votes[0][1])/len(content), 4)])
        # if len(votes) == 1 or votes[0][1] / votes[1][1] > 2:
        #     return tuple([self.fields[votes[0][0]][0], round(1+float(votes[0][1])/len(content), 4)])
        # return False

    def record_weka(self, x, y):

        labels = set(y)
        labels = dict(zip(labels, xrange(len(labels))))
        with codecs.open('weka/field.1.train.arff', 'w', 'utf-8') as fo:
            fo.write('%% class: %s\n' % json.dumps(labels).decode('unicode_escape').encode('utf-8'))
            fo.write('@RELATION field \n\n')
            fo.write(''.join(['@ATTRIBUTE %s NUMERIC\n' % i for i in xrange(len(x[0]))]))
            fo.write('@ATTRIBUTE class {%s}\n' % ','.join(map(lambda x: str(x), labels.values())))
            fo.write('@DATA \n')
            for i in xrange(len(y)):
                fo.write('%s,%s\n' % (','.join([str(item) for item in x[i]]), labels.get(y[i])))


def weighted_choice(choices):

    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w


if __name__ == '__main__':

    print __file__

    # upsample('template/fields.data')
    # scatter_sample('weka/field.train.arff')
    fc = FieldClassifier()
    s = Segmenter()
    c = u'通过贴图让用户简单地画漫画，并用漫画沟通、社交。网站上线1年，ipad端7月3日上线。IPAD版上线一周积累20万用户，第一周有11.000多幅漫画上传。'
    print fc.naive_classify(s.cut(c))
    # fc.build_labeled_corpus()
    # fc.train('template/fields.1.data')