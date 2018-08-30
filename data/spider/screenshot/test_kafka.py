__author__ = 'victor'

import sys
reload(sys)
sys.path.append('../nlp')
sys.setdefaultencoding('utf-8')

import json
from common import nlpconfig
from kafka import KafkaConsumer

consumer_shot = None


def init_kafka():

    global consumer_shot

    url = nlpconfig.get_kafka_config().get('url')
    # consumer_shot = KafkaConsumer("aggregator", group_id="screenshot",
    #                               metadata_broker_list=[url], auto_offset_reset='smallest')
    consumer_shot = KafkaConsumer("aggregator", group_id="screen shot",
                                  metadata_broker_list=[url], auto_offset_reset='smallest')


if __name__ == '__main__':

    print __file__
    init_kafka()
    for index, message in enumerate(consumer_shot):
        cid = int(json.loads(message.value).get('_id'))
        print index
