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
import config as tsbconfig
from basic_track import TopicTracker

import logging
import json
import socket
from datetime import datetime
from kafka import KafkaConsumer, KafkaClient, SimpleProducer

# kafka
consumer_topic_message_news = None
consumer_topic_message_company = None
sproducer_topic_message = None

# logging
logging.getLogger('track_topic').handlers = []
logger_track_topic = logging.getLogger('track_topic')
logger_track_topic.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track_topic.addHandler(stream_handler)


def init_kafka(setting='tpm'):

    global consumer_topic_message_news, consumer_topic_message_company, producer_topic_message

    url = tsbconfig.get_kafka_config()
    # HashedPartitioner is default
    if setting == 'tpm':
        consumer_topic_message_news = KafkaConsumer("task_news_done", group_id="track topic message",
                                                    bootstrap_servers=[url], auto_offset_reset='smallest')
    elif setting == 'tpc':
        consumer_topic_message_company = KafkaConsumer("keyword_v2", group_id="track topic message company",
                                                       session_timeout_ms=9000,
                                                       bootstrap_servers=[url], auto_offset_reset='smallest')
    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_topic_message = SimpleProducer(kafka)


def general_topic_news_incremental():

    global logger_track_topic, consumer_topic_message_news, producer_topic_message
    tt = TopicTracker()
    socket.setdefaulttimeout(0.5)
    init_kafka('tpm')
    logger_track_topic.info('Incremental generate track topic message of news')
    start_hour = int(datetime.now().hour)

    for message in consumer_topic_message_news:
        if int(datetime.now().hour) != start_hour:
            start_hour = int(datetime.now().hour)
            tt.reload_topics()
        try:
            logger_track_topic.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                   message.offset, message.key, message.value))
            result = dict(tt.fit_news_id(json.loads(message.value).get('newsId')))
            logger_track_topic.info('Processsed %s, %s' % (json.loads(message.value).get('newsId'), json.dumps(result)))
        except Exception, e:
            logger_track_topic.exception(e)


def general_topic_company_incremental():

    global logger_track_topic, consumer_topic_message_company, producer_topic_message
    tt = TopicTracker()
    db = dbcon.connect_torndb()
    socket.setdefaulttimeout(0.5)
    init_kafka('tpc')
    logger_track_topic.info('Incremental generate track topic message of company')
    start_hour = int(datetime.now().hour)

    for message in consumer_topic_message_company:
        if int(datetime.now().hour) != start_hour:
            start_hour = int(datetime.now().hour)
            tt.reload_topics()
        try:
            logger_track_topic.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                   message.offset, message.key, message.value))
            cid, action = json.loads(message.value).get('id'), json.loads(message.value).get('action', 'create')
            if action == 'delete':
                continue
            if dbutil.get_company_active(db, cid) is not None and dbutil.get_company_active(db, cid) != 'Y':
                continue
            result = dict(list(tt.fit_company_id(cid)))
            logger_track_topic.info('Processsed %s, %s' % (json.loads(message.value).get('id'), json.dumps(result)))
        except Exception, e:
            logger_track_topic.exception(e)


def general_topic_track_init():

    tt = TopicTracker()
    tt.fit_latest()


def special_gongshang():

    global logger_track_topic, consumer_topic_message_company
    tt = TopicTracker()
    db = dbcon.connect_torndb()
    socket.setdefaulttimeout(0.5)
    init_kafka('tpc')
    logger_track_topic.info('Incremental generate track topic message of company')


if __name__ == '__main__':

    if sys.argv[1] == 'general_news':
        general_topic_news_incremental()
    elif sys.argv[1] == 'general_company':
        general_topic_company_incremental()
