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
import desc_helper

#logger
loghelper.init_logger("find_member", stream=True)
logger = loghelper.get_logger("find_member")

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

def check_e(cid, rels):
    conn = db.connect_torndb()
    names = []
    newnames = []
    md = {}
    for rel in rels:
        member = conn.get("select * from member where id=%s", rel["memberId"])
        if (member["name"] is None or member["name"].strip() == "" or desc_helper.count_chinese(member["name"]) ==0) \
                and member["verify"] is None:
            # logger.info("Check english name: %s, position: %s, name: %s, company: %s",
            #             member["id"], rel["position"], member["name"], cid)
            names.append(member['name'])

        if md.has_key(rel["position"]) is True:
            md[rel["position"]].append(member["name"])
        else:
            md[rel["position"]] = [member["name"]]

    for p in md:
        if len(md[p])>1:
            for name in md[p]:
                if name in names:
                    newnames.append(name)


    conn.close()
    # return names
    return names, newnames

if __name__ == "__main__":
    start = 0
    num = 0
    num1 = 0
    cid = 0
    fp2 = open("mm.txt", "w")

    while True:
        conn = db.connect_torndb()
        companies = list(conn.query("select * from company where (active is null or active='Y') and id>%s "
                                    "order by id limit 10000",cid))
        if len(companies) == 0:
            break

        for company in companies:
            cid = company["id"]
            member_rels = conn.query("select * from company_member_rel where (active is null or active='Y') "
                                     "and companyId=%s and (type=5010 or type=5020)", cid)
            if len(member_rels) > 1:
                noe, node = check_e(cid, member_rels)
                if len(noe) < len(member_rels) and len(noe)>0:
                    num1 += 1
                    priority = 1
                    if len(node)>0:
                        num += 1
                        priority = 2
                        # logger.info(ns)
                        logger.info("Check english name %s|%s: names: %s, company: %s",
                                    len(node), len(member_rels), ":".join(node), cid)
                    c = conn.get("select * from company where id=%s", cid)
                    link = 'http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"]
                    line = "%s+++%s+++%s+++%s\n" % (c["code"], c["name"], link, priority)
                    fp2.write(line)

        conn.close()


        start += 1000
    fp2.close()
    logger.info("Total companies:  %s|%s", num,num1)