# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from feature import TfIdfExtractor
from feature import BigramExtractor

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV


def train():

    db = dbcon.connect_torndb()
    e = TfIdfExtractor()
    # e = BigramExtractor()
    X, Y = [], []
    for item in db.query('select * from source_context where confidence>0.95 and length(content)>100;'):
        X.append(item.content)
        Y.append(item.type == 30010)
    e.train(X, Y)
    db.close()
    return e, e.transform(X), Y


class ContextClassifier(object):

    def __init__(self, e=None, clf='lr'):

        self.extractor = e
        self.clf = self.__init_clf(clf)
        self.train()

    def classify_noise(self, docs):

        return self.clf.predict(self.extractor.transform(docs))

    def classify_noise_prob(self, docs):

        return self.clf.predict_proba(self.extractor.transform(docs))

    def __init_clf(self, clf):

        if clf == 'lr':
            return LogisticRegression(penalty='l2', C=5)
        else:
            return RandomForestClassifier()

    def train(self, trainx=None, trainy=None):

        e, trainx, trainy = train()
        self.extractor = e

        self.clf.fit(trainx, trainy)
        # valid = cross_validation.cross_val_score(self.clf, trainx, trainy, cv=10)
        # print valid.mean(), valid.max(), valid.min(), valid.var()

        # parameters = {'penalty': ('l1', 'l2'),
        #               'C': range(1, 15)}
        # gsclf = GridSearchCV(self.clf, parameters, cv=5, scoring='precision')
        # gsclf.fit(trainx, trainy)
        # for item in gsclf.grid_scores_:
        #     print item
        # print gsclf.best_params_


if __name__ == '__main__':

    cf = ContextClassifier(clf='lr')