# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
import traceback
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import util
import db

#logger
loghelper.init_logger("parser_tianyancha", stream=True)
logger = loghelper.get_logger("parser_tianyancha")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

collection = mongo.crawler_v3.projectdata
collection.create_index([("source", pymongo.DESCENDING),
                         ("type", pymongo.DESCENDING),
                         ("key_int", pymongo.DESCENDING)], unique=False)
collection.create_index([("source", pymongo.DESCENDING),
                         ("type", pymongo.DESCENDING),
                         ("key", pymongo.DESCENDING)], unique=True)


SOURCE = 13090  #天眼查
TYPE = 36008    #工商


def from1970todate(l):
    if l is None:
        return None
    d = time.localtime(l/1000)
    return datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)

if __name__ == '__main__':
    skip = 0
    limit = 1000

    num = 0
    while True:
        cs = collection.find({"source":SOURCE, "type":TYPE}, skip=skip, limit=limit, sort=[("_id", pymongo.DESCENDING)])

        skip += limit
        finish = True
        for c in cs:
            #finish = False
            num += 1
            if c["content"] is None:
                continue
            if c["content"]["data"] is None:
                continue

            base = c["content"]["data"]["baseInfo"]
            if base.get("regStatus") is None:
                continue

            logger.info("%s: %s" % (num, c["key"]))

            #logger.info(base)
            conn = db.connect_torndb()
            source = conn.get("select * from source_gongshang_base where source=%s and sourceId=%s", SOURCE, str(c["key_int"]))
            if source is None:
                sql = "insert source_gongshang_base( \
                    source,sourceId, \
                    name,regCapital,industry,regInstitute,establishTime,base, \
                    regNumber,regStatus,fromTime,toTime,businessScope,regLocation, \
                    companyOrgType, legalPersonId, legalPersonName, \
                    createTime \
                    ) values( \
                    %s, %s, \
                    %s, %s, %s, %s, %s, %s, \
                    %s, %s, %s, %s, %s, %s, \
                    %s, %s, %s, \
                    now() \
                    )"
                conn.insert(sql,
                            SOURCE, str(c["key_int"]),
                            base["name"], base.get("regCapital"),base.get("industry"),base.get("regInstitute"),from1970todate(base.get("estiblishTime")),base.get("base"),
                            base.get("regNumber"),base.get("regStatus"),from1970todate(base.get("fromTime")),from1970todate(base.get("toTime")),base.get("businessScope"),base.get("regLocation"),
                            base.get("companyOrgType"), base.get("legalPersonId"), base.get("legalPersonName")
                            )
            conn.close()

        if finish:
            break