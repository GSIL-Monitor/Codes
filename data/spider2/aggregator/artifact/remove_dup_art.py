# -*- coding: utf-8 -*-
import os, sys, re, json
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper
import db

#logger
loghelper.init_logger("remove_dup_member", stream=True)
logger = loghelper.get_logger("remove_dup_member")

scores = {"recommend":1}

DUPS = 0
Md = 0
Ma = 0
Mc = 0
aad = 0
def check_dup(artis):
    global DUPS

    linksmap = {}
    for art in artis:
        if art["domain"] is not None and art["domain"].strip() != "":
            linksmap.setdefault(art["domain"].strip(), []).append(art)


    dups =[]
    for domain in linksmap:
        if len(linksmap[domain]) <2: continue
        logger.info("%s, %s", domain, len(linksmap[domain]))
        maxscroe = 0; remainId = None; allIds = []
        for web in linksmap[domain]:
            allIds.append(web["id"])
            # logger.info("DUP: %s: %s /%s /%s", web["id"], web["domain"], web["createTime"], web["companyId"])
            score = len([column for column in scores if web[column] is not None and web[column] == 'Y'])
            logger.info("DUP: %s: %s /%s /%s -> %s", web["id"], web["domain"], web["createTime"], web["companyId"], score)
            if remainId is None: remainId=web["id"]; maxscroe = score
            elif score  > maxscroe: remainId=web["id"]
        logger.info("Remain: %s", remainId)
        dups.extend([id for id in allIds if id != remainId])
    if len(dups) > 0:
        logger.info("Remove: %s", dups)
        remove_dup(dups)
        DUPS += len(dups)


def fullFill(website):
    conn = db.connect_torndb()
    conn.update("update artifact set domain=%s where id=%s", website["domain"], website["id"])
    conn.close()


def remove_dup(dups):
    global aad
    conn = db.connect_torndb()
    for id in dups:
        aa = conn.get("select * from artifact where active='N' and id=%s", id)
        if aa is not None:
            logger.info("wrong :%s", id);aad+=1

        conn.update("update artifact set active='N', modifyUser=-541 where id=%s", id)

    conn.close()




if __name__ == "__main__":
    start = 0
    num = 0
    cid = 0
    while True:
        conn = db.connect_torndb()
        companies = list(conn.query("select domain,companyId,count(*) as cnt, name from artifact where "
                                    "(active is null or active='Y') and domain is not null and type in (4040,4050) "
                                    "group by domain,companyId having cnt>1"))
        if len(companies) == 0:
            break
        COMPANIES = []
        for company in companies:
            if company["companyId"] not in COMPANIES: COMPANIES.append(company["companyId"])

        logger.info("total companies: %s", len(COMPANIES))
        for cid in COMPANIES:
            # cid = company["companyId"]
            its = conn.query("select * from artifact where (active is null or active='Y') and type in (4040,4050) and companyId=%s", cid)
            if len(its) > 1:
                #logger.info(member_rels)
                check_dup(its)
        conn.close()
        break

    # logger.info("Missing domain: %s, missing link: %s - > %s", Md, Ma, Mc)
    logger.info("Total dups:  %s/%s", DUPS, aad)