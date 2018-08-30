# -*- coding: utf-8 -*-
import os, sys
import time
import json
from kafka import (KafkaClient, SimpleProducer)
import find_company

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_util


#logger
loghelper.init_logger("company_aggregator_new", stream=True)
logger = loghelper.get_logger("company_aggregator_new")



def set_sourcecompany_processstatus(source_company_id):
    conn = db.connect_torndb()
    conn.update("update source_company set processStatus=2 where id=%s", source_company_id)
    conn.close()


def aggregator(source_company, test=False):
    pass



if __name__ == '__main__':

    while True:
        logger.info("Company aggregator mongo start...")
        conn = db.connect_torndb()
        scs = list(conn.query("select * from source_company where processStatus=1 and (active is null or active='Y') and source!=13002 order by id desc limit 100"))
        # scs = list(conn.query("select * from source_company where id=31098"))
        conn.close()

        for sc in scs:
            aggregator(sc)
            # break

        logger.info("Company aggregator end.")

        # break
        if len(scs) == 0:
            time.sleep(60)