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
from common.zhtools.segment import Segmenter
from common.zhtools import word_filter
from common.feed import NewsFeeder

import itertools
import logging
import pymongo
import numpy as np
import tensorflow as tf
from random import sample
from tensorflow.contrib import learn
from sklearn.externals import joblib
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
from sklearn import metrics

# logging
logging.getLogger('fund').handlers = []
logger_fund = logging.getLogger('cate')
logger_fund.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_fund.addHandler(stream_handler)


def load_training_data():

    news_feeder = NewsFeeder()
    trainx, trainy = [], []

    mongo = dbcon.connect_mongo()
    for record in mongo.article.news.find({'$and': [{'category': {'$ne': None}}, {'category': {'$ne': 60199}}],
                                           'category_confidence': None,
                                           'type': 60001}).sort('createTime', pymongo.DESCENDING).limit(5000):
        contents = news_feeder.feed(record)
        if len(contents) > 10:
            # samples.append((' '.join(contents), int(record['category'] == 60101)))

            label = int(record['category'] == 60101)
            if trainy.count(label) <= 5000:
                trainx.append(' '.join(contents))
                trainy.append(label)

    mongo.close()

    # print set(trainy)
    return np.array(trainx), np.array(trainy)


def get_fund_classifier():

    sample_x, sample_y = load_training_data()

    MAX_DOCUMENT_LENGTH = 50
    EMBEDDING_SIZE = 200

    vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    sample_x = np.array(list(vocab_processor.fit_transform(sample_x)))
    n_words = len(vocab_processor.vocabulary_)
    logger_fund.info('Size of data')
    logger_fund.info(sample_x.shape)
    logger_fund.info('Total words: %d' % n_words)

    def average_model(X, y):

        word_vectors = learn.ops.categorical_variable(X, n_classes=n_words, embedding_size=EMBEDDING_SIZE, name='words')
        features = tf.reduce_max(word_vectors, reduction_indices=1)
        return learn.models.logistic_regression(features, y)

    def rnn_model(X, y):

        word_vectors = learn.ops.categorical_variable(X, n_classes=n_words, embedding_size=EMBEDDING_SIZE, name='words')
        word_list = tf.unpack(word_vectors, axis=1)
        cell = tf.nn.rnn_cell.GRUCell(EMBEDDING_SIZE)
        _, encoding = tf.nn.rnn(cell, word_list, dtype=tf.float32)
        return learn.models.logistic_regression(encoding, y)

    classifier = learn.TensorFlowEstimator(model_fn=rnn_model, n_classes=2, continue_training=True, steps=1000,
                                           learning_rate=0.1, optimizer='Adagrad')
    classifier.fit(sample_x, sample_y)
    return vocab_processor, classifier


if __name__ == '__main__':

    print __file__

    sample_x, sample_y = load_training_data()
    trainx, testx, trainy, testy = train_test_split(sample_x, sample_y, test_size=0.2, random_state=42)

    MAX_DOCUMENT_LENGTH = 50
    EMBEDDING_SIZE = 200

    vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    trainx = np.array(list(vocab_processor.fit_transform(trainx)))
    testx = np.array(list(vocab_processor.fit_transform(testx)))
    n_words = len(vocab_processor.vocabulary_)
    logger_fund.info('Size of data')
    logger_fund.info(trainx.shape)
    logger_fund.info('Total words: %d' % n_words)

    def average_model(X, y):

        word_vectors = learn.ops.categorical_variable(X, n_classes=n_words, embedding_size=EMBEDDING_SIZE, name='words')
        features = tf.reduce_max(word_vectors, reduction_indices=1)
        return learn.models.logistic_regression(features, y)

    def rnn_model(X, y):

        word_vectors = learn.ops.categorical_variable(X, n_classes=n_words, embedding_size=EMBEDDING_SIZE, name='words')
        word_list = tf.unpack(word_vectors, axis=1)
        cell = tf.nn.rnn_cell.GRUCell(EMBEDDING_SIZE)
        _, encoding = tf.nn.rnn(cell, word_list, dtype=tf.float32)
        return learn.models.logistic_regression(encoding, y)

    # clf = learn.TensorFlowEstimator(model_fn=rnn_model, n_classes=15, steps=100, optimizer='Adam',
    #                                 learning_rate=0.01, continue_training=True)
    # clf.fit(trainx, trainy)
    # joblib.dump(clf, os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/category.rnn.model'))

    # scores = cross_validation.cross_val_score(clf, trainx, trainy, scoring='precision', cv=5)
    # print MAX_DOCUMENT_LENGTH, EMBEDDING_SIZE, scores.mean(), scores

    # score = metrics.accuracy_score(trainy, clf.predict(trainx))
    # score = metrics.accuracy_score(testy, clf.predict(testx))
    # print('Accuracy: {0:f}'.format(score))

    parameters = {
        'learning_rate': [0.05, 0.1, 0.15],
        'steps': [500, 1000, 1200, 1500, 2000],
        'optimizer': ["Adam", "Adagrad"]
    }

    keys, values = parameters.keys(), parameters.values()
    cvscores = []
    for parameter in itertools.product(*values):
        ps = {keys[i]: parameter[i] for i in xrange(3)}
        clf = learn.TensorFlowEstimator(model_fn=rnn_model, n_classes=2, continue_training=True, **ps)
        clf.fit(trainx, trainy)
        score = metrics.accuracy_score(testy, clf.predict(testx))
        cvscores.append((ps, score))
    for cvscore in cvscores:
        print cvscore[0], cvscore[1]
    print 'best score'
    print sorted(cvscores, key=lambda x: x[1], reverse=True)[0]