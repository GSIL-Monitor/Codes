# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html

from bson.objectid import ObjectId
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import requests
import util
import parser_util

if __name__ == '__main__':
    if len(sys.argv) > 2:
        parser_name = sys.argv[1]
        msg_name = sys.argv[2]
    else:
        print "usage: /opt/py-env/bin/python consume_messages.py recruit_jobtong crawler_recruit_jobtong "
        exit(0)


    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init(parser_name, msg_name)

    for message in kafka_consumer:
        logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
        msg = json.loads(message.value)
        type = msg["type"]
        company_key = msg["company_key"]

        if type == "company":
            kafka_consumer.task_done(message)
            kafka_consumer.commit()

