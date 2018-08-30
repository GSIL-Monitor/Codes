# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import config as tsbconfig
from common import nlpconfig

import json
from kafka import KafkaConsumer

# kafka
consumer = None


def initKafka(topic, group):

    global consumer

    # url = nlpconfig.get_kafka_config().get('url')
    # consumer = KafkaConsumer(topic, group_id="test",
    #                          metadata_broker_list=[url], auto_offset_reset='smallest')
    url = tsbconfig.get_kafka_config()
    consumer = KafkaConsumer(topic, group_id=group,
                             bootstrap_servers=[url], auto_offset_reset='smallest')


def test(topic, gap=1, group='test'):

    global consumer
    initKafka(topic, group)
    gap = int(gap)
    print consumer
    for index, msg in enumerate(consumer):
        if json.loads(msg.value).get('id', '') == 19623:
            print msg

if __name__ == '__main__':

    test(sys.argv[1], sys.argv[2], sys.argv[3])