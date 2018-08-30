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

import itertools
import logging
import numpy as np
import tensorflow as tf
from tensorflow.contrib import learn
from sklearn import metrics
from sklearn.cross_validation import train_test_split

# logging
logging.getLogger('cate').handlers = []
logger_cate = logging.getLogger('cate')
logger_cate.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_cate.addHandler(stream_handler)


labels = {
    60101: 0,
    60102: 1,
    60103: 2,
    60104: 3,
    60105: 4
}

labels_reverse = {v: k for k, v in labels.iteritems()}


def load_ruled_news():

    global labels

    seg = Segmenter(tag=True)
    wfilter = word_filter.get_default_filter()
    trainx, trainy = [], []

    mongo = dbcon.connect_mongo()
    for record in mongo.article.news.find({'$and': [{'category': {'$ne': None}}, {'category': {'$ne': 60199}}],
                                           'type': 60001, 'category_confidence': None}).limit(10000):
        contents = wfilter(seg.cut(record['title']))
        contents.extend(wfilter(seg.cut(' '.join([piece['content'] for piece in record['contents']]))))
        if len(contents) > 10:
            trainx.append(' '.join(contents))
            # trainy.append(int(record['category'] == 60101))
            trainy.append(labels.get(record['category']))
    mongo.close()

    # print set(trainy)
    return np.array(trainx), np.array(trainy)

if __name__ == '__main__':

    print __file__

    sample_x, sample_y = load_ruled_news()
    trainx, testx, trainy, testy = train_test_split(sample_x, sample_y, test_size=0.2, random_state=42)

    MAX_DOCUMENT_LENGTH = 50
    EMBEDDING_SIZE = 200

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

    vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    trainx = np.array(list(vocab_processor.fit_transform(trainx)))
    testx = np.array(list(vocab_processor.fit_transform(testx)))
    n_words = len(vocab_processor.vocabulary_)
    logger_cate.info('Size of data')
    logger_cate.info(trainx.shape)
    logger_cate.info('Total words: %d' % n_words)

    # clf = learn.TensorFlowEstimator(model_fn=rnn_model, n_classes=5, steps=100, optimizer='Adam',
    #                                 learning_rate=0.01, continue_training=True)
    # clf.fit(trainx, trainy)
    # joblib.dump(clf, os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/category.rnn.model'))

    # mongo = dbcon.connect_mongo()
    # seg = Segmenter(tag=True)
    # wfilter = word_filter.get_default_filter()
    # for record in list(mongo.article.news.find({'type': 60001, 'category': None, 'category_confidence': None})):
    #     try:
    #         contents = wfilter(seg.cut(record['title']))
    #         contents.extend(wfilter(seg.cut(' '.join([piece['content'] for piece in record['contents']]))))
    #         contents = np.array(list(vocab_processor.fit_transform(np.array([' '.join(contents)]))))
    #         label = clf.predict(contents)[0]
    #         prob = clf.predict_proba(contents)[0][label]
    #         category = labels_reverse.get(label)
    #         mongo.article.news.update({'_id': record['_id']}, {'$set': {'category': category,
    #                                                                     'category_confidence': round(float(prob), 2)}})
    #         logger_cate.info('%s category classified' % record['_id'])
    #     except Exception, e:
    #         logger_cate.exception('%s, %s' % (record['_id'], e))
    # mongo.close()


    # scores = cross_validation.cross_val_score(clf, trainx, trainy, scoring='precision', cv=5)
    # print MAX_DOCUMENT_LENGTH, EMBEDDING_SIZE, scores.mean(), scores

    parameters = {
        'learning_rate': [0.01, 0.05, 0.1],
        'steps': [2000, 1000, 500, 200],
        'optimizer': ["Adam", "Adagrad"]
    }
    #
    keys, values = parameters.keys(), parameters.values()
    cvscores = []
    for parameter in itertools.product(*values):
        ps = {keys[i]: parameter[i] for i in xrange(3)}
        clf = learn.TensorFlowEstimator(model_fn=rnn_model, n_classes=5, continue_training=True, **ps)
        clf.fit(trainx, trainy)
        score = metrics.accuracy_score(testy, clf.predict(testx))
        cvscores.append((ps, score))
    for cvscore in cvscores:
        print cvscore[0], cvscore[1]
    print 'best score'
    print sorted(cvscores, key=lambda x: x[1], reverse=True)[0]