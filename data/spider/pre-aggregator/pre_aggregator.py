# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import gridfs
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from tld import get_tld
from urlparse import urlsplit
import tldextract

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import pre_util



import beian



def prepare():
    beian



if __name__ == '__main__':
    (logger, mongo, kafka_producer, kafka_consumer) = pre_util.parser_init("pre", "parser_v2", "pre")

    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    source_company_id = msg["id"]

                    if type == "company":
                        print ''

                except Exception,e :
                    logger.exception(e)
                finally:
                    kafka_consumer.task_done(message)
                    kafka_consumer.commit()
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            (logger, mongo, kafka_producer, kafka_consumer) = pre_util.parser_init("pre", "parser_v2", "pre")
