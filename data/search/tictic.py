# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import db as dbcon
import config
from nlp.common import dbutil
from nlp.score.job import good_job
from nlp.score.downloads import black_android_all
from nlp.score.person import FounderScorer
from client import SearchClient
from api.views.collection import update_collection

import json
import logging
from elasticsearch import Elasticsearch
from kafka import KafkaClient, SimpleProducer

# logging
logging.getLogger('tictic').handlers = []
logger_tic = logging.getLogger('tictic')
logger_tic.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_tic.addHandler(stream_handler)

# init kafka
url = config.get_kafka_config()
kafka = KafkaClient(url)
producer_collection = SimpleProducer(kafka)


def init_es():

    if sys.platform == 'darwin':
        host, port = config.get_es_local()
    else:
        # host, port = config.get_es_config()
        host, port = config.get_es_config_2()
    return SearchClient(Elasticsearch([{'host': host, 'port': port}]))


def do_query(client, query):

    query['size'] = max(query.get('size', 0), 1000)
    if 1000 in query.get('round') and (0 not in query.get('round')):
        query.setdefault('round', []).append(0)

    return client.search('company', **query)


def do_query2(client, query):

    rounds = query.get('filter', {}).get('round', [])
    if 1000 in rounds and (0 not in rounds):
        query.setdefault('filter', {}).setdefault('round', []).append(0)
    return client.search('collection', **query)


def update_black():

    # job
    # logger_tic.info('start to process black job')
    # good_job()
    # logger_tic.info('job black processed')
    #
    # # android
    # logger_tic.info('start to process black android')
    # db = dbcon.connect_torndb()
    # for cid, score in black_android_all().iteritems():
    #     dbutil.update_collection(db, 8, cid, score)
    # db.close()
    # logger_tic.info('android black processed')

    # 清北复交
    logger_tic.info(u'start to process 清北')
    db = dbcon.connect_torndb()
    fs = FounderScorer()
    for cid in iter(dbutil.get_all_company_id(db)):
        if dbutil.get_company_round(db, cid) > 1030:
            continue
        score = fs.address_education(db, cid)
        if score > 0:
            dbutil.update_collection(db, 409, cid, round(float(score)/10, 2))
    db.close()
    logger_tic.info(u'清北 processed')


def update_rules():

    global logger_tic
    db = dbcon.connect_torndb()
    client = init_es()
    for rule in db.query('select id, rule from collection where rule is not null'):
        try:
            rules = json.loads(rule.rule)
            if 'filter' in rules:
                results = do_query2(client, rules)
            else:
                results = do_query(client, rules)
            updates = update_collection(rule.id, results, False)
            send_msg(rule.id, len(updates))
            logger_tic.info('Succed %s, update %s' % (rule.id, ','.join([str(cid) for cid in updates])))
        except Exception, e:
            logger_tic.exception('Failed %s, %s' % (rule.id, e))
    db.close()


def send_msg(colid, count):

    global producer_collection
    if count and count > 0:
        producer_collection.send_messages("track_message",
                                          json.dumps({'id': colid, 'type': 'collection', 'new_count': count}))


if __name__ == '__main__':

    if sys.argv[1] == 'rule':
        update_rules()
    elif sys.argv[1] == 'black':
        update_black()