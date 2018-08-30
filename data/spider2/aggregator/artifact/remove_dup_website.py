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

scores = {"description":1, "rank":1, "createUser":2, "modifyUser":2}

DUPS = 0
Md = 0
Ma = 0
Mc = 0
def check_dup(websites, pattern):
    global Md
    global Ma
    global Mc
    linksmap = {}
    for website in websites:
        if website["link"] is not None and website["link"].strip() != "":
            linksmap.setdefault(website["link"].strip(), []).append(website)
            if website["domain"] is None or website["domain"].strip() == "":
                flag, domain = url_helper.get_domain(website["link"])
                website["domain"] = domain
                logger.info("Website Missing domain for :%s , %s", website["id"], website["companyId"])
                fullFill(website)
                Md += 1
        else:
            logger.info("Website Missing link for :%s , %s", website["id"], website["companyId"])
            remove_dup([website["id"]])
            Ma += 1

    dups =[]
    for link in linksmap:
        if len(linksmap[link]) <2: continue
        maxscroe = 0; remainId = None; allIds = []
        Mc += 1
        for web in linksmap[link]:
            allIds.append(web["id"])
            logger.info("DUP: %s: %s /%s /%s", web["id"], web["link"], web["createTime"], web["companyId"])
            score = len([column for column in scores if web[column] is not None and str(web[column]).strip() != "" and str(web[column]).strip() != "0"])
            if remainId is None: remainId=web["id"]; maxscroe = score
            elif score  > maxscroe: remainId=web["id"]
        logger.info("Remain: %s", remainId)
        dups.extend([id for id in allIds if id != remainId])
    if len(dups) > 0:
        logger.info("Remove: %s", dups)
        remove_dup(dups)


def fullFill(website):
    conn = db.connect_torndb()
    conn.update("update artifact set domain=%s where id=%s", website["domain"], website["id"])
    conn.close()


def remove_dup(dups):
    conn = db.connect_torndb()
    for id in dups:
        conn.update("update artifact set active='N', modifyUser=-1 where id=%s", id)
    conn.close()




if __name__ == "__main__":
    start = 0
    num = 0
    cid = 0
    while True:
        conn = db.connect_torndb()
        companies = list(conn.query("select * from company where id>%s order by id limit 1000",cid))
        if len(companies) == 0:
            break

        for company in companies:
            cid = company["id"]
            websites = conn.query("select * from artifact where (active is null or active='Y') and type=4010 and companyId=%s", cid)
            if len(websites) > 1:
                #logger.info(member_rels)
                check_dup(websites, "ceo")
        conn.close()

    logger.info("Missing domain: %s, missing link: %s - > %s", Md, Ma, Mc)
    logger.info("Total dups:  %s", DUPS)