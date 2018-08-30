# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.setdefaultencoding('utf-8')

import config as tsbconfig

import json
from kafka import KafkaConsumer


def clear_kafka():

    url = tsbconfig.get_kafka_config()
    consumer_rec = KafkaConsumer("keyword_v2", group_id="company recommend",
                                 bootstrap_servers=[url], auto_offset_reset='smallest')
    for index, message in enumerate(consumer_rec):
        cid = json.loads(message.value).get('id')
        if int(cid) < 180000:
            consumer_rec.commit()
        if index % 1000 == 0:
            print index, message

if __name__ == 'main':

    clear_kafka()