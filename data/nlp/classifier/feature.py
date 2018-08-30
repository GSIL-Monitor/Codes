# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common.zhtools.segment import Segmenter
from common.zhtools import stopword

from abc import abstractmethod
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.linear_model import SGDClassifier
from sklearn.grid_search import GridSearchCV


class FeatureExtractor(object):

    @abstractmethod
    def train(self, docs, labels):
        pass

    @abstractmethod
    def transform(self, docs):
        pass


class TfIdfExtractor(FeatureExtractor):

    def __init__(self, opt=None):

        if not isinstance(opt, dict):
            opt = {}

        if opt.get('segmenter'):
            self.seg = opt.get('segmenter')
        else:
            self.seg = Segmenter()
        self.vectorizer = TfidfVectorizer(sublinear_tf=True,
                                          stop_words=stopword.get_standard_stopwords(),
                                          max_df=opt.get('max_df', 0.5),
                                          min_df=opt.get('min_df', 50),
                                          max_features=5000)
        self.selector = SelectKBest(chi2, k=opt.get('topk', 'all'))

    def train(self, docs, labels, seged=False):

        trainset = self.vectorizer.fit_transform(self.iter_docs(docs, seged))
        # print len(self.vectorizer.get_feature_names())
        # trainset = self.selector.fit_transform(trainset, labels)
        return trainset, labels

    def transform(self, docs, seged=False):

        return self.vectorizer.transform(self.iter_docs(docs, seged))
        # return self.selector.transform(self.vectorizer.transform(self.iter_docs(docs, seged)))

    def iter_docs(self, docs, seged):

        for doc in docs:
            if not seged:
                yield ' '.join(self.seg.cut(doc))
            else:
                yield doc


class BigramExtractor(FeatureExtractor):

    def __init__(self):

        self.vectorizer = CountVectorizer(ngram_range=(1, 1), max_df=0.8, min_df=5)
        self.train()

    def train(self, trainx=None, trainy=None):

        trainx, trainy = load_data()
        self.vectorizer.fit(trainx, trainy)
        print len(self.vectorizer.get_feature_names()), 'feature count'

    def transform(self, docs):

        return self.vectorizer.transform(docs)


class PipeExtractor(FeatureExtractor):

    def __init__(self):
        self.pipeline = Pipeline([
            ('vect', CountVectorizer(ngram_range=(1, 2), max_df=0.6, min_df=0.1)),
            ('tfidf', TfidfTransformer()),
        ])


def load_data():

    db = dbcon.connect_torndb()
    seg = Segmenter()
    X, Y = [], []
    for item in db.query('select * from source_context;'):
        X.append(' '.join(list(seg.cut(item.content))).strip())
        Y.append(item.type == 30010)
    db.close()
    return X, Y


if __name__ == '__main__':

    print __file__
    pipeline = Pipeline([
        # ('vect', CountVectorizer()),
        # ('tfidf', TfidfTransformer()),
        # ('selector', SelectKBest()),
        ('vect', TfidfVectorizer()),
        ('clf', SGDClassifier()),
    ])
    parameters = {
        'vect__max_df': (0.5, 0.6, 0.7, 0.8),
        'vect__min_df': (0.01, 0.05, 0.1, 0.2, 0.3),
        # 'vect__max_features': (5000, 10000, 50000),
        # 'vect__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
        # 'selector__k': (300, 500, 1000, 2000, 5000, 10000),
        #'tfidf__norm': ('l1', 'l2'),
        'clf__alpha': (0.00001, 0.000001),
        'clf__penalty': ('l2', 'elasticnet'),
    }

    trainx, trainy = load_data()
    # from sklearn.datasets import fetch_20newsgroups
    # categories = [
    #     'alt.atheism',
    #     'talk.religion.misc',
    # ]
    # data = fetch_20newsgroups(subset='train', categories=categories)
    # trainx, trainy = data.data, data.target
    print 'data loaded'

    grid_search = GridSearchCV(pipeline, parameters, n_jobs=1, verbose=1)
    grid_search.fit(trainx, trainx)
    for item in grid_search.grid_scores_:
        print item
    print grid_search.best_params_