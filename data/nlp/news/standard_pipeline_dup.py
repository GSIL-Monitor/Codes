# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common.zhtools.segment import Segmenter
from common.zhtools import word_filter
from classifier.simple_sector import ClusterVIPClassifier
from mentioned import CompanyLinker

import time
import logging
import pymongo
import numpy as np
import tensorflow as tf
from tensorflow.contrib import learn
from datetime import datetime, timedelta


# logging
logging.getLogger('news_pip').handlers = []
logger_news_pip = logging.getLogger('news_pip')
logger_news_pip.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_news_pip.addHandler(stream_handler)


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
    for record in mongo.article.news.find({'$and': [{'category': {'$ne': None}}, {'category': {'$ne': 60199}},
                                                    {'category': {'$ne': 60106}}],
                                           'type': 60001, 'category_confidence': None}).limit(10000):
        contents = wfilter(seg.cut(record['title']))
        contents.extend(wfilter(seg.cut(' '.join([piece['content'] for piece in record['contents']]))))
        if len(contents) > 10:
            trainx.append(' '.join(contents))
            trainy.append(int(labels.get(record['category'])))
    mongo.close()

    return np.array(trainx), np.array(trainy)


if __name__ == '__main__':

    logger_news_pip.info('start to process')

    # prepare for category
    trainx, trainy = load_ruled_news()

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
    n_words = len(vocab_processor.vocabulary_)
    logger_news_pip.info('Size of data')
    logger_news_pip.info(trainx.shape)
    logger_news_pip.info('Total words: %d' % n_words)
    clf = learn.TensorFlowEstimator(model_fn=rnn_model, n_classes=5, steps=2000, optimizer='Adagrad',
                                    learning_rate=0.1, continue_training=True)
    clf.fit(trainx, trainy)

    # prepare for simple sector
    cvipc = ClusterVIPClassifier()

    # prepare for mentioned company
    life_circle_linker = 100
    life_circle_linker_max = 100
    linker = CompanyLinker()

    # prepare for connection
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    seg = Segmenter(tag=True)
    wfilter = word_filter.get_default_filter()

    logger_news_pip.info('start to process pending news')

    while True:

        for record in list(mongo.article.news.find({'type': {'$in': [60001, 60002, 60003]},
                                                    'processStatus': 0}).sort('date', pymongo.DESCENDING)):

            if record.get('source', 0) == 13022:
                mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -4}})
                continue

            # process sector
            try:
                if record.get('sectors', False):
                    pass
                elif cvipc.classify_rules(record):
                    sids, weights = cvipc.classify_rules(record)
                    mongo.article.news.update({'_id': record['_id']}, {'$set': {'sectors': sids,
                                                                                'sector_confidence': weights}})
                else:
                    docs = [record['title']]
                    docs.extend([content['content'] for content in record.get('contents', [])])
                    results = cvipc.classify_stream(docs, topn=2)
                    # process first sector
                    vip, weight = results[0]
                    if weight < 0.5:
                        sids = [999]
                        weights = [round(weight, 2)]
                    else:
                        sids = [db.get('select id from sector where sectorName=%s and level=1;', vip).id]
                        weights = [round(weight, 2)]
                    # process second sector
                    if len(results) == 2 and results[1][1] >= 5:
                        try:
                                vip, weight = results[1]
                                sids.append(db.get('select id from sector where sectorName=%s;', vip).id)
                                weights.append(round(weight, 2))
                        except Exception, e:
                            logger_news_pip.exception('second sector exception %s, %s' % (record['_id'], e))
                    mongo.article.news.update({'_id': record['_id']}, {'$set': {'sectors': sids,
                                                                                'sector_confidence': weights}})
                logger_news_pip.info('sector processed %s' % record['_id'])
            except Exception, e:
                logger_news_pip.exception('sector failed, %s, %s' % (record['_id'], e))
                mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -1}})
                continue

            # process mentioned company
            if record.get('date', False) and (record.get('date') < datetime.now() - timedelta(days=30)) \
                    and not record.get('companyIds'):
                try:
                    if life_circle_linker <= 0:
                        linker = CompanyLinker()
                        life_circle_linker = life_circle_linker_max
                    mentioned = list(linker.find(record['_id']))
                    if record.get('companyId', False) and record.get('companyId') not in [x[0] for x in mentioned]:
                        mentioned.append((record['companyId'], 1))
                    if mentioned:
                        cids, confs = [x[0] for x in mentioned], [x[1] for x in mentioned]
                        mongo.article.news.update({'_id': record['_id']},
                                                  {'$set': {'companyIds': cids, 'mention_confidence': confs}})
                    else:
                        cids = [0]
                    logger_news_pip.info('mentioned processed %s, found %s' % (record['_id'], str(cids)))
                    life_circle_linker -= 1
                except Exception, e:
                    logger_news_pip.exception('mentioned failed, %s, %s' % (record['_id'], e))
                    mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -2}})
                    continue

            # process category
            try:
                if (record.get('category', None) is None) and (record.get('type', 0) == 60001):
                    contents = wfilter(seg.cut(record['title']))
                    contents.extend(wfilter(seg.cut(' '.join([piece['content'] for piece in record['contents']]))))
                    contents = np.array(list(vocab_processor.fit_transform(np.array([' '.join(contents)]))))
                    label = clf.predict(contents)[0]
                    prob = clf.predict_proba(contents)[0][label]
                    category = labels_reverse.get(label)
                    if prob < 0.7:
                        category = 60199
                        prob = 1 - prob
                    mongo.article.news.update({'_id': record['_id']},
                                              {'$set': {'category': category,
                                                        'category_confidence': round(float(prob), 2)}})
                    logger_news_pip.info('category processed %s' % record['_id'])
                else:
                    logger_news_pip.info('category skip %s' % record['_id'])
            except Exception, e:
                logger_news_pip.exception('category failed, %s, %s' % (record['_id'], e))
                mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -3}})
                continue

            # mark done
            try:
                mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': 1, 'modifyUser': 139}})
                logger_news_pip.info('All Done, %s' % record['_id'])
            except Exception, e:
                logger_news_pip.exception('Fail to insert, %s, %s' % (record['_id'], e))

    time.sleep(600)