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
collection_task_serial = mongo['open-maintain'].task_serial
conn = db.connect_torndb()


def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("open_maintain", group_id="maintain",
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
                    taskid = msg['task_id']
                    mongo = db.connect_mongo()
                    collection = mongo['open-maintain'].task
                    collectionDefine = mongo['open-maintain'].task_origin_def
                    task = collection.find_one({'_id': ObjectId(taskid)})

                    sectionMap = {'funding': 'artifact', 'memberAndRecruitment': 'tag', 'artifact': 'news',
                                  'tag': 'industryAndComps',
                                  'basic': 'funding', 'news': 'memberAndRecruitment', 'industryAndComps': 'finish'}

                    if task.get('flow') == 'N':
                        logger.info("don't flow %s|%s", task['companyId'], task['section'])
                        collection.update_one({'_id': task['_id']}, {'$set': {'flowProcess': 1}})
                        kafkaConsumer.commit()
                    elif task.get('processStatus') != 1:
                        logger.info("can't  process dunt flow %s|%s", task['companyId'], task['section'])
                        collection.update_one({'_id': task['_id']}, {'$set': {'flowProcess': 1}})
                        kafkaConsumer.commit()
                    else:
                        if task['section'] == 'basic': #收到basic处理完成
                            origindefine = collectionDefine.find_one({'origin': task['origin']})

                            mt_generator.preAssignTask(origindefine['skipVerified'], task['companyId'], 'funding', -666,
                                                       task['origin'], task['priority'],taskSerialId=task['taskSerialId'],
                                                       parentTaskId=taskid,flow=task['flow'])

                        if collection.find_one(
                                {'companyId': task['companyId'], 'active': 'Y', "processStatus": {'$ne':1}}) is None:
                            logger.info('company:%s all task finished,set to active', task['companyId'])
                            conn.update('''update company set active='Y' where id=%s''', task['companyId'])
                            collection_task_serial.update_one({'_id': task['taskSerialId']}, {'$set': {'status':2}})

                        # if origindefine['skipVerified'] == 'N':
                        #     if sectionMap.has_key(task['section']):
                        #         section = sectionMap[task['section']].strip()
                        #     else:
                        #         logger.info('wrong section:%s', task['section'])
                        # else:
                        #     section = mt_generator.find_tobeverify_section(task['companyId'], section=task['section'])
                        #
                        # mt_generator.assignTask(task['companyId'], section, -666, task['origin'],
                        #                         priority=task['priority'], parentTaskId=taskid)

                        collection.update_one({'_id': task['_id']}, {'$set': {'flowProcess': 1}})
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
