# -*- coding: utf-8 -*-
import os, sys, re, json
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util
import db

#logger
loghelper.init_logger("remove_dup_member", stream=True)
logger = loghelper.get_logger("remove_dup_member")

scores = {"description":1, "work":1, "education":1, "photo":1, "email":0.5}

DUPS = 0
def check_dup(rels, pattern):
    dups =[]
    for rel in rels:
        if rel["position"] is None or rel["position"].strip() == "":
            continue
        if re.search(pattern, rel["position"], re.I):
            dups.append(rel)

    if len(dups) <= 1:
        return
    else:
        logger.info("Find dups")
        for dup in dups:
            logger.info(json.dumps(dup, ensure_ascii=False, cls=util.CJsonEncoder))
        remove_dup(dups)

def remove_dup(rels):
    global DUPS
    id_remain = None
    max = 0
    companyId = None
    conn = db.connect_torndb()
    for rel in rels:
        if companyId is None:
            companyId = rel["companyId"]
        if id_remain is None:
            id_remain = rel["id"]
        member = conn.get("select * from member where id=%s", rel["memberId"])
        logger.info("Check id: %s, position: %s, name: %s", rel["id"], rel["position"], member["name"])
        logger.info(json.dumps(member, ensure_ascii=False, cls=util.CJsonEncoder))
        score = 0
        for column in scores:
            if member[column] is not None and member[column].strip() != "":
                score += scores[column]
        if score > max:
            max = score
            id_remain = rel["id"]

    logger.info("Remain id : %s", id_remain)
    conn.update("update company_member_rel set active='N' where companyId=%s and id!=%s", companyId, id_remain)
    conn.close()
    DUPS += 1



if __name__ == "__main__":
    start = 0
    num = 0
    cid = 0
    while True:
        conn = db.connect_torndb()
        companies = list(conn.query("select * from company where (active is null or active='Y') and id>%s order by id limit 1000",cid))
        if len(companies) == 0:
            break

        for company in companies:
            cid = company["id"]
            member_rels = conn.query("select * from company_member_rel where (active is null or active='Y') and companyId=%s and (type=5010 or type=5020)", cid)
            if len(member_rels) > 1:
                #logger.info(member_rels)
                check_dup(member_rels, "ceo")
                check_dup(member_rels, "cto")
                check_dup(member_rels, "coo")
        conn.close()


        start += 1000

    logger.info("Total dups:  %s", DUPS)