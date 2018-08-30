# coding=utf-8
__author__ = 'victor'

import os
import json
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

from kafka import KafkaConsumer

import config as tsbconfig


consumer = None


def init_kafka():

    global consumer

    url = tsbconfig.get_kafka_config()
    # HashedPartitioner is default
    consumer = KafkaConsumer("task_company", group_id="test5",
                             bootstrap_servers=[url], auto_offset_reset='smallest')


if __name__ == '__main__':

    init_kafka()
    for index, message in enumerate(consumer):
        # if index % 5000 == 0:
        if json.loads(message.value).get('source') == 'company_fa':
            print index, message.value
        # msg = json.loads(message.value).get('id')
        # if msg and msg == 93779 or msg == '93779':
        #     print message