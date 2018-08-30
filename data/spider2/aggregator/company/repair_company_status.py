# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

import company_aggregator_baseinfo

#logger
loghelper.init_logger("repair_company_status", stream=True)
logger = loghelper.get_logger("repair_company_status")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select id,code,name from company")
    conn.close()

    for c in cs:
        logger.info("id: %s, code: %s, name: %s", c["id"], c["code"], c["name"])
        company_aggregator_baseinfo.patch_company_status(c["id"])


    logger.info("End.")