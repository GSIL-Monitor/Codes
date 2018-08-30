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
import util
import db
import aggregator_util


source = 13050
def merge_company(company_key):

    match = aggregator_util.match_company(source, company_key)
    if match is None:
        return

    print 'merge .....'

    conn = db.conn_db()
    try:
        aggregator_util.insert_company(source, company_key, conn)
        aggregator_util.insert_member(source, company_key, conn)
        aggregator_util.insert_funding(source, company_key, conn)
        aggregator_util.insert_footprint(source, company_key, conn)
        aggregator_util.insert_job(source, company_key, conn)

        conn.commit()
    except Exception,e:
        logger.info(e)
    finally:
        conn.close()




if __name__ == '__main__':
    spider_name = "recruit_lagou"
    (logger, fromdb, mysqldb, kafka_producer, kafka_consumer) = aggregator_util.aggregator_init(spider_name)
    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
			                                         message.offset, message.key,
			                                         message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    company_key = msg["id"]
                    if type == "company":
                        merge_company(company_key)

                    # kafka_consumer.task_done(message)
                    # kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = aggregator_util.aggregator_init(spider_name)
