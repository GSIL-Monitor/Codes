# -*- coding: utf-8 -*-
import os, sys
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import config
import loghelper


#logger
loghelper.init_logger("test", stream=True)
logger = loghelper.get_logger("test")


# kafka
kafkaProducer = None
kafkaConsumer = None

def initKafka():
    global kafkaProducer
    global kafkaConsumer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("crawler_itjuzi_v2", group_id="test",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')


if __name__ == '__main__':
    initKafka()