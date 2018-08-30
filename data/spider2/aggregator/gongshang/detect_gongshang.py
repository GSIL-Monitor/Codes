# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import traceback
from kafka import (KafkaClient, KafkaConsumer, SimpleProducer)
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, db, config, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

#logger
loghelper.init_logger("detect_gongshang", stream=True)
logger = loghelper.get_logger("detect_gongshang")


# kafka
kafkaConsumer = None
kafkaProducer = None

def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("gongshang_detect", group_id="testgoshang",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')

def update(name):
    mongo = db.connect_mongo()
    collection_name = mongo.info.gongshang_name
    collection_name.update_one({"name": name}, {'$set': {"lastCheckTime": None}})
    mongo.close()

def insert(name):
    name = name.replace("（开业）","")
    sourceId = util.md5str(name)
    sid = parser_db_util.save_company_fullName(name,13099,sourceId)
    logger.info("sid:%s->sourceId:%s",sid, sourceId)
    parser_db_util.save_source_company_name(sid, name, 12010)

# return companyid list
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
                    if msg["type"] == "update":
                        update(msg["name"])
                        kafkaConsumer.commit()

                    elif msg["type"] == "new":
                        if msg["name"] is not None:
                            if msg["name"].find("投资")>0 or msg["name"].find("资产管理")>0 \
                                    or msg["name"].find("有限合伙")>0:
                                kafkaConsumer.commit()
                            elif len(msg["name"]) > 0:
                                insert(msg["name"])
                                kafkaConsumer.commit()
                            else:
                                kafkaConsumer.commit()
                                pass

                    else:
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
        break
