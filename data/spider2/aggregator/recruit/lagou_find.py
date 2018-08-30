# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import pymongo
from bson.objectid import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
#logger
loghelper.init_logger("lagou_find", stream=True)
logger = loghelper.get_logger("lagou_find")


codes = [
    "bangongbao",
    "A0TOXHF1",
    "CESHI",
    "loukafei",
    "huanqiushuma",
    "shzhxcbzhjshfgfxgs",
    "Payssionpft",
    "xiaoerzhudian",
    "jinghaokeji",
    "aiyunche",
    "xiaolvwang",
    "hezhongzhengliang",
    "7749",
    "dakatai",
    "fengchuruanjian",
    "Swipyhkj",
    "saileshequ",
    "benzhishenghuokeji",
    "tuotuodanshenlvxing",
    "naikesitekeji",
    "haohuoban",
    "lingjuxiaoyuanwang",
    "91yueduwang",
    "lAIDsir33",
    "WE1",
    "6danyouxiwang",
    "gaixila",
    "17kaojiazhao1204",
    "jinliren",
    "jiaoquan",
    "zhaofaner71",
    "ZSQY",
    "bjshdldhchbxgs",
    "shidiandushu",
    "jkpdshzhb",
    "shuchao",
    "bjxlkj",
    "ruiyinqichejinrong",
    "junlintang",
    "lakeduo",
    "tuziwenhua",
    "guoding",
]

def find(code):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_job = mongo.job.job
    collection_company = mongo.job.company
    company = conn.get("select * from company where code=%s", code)
    if company is None:
        logger.info("code: %s not alive", code)
    else:
        companyId = company["id"]
        rels = conn.query("select * from company_recruitment_rel where companyId=%s", companyId)
        if len(rels) == 0:
            scs = conn.query("select * from source_company where companyId=%s and source=13050", companyId)
            # logger.info("code: %s not has lagou, in source: %s", code, len(scs))
            logger.info("%s############%s#########%s", code, 0, len(scs))
        else:
            # logger.info("code has %s lagou", len(rels))

            for rel in rels:
                sjobs = list(collection_job.find({"recruit_company_id": str(rel["jobCompanyId"])}))
                sc = collection_company.find_one({"_id": ObjectId(str(rel["jobCompanyId"]))})
                # logger.info("********%s(%s) has %s jobs", str(rel["jobCompanyId"]), sc["sourceUrl"],len(sjobs))
                logger.info("%s############%s#########%s", code, len(sjobs), sc["sourceUrl"])



    conn.close()
    mongo.close()



def insert(companyId,jobCompanyId):
    sql = "insert company_recruitment_rel(jobCompanyId,companyId,createTime,modifyTime) values(%s,%s,now(),now())"
    conn = db.connect_torndb()
    rel = conn.get("select * from company_recruitment_rel where jobCompanyId=%s and companyId=%s",jobCompanyId,companyId)
    if rel is None:
        conn.insert(sql, jobCompanyId,companyId)
    conn.close()
    pass

if __name__ == '__main__':
    logger.info("Begin...")
    for code in codes:
        find(code)
    logger.info("End.")