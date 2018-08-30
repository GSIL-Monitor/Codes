# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
from lxml import html
from pyquery import PyQuery as pq

# logger
loghelper.init_logger("lagou_round_patch", stream=True)
logger = loghelper.get_logger("lagou_round_patch")


def run():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    result = conn.query('''select sc.id,sc.sourceid
                  from source_company sc
                  where (active='Y' or active is null) and createtime>='2018-3-12'
                  and source=13050 and roundDesc is null limit 1000
                  ''')

    cnt = 0
    for sc in result:
        cnt += 1
        raw = mongo.raw.projectdata.find_one({'source': 13050, "type": 36001, 'key': str(sc['sourceid'])})
        d = pq(html.fromstring(raw['content'].decode("utf-8")))
        round = d('#container_right .process + span').text()
        logger.info('cnt:%s|sourceid:%s %s', cnt, sc['sourceid'], round)
        conn.update('''update source_company set roundDesc=%s,modifyTime=now()  where id=%s''', round, sc['id'])
    conn.close()
    mongo.close()


if __name__ == "__main__":
    while True:
        logger.info('begin..')
        run()
        logger.info('end..')
        time.sleep(60)
