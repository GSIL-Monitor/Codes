 # coding=utf-8
__author__ = 'wangqc'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common.feed import Feeder, NewsFeeder

import codecs
import multiprocessing
from bson.objectid import ObjectId
from datetime import datetime
from itertools import product
from random import randint

import numpy as np
import fasttext
from sklearn import metrics
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import cross_validate
from gensim.models import Word2Vec


class FundingClassifier(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.feeder = Feeder()
        self.nf = NewsFeeder()

        self.keywords=['融资']
        self.neg_sample = 'task/files/fund.negsample'
        self.content_model_path = 'models/fund/fasttext.fundfull.180226.bin'
        self.title_model_path = 'models/fund/fasttext.fundtitle.180226.bin'

        if os.path.exists(self.content_model_path):
            self.content_model = fasttext.load_model(self.content_model_path)
        if os.path.exists(self.title_model_path):
            self.title_model = fasttext.load_model(self.title_model_path)

    # convert news to data， if write: converted data should be written into file and label, full and title are needed
    def __featurize_news(self, record, label=None, full=None, title=None, t=50, write=True):

        content = ' '.join(self.nf.feed(record, granularity='fine'))
        _title = ' '.join(self.nf.wfilter(self.nf.seg.cut4search(record['title'].replace('\n', ' '))))
        if write:
            if len(content) > t and len(_title) > t // 5:
                full.write('%s __label__%d %s\n' % (record['_id'], label, content))
                title.write('%s __label__%d %s\n' % (record['_id'], label, _title))
        else:
            return content, _title

    # mode = 'train' or 'test', convert news to data
    # if train: generate train and validation data from selected news pool (TP : FP : others ~ 1:1:1)
    # if test: generate test data randomly from whole news pool
    def dump_data(self, path, boost_limit=20000, test_size=50000, mode='train'):

        # if not full text, pick only news title
        if mode != 'train' and mode != 'test':
            raise Exception, 'input mode as train or test'
        if mode == 'train':
            # collect negative sample ids
            ns_id = dict.fromkeys([line.strip() for line in codecs.open(self.neg_sample)], None)
            with codecs.open(path + 'full.train', 'w', 'utf-8') as ftrain, codecs.open(path + 'full.valid', 'w', 'utf-8') as fvalid,\
                    codecs.open(path + 'title.train', 'w', 'utf-8') as ttrain, codecs.open(path + 'title.valid', 'w', 'utf-8') as tvalid:
                boost = 0
                self.mongo.article.news.create_index([('createTime', -1)])
                for news in self.mongo.article.news.find(
                        {'processStatus': 1, 'modifyUser': {'$nin': [None, 139]}, 'features': {'$ne': None},
                         'createTime': {'$gt': datetime(2017, 1, 1)}}).sort([('createTime', -1)]):
                    # pick true sample
                    if 578349 in news['features']:
                        self.__featurize_news(news, 1, ftrain, ttrain) if randint(0, 4) else self.__featurize_news(news, 1, fvalid, tvalid)
                    # pick negative sample
                    elif str(news['_id']) in ns_id:
                        self.__featurize_news(news, 0, ftrain, ttrain) if randint(0, 4) else self.__featurize_news(news, 0, fvalid, tvalid)
                    # boost with other sample
                    elif boost < boost_limit:
                        self.__featurize_news(news, 0, ftrain, ttrain) if randint(0, 4) else self.__featurize_news(news, 0, fvalid, tvalid)
                        boost += 1
        else:
            with codecs.open(path + 'full.test', 'w', 'utf-8') as ftest, codecs.open(path + 'title.test', 'w', 'utf-8') as ttest:
                test_num = 0
                for news in self.mongo.article.news.find(
                        {'processStatus': 1, 'modifyUser': {'$nin': [None, 139]}, 'features': {'$ne': None}}):
                    if test_num > test_size:
                        break
                    if 578349 in news['features']:
                        self.__featurize_news(news, 1, ftest, ttest)
                    else:
                        self.__featurize_news(news, 0, ftest, ttest)
                    test_num += 1

    # summarize total label counts for each input file (e.g. train, validation and test data)
    def stat(self, path, *sources):

        with codecs.open(path + 'summary', 'w', 'utf-8') as fo:
            for s in sources:
                count = dict()
                for line in codecs.open(s, 'rb', 'utf-8'):
                    label = line.split(' ', 2)[1]
                    count[label] = count.get(label, 0) + 1
                summary = '\nLabel\tCount\n' + '\n'.join(['%-8s\t%-8d' % (k, v) for k, v in count.items()])
                fo.write('%s:\n\n' % (s.split('/')[-1]) + summary + '\n------\n\n')

    # fasttext params tuning on dim, lr, loss and ws, params input format as 'key=[*values]'
    def train(self, train, test, model, **kwargs):

        params = {'dim': [100, 150], 'lr': [0.1, 0.5, 1], 'loss': ['ns', 'hs'], 'ws': [5, 10]}
        for k, v in kwargs.items():
            params[k] = v
        keys, values = params.keys(), params.values()
        best, best_score = '', 0
        for p in product(*values):
            ps = {keys[i]: p[i] for i in xrange(4)}
            clf = fasttext.supervised(train, model + '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), **ps)
            result = clf.test(test)
            print '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3])
            print 'Precision: %.2f%%' % (result.precision * 100)
            print 'Recall Rate: %.2f%%\n' % (result.recall * 100)
            f1 = float(2.0 * result.precision * result.recall) / float(result.precision + result.recall)
            if best_score < f1:
                best, best_score, = '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), f1
        print '%s\n%.2f' % (best, best_score)

    # if full, test as test data file; else test as raw text
    def _model_predict(self, test, clf, full=True):

        if full:
            raw = np.array([line.split(' ', 2) for line in codecs.open(test, 'rb', 'utf-8')])
            ids, y, raw_text = raw[:, 0], np.array([int(i[-1]) for i in raw[:, 1]]), raw[:, 2]
            pp = np.array(clf.predict_proba(raw_text))[:, 0]
            return ids, y, raw_text, np.array([int(i[-1]) for i in pp[:, 0]]), np.array(map(float, pp[:, 1]))
        else:
            pp = np.array(clf.predict_proba(test))[:, 0]
            return np.array([int(i[-1]) for i in pp[:, 0]]), np.array(map(float, pp[:, 1]))

    # combine two fasttext classifiers results(build from full text and title text) to tag test data
    def _model_combine(self, yfpred, yfprob, ytpred, ytprob, titles):

        yfpred[yfprob < 0.65] = 0
        ytpred[ytprob < 0.55] = 0

        def have_word(text):
            for w in self.keywords:
                if w in text:
                    return True
            return False

        for i in range(len(yfpred)):
            if yfpred[i] and not have_word(titles[i]) and not ytpred[i]:
                yfpred[i] = 0
            elif not yfpred[i] and have_word(titles[i]) and ytpred[i]:
                yfpred[i] = 1
        return yfpred

    # tag 'fund' for test data; 1 as fund news; 0 as not fund news
    def test(self, ftest, ttest):

        _, y, _, yfpred, yfprob = self._model_predict(ftest, self.content_model)
        title_text = np.array([line.split(' ', 2)[-1] for line in codecs.open(ttest, 'rb', 'utf-8')])
        ytpred, ytprob = self._model_predict(title_text, self.title_model, full=False)
        ypred = self._model_combine(yfpred, yfprob, ytpred, ytprob, title_text)
        return metrics.accuracy_score(y, ypred)

    # # tag 'fund' for news; 1 as fund news; 0 as not fund news
    def predict(self, news_record):

        try:
            content, title = self.__featurize_news(news_record, write=False)
            yfpred, yfprob = self._model_predict([content], self.content_model, full=False)
            ytpred, ytprob = self._model_predict([title], self.title_model, full=False)
            return self._model_combine(yfpred, yfprob, ytpred, ytprob, [title])[0]
        except Exception, e:
            return

    def predict_news_id(self, nid):

        news = self.mongo.article.news.find_one({'_id': ObjectId(nid)})
        return self.predict(news)

    # def embedding(self, source):
    #
    #     name = 'tmp/fund/w2v/fund'
    #     contents = [line.split()[2:] for line in codecs.open(source, 'rb', 'utf-8')]
    #     model = Word2Vec(contents, size=400, window=3, min_count=20, workers=multiprocessing.cpu_count())
    #     model.save('%s.binary.w2vmodel' % name)
    #
    # def vectorized(self, source):
    #
    #     if os.path.exists('%s_id.npy' % source):
    #         ids, x, y = np.load('%s_id.npy' % source), np.load('%s_x.npy' % source), np.load('%s_y.npy' % source)
    #     else:
    #         word2vec_model = 'embbeding/models/s400w3min20_yitai.binary.w2vmodel'
    #         # word2vec_model = 'tmp/fund/w2v/fund.binary.w2vmodel'
    #         w2v = Word2Vec.load(word2vec_model)
    #         raw = np.array([line.split(' ', 2) for line in codecs.open(source, 'rb', 'utf-8')])
    #         ids, y = np.array(raw[:, 0]), np.array([int(l[-1]) for l in raw[:, 1]])
    #         x = np.array([np.mean([w2v[w] for w in c.split() if w in w2v], axis=0) for c in raw[:, 2]])
    #         np.save('%s_id.npy' % source, ids), np.save('%s_x.npy' % source, x), np.save('%s_y.npy' % source, y)
    #     return ids, x, y
    #
    # def sample(self, x, y, true_num=2000, false_num=4000):
    #
    #     mask_true = np.random.choice(np.arange(len(y))[y == 1], true_num, replace=False)
    #     mask_false = np.random.choice(np.arange(len(y))[y == 0], false_num, replace=False)
    #     return x[np.concatenate((mask_true, mask_false))], np.array([1]*true_num + [0]*false_num)
    #
    # def w2v_train(self, model, x, y):
    #
    #     if model == 'svm':
    #         return [np.mean(cross_validate(SVC(C=c), x, y, cv=5, scoring='accuracy')['test_score'])
    #                 for c in [10, 50, 100, 200, 500]]
    #     if model == 'lr':
    #         return [np.mean(cross_validate(LogisticRegression(C=c), x, y, cv=5, scoring='accuracy')['test_score'])
    #                 for c in [0.01, 0.1, 1, 10, 100]]
    #     if model == 'ada':
    #         return [np.mean(cross_validate(AdaBoostClassifier(learning_rate=lr, n_estimators=200), x, y, cv=5, scoring='accuracy')['test_score'])
    #                 for lr in [0.01, 0.1, 0.5, 1]]
    #
    # def naive(self, source):
    #
    #     raw = np.array([line.split(' ', 2) for line in codecs.open(source, 'rb', 'utf-8')])
    #     return metrics.accuracy_score([int(l[-1]) for l in raw[:, 1]], [('融资' in x) * 1 for x in raw[:, 2]])


if __name__ == '__main__':

    ft = FundingClassifier()
    # ft.dump_data('cache/fund/', mode='train')
    # ft.dump_data('cache/fund/', mode='test')
    # ft.stat('cache/fund/', 'cache/fund/full.train', 'cache/fund/full.valid', 'cache/fund/full.test')
    # # fasttext
    # ft.train('cache/fund/full.train', 'cache/fund/full.valid', 'models/fund/full.models.', dim=[100], lr=[0.5], loss = ['hs'], ws=[5])
    # ft.train('cache/fund/title.train', 'cache/fund/title.valid', 'models/fund/title.models.', dim=[120], lr=[0.2], loss = ['hs'], ws=[5])
    # print ft.test('cache/fund/full.test', 'cache/fund/title.test')
    print ft.predict_news_id('5ad49467deb4717d55915098')
    # word vector machine learning
    # embedding('cache/fund.train')
    # _, x, y = vectorized('cache/fund.train')
    # print w2v_train('svm', *sample(x, y))




