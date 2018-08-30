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
loghelper.init_logger("remove_dup_investor", stream=True)
logger = loghelper.get_logger("remove_dup_investor")

def get_investor(name):
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where name=%s and (active is null or active='Y')",name)
    conn.close()
    if investor is None:
        return None
    return investor["id"]


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    fp = open("dup_investor_v2.txt")
    # lines = fp.readlines()
    lines = []
    for line in lines:
        #logger.info(line)
        names = [name for name in line.strip().split("#") if name is not None and name.strip() != ""]
        if len(names) < 2:
            continue
        for name in names:
            logger.info(name)

        investorIds = [get_investor(name) for name in names if get_investor(name) is not None]
        investorIds_str = [str(investorId) for investorId in investorIds]

        if len(investorIds) < 2:
            logger.info("Names: %s only match %s investors: %s", ":".join(names), len(investorIds), ":".join(investorIds_str))
            continue

        ts = conn.query("select * from audit_reaggregate_investor where type=1 and beforeProcess like %s",
                        "%" + str(investorIds[0]) + "%")
        exists = False
        for t in ts:
            find = True
            for investorId in investorIds:
                if t["beforeProcess"].find(str(investorId)) == -1:
                    find = False
                    break
            if find is True:
                logger.info("************Find same request databaseid: %s", t["id"])
                exists = True
                break

        if exists is False:
            logger.info("Insert %s", ":".join(investorIds_str))
            conn.insert("insert audit_reaggregate_investor(type,beforeProcess,createTime,processStatus) "
                    "values(1,%s,now(),0)", " ".join(investorIds_str))
        #break
    conn.close()

    audits = conn.query("select * from audit_reaggregate_investor where processStatus=2")
    for audit in audits:
        investorIds = audit["beforeProcess"].replace(","," ").split()
        sinvestorId = audit["afterProcess"]
        for investorId in investorIds:
            if investorId == sinvestorId or sinvestorId is None or sinvestorId == "":
                continue
            logger.info("Update old:%s -> new:%s",investorId,sinvestorId)
            conn.update("update source_investor set investorId=%s where investorId=%s", sinvestorId,investorId)
    conn.close()
    logger.info("End.")