# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, name_helper, url_helper
import json, config, traceback, time, util
from kafka import (KafkaClient, KafkaConsumer, SimpleProducer)
from bson.objectid import ObjectId
import mt_generator

# kafka
kafkaConsumer = None
kafkaProducer = None

# logger
loghelper.init_logger("mt_flow", stream=True)
logger = loghelper.get_logger("mt_flow")

mongo = db.connect_mongo()
collection = mongo['open-maintain'].task
collectionUser = mongo['open-maintain'].user
conn = db.connect_torndb()


def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("user", group_id="maintain",
                                  bootstrap_servers=[url],
                                  auto_offset_reset='smallest')


if __name__ == "__main__":

    init_kafka()
    while True:
        try:
            logger.info("start")
            # logger.info(kafkaConsumer)
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    # msg: type:XXXX, name :xxxx
                    logger.info(json.dumps(msg, ensure_ascii=False, cls=util.CJsonEncoder))

                    # {u'posting_time': 1513233018091, u'from': u'atom', u'task_id': u'5a31e118346dbf6bd34caf58'}
                    userId = msg['userId']
                    if msg['online'] == 'N':
                        logger.info('user %s offline, unassign his tasks' % userId)
                        collection.update_many({'taskUser': userId, 'active': 'Y', 'flow': 'Y', "processStatus": 0},
                                               {'$set': {'taskUser': -666}})
                    kafkaConsumer.commit()

                except Exception, e:
                    traceback.print_exc()
                    # break
        except KeyboardInterrupt:
            logger.info("break1")
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()
