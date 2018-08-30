# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import config as tsbconfig
from email_helper import send_mail

import os
import logging
import json
import ConfigParser
from kafka import KafkaConsumer

# logging
logging.getLogger('alarm').handlers = []
logger_alarm = logging.getLogger('alarm')
logger_alarm.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_alarm.addHandler(stream_handler)


class Alarm(object):

    def __init__(self):

        url = tsbconfig.get_kafka_config()
        self.consumer_alarm = KafkaConsumer("alarm", group_id="exception_catch",
                                            bootstrap_servers=[url], auto_offset_reset='smallest')
        self.configs = self.__load_config()
        self.reload_circle = 10

    def __load_config(self):

        cf = ConfigParser.ConfigParser()
        cf.read(os.path.join(os.path.split(os.path.realpath(__file__))[0], "../../conf/alarm.conf"))
        configs = {}
        for session in cf.sections():
            configs[cf.get(session, 'source')] = cf.items(session)
        return configs

    def __reload(self):

        self.reload_circle = 10
        self.configs = self.__load_config()

    def keep_informed(self):

        global logger_alarm
        for msg in self.consumer_alarm:
            logger_alarm.info("%s:%d:%d: key=%s value=%s" % (msg.topic, msg.partition, msg.offset, msg.key, msg.value))
            self.reload_circle -= 1
            if self.reload_circle == 0:
                self.__reload()
            msg = json.loads(msg.value)
            receiver = self.configs.get(msg.get('source'))
            if receiver:
                send_mail(u'烯牛数据', u'烯牛数据', u'noreply@xiniudata.com', receiver, u'报错', msg.get('comments'))
                logger_alarm.info('Mail sent')


if __name__ == '__main__':

    alarm = Alarm()
    alarm.keep_informed()