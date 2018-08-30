# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import json
from kafka import KafkaClient, SimpleProducer, KafkaConsumer

import config as tsbconfig


consumer = None


def init_kafka(index):

    global consumer

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    consumer = SimpleProducer(kafka)
    consumer = KafkaConsumer("keyword_v2", group_id="create search%s index" % index,
                             bootstrap_servers=[url], auto_offset_reset='smallest')


def clear_msg(index):

    global consumer
    init_kafka(index)
    for message in consumer:
        action = json.loads(message.value).get('action', 'create')
        if action == 'create':
            consumer.commit()
            print message


def count_msg(index):

    global consumer
    init_kafka(index)
    for count, msg in enumerate(consumer):
        if count % 100 == 0:
            print count


def locate():

    global consumer
    init_kafka('test0523')
    for message in consumer:
        if json.loads(message.value).get('id', 0) == 329483:
            print message


if __name__ == '__main__':

    if sys.argv[1] == 'clear':
        clear_msg(sys.argv[2])
    elif sys.argv[1] == 'count':
        count_msg(sys.argv[2])
    elif sys.argv[1] == 'locate':
        locate()
