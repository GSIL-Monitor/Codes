# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db

#logger
loghelper.init_logger("repair_dup_code", stream=True)
logger = loghelper.get_logger("repair_dup_code")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select code,count(*) cnt from company group by code having cnt > 1")

    for c in cs:
        logger.info("%s",c["code"])
        companies = conn.query("select * from company where code=%s order by active desc",c["code"])
        cnt = 0
        for company in companies:
            cnt += 1
            if cnt == 1:
                continue
            code = "%sn%d" % (c["code"],cnt)
            logger.info("id=%s, name=%s, new code=%s", company["id"], company["name"], code)
            conn.update("update company set code=%s where id=%s", code, company["id"])
    conn.close()

    logger.info("End.")