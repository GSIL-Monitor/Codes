# -*- coding: utf-8 -*-
import os, sys
import time
import json
from kafka import (KafkaConsumer, KafkaClient)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import config
import loghelper

#logger
loghelper.init_logger("test", stream=True)
logger = loghelper.get_logger("test")


# kafka
kafkaConsumer = None


def initKafka():
    global kafkaConsumer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    kafkaConsumer = KafkaConsumer("coldcall", group_id="test",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')

if __name__ == '__main__':
    logger.info("test start")
    initKafka()

    while True:
        try:
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)

                except Exception,e :
                    logger.exception(e)
                finally:
                    #kafkaConsumer.task_done(message)
                    #kafkaConsumer.commit()
                    pass

        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            initKafka()