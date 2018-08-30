# -*- coding: utf-8 -*-
import os, sys, re, json, time
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

# scores = {"description":1, "rank":1, "createUser":2, "modifyUser":2}

DUPS = 0
dids = []

Mb = 0
Ma = 0
Mc = 0
Md = 0
Me = 0


def check_dup(arts, domain):
    logger.info(dids)
    global Mb
    global Ma
    global Mc
    global Md
    global Me
    conn = db.connect_torndb()
    varts = [a for a in arts if a["verify"] is not None and a["verify"] == 'Y' and
             conn.get("select * from company where id=%s and (active='Y' or active is null)", a["companyId"]) is not None]
    vcs =[]
    for vart in varts:
        if int(vart["companyId"]) not in vcs: vcs.append(int(vart["companyId"]))
    if len(varts) > 1:
        if len(vcs) == 1:
            pass
        else:
            # logger.info("more than 1 artifacts verified by domain: %s", domain)
            Ma += 1

            for va in varts:
                vac = conn.get("select * from company where id=%s and (active='Y' or active is null)", va["companyId"])
                logger.info("Checking : %s|%s|%s|%s|%s|%s", va["type"], va["domain"], va["name"],
                            vac["name"], vac["code"], vac["modifyUser"])
            logger.info("")
    elif len(varts) == 1:
        Mb += 1
        if varts[0]["companyId"] is not None:
            c = conn.get("select * from company where id=%s and (active='Y' or active is null)", varts[0]["companyId"])
            if c is None: Md += 1
            else:
                for a in arts:
                   if a["id"] != varts[0]["id"]:
                        # logger.info("Need remove %s|%s under companyId: %s since reserve under: %s",
                        #             a["id"], a["domain"], a["companyId"], c["id"])
                        Me += 1
                        dids.append(int(a["id"]))
                        # remove_dup(a["id"])

    else:
        # logger.info("No artifacts verified by domain: %s", domain)
        Mc += 1
    conn.close()



def fullFill(website):
    conn = db.connect_torndb()
    conn.update("update artifact set domain=%s where id=%s", website["domain"], website["id"])
    conn.close()


def remove_dup(ids):
    conn = db.connect_torndb()
    for id in ids:
        conn.update("update artifact set active='N', modifyUser=-540 where id=%s", id)
    conn.close()




if __name__ == "__main__":
    start = 0
    num = 0
    cid = 0
    while True:
        # global Mb
        # global Ma
        # global Mc
        # global Md
        # global Me
        connp = db.connect_torndb_proxy()
        artifacts = list(connp.query("select distinct domain from artifact where verify='Y' and "
                                    "(active='Y' or active is null)"))
        # artifacts = list(conn.query("select distinct domain from artifact where domain='915709839'"))

        for artifact in artifacts:
            domain = artifact["domain"]
            arts = connp.query("select * from artifact where (active is null or active='Y') and domain=%s", domain)
            if len(arts) > 1:
                #logger.info(member_rels)
                check_dup(arts, domain)
        connp.close()
        logger.info("%s>%s>%s>%s>%s", Ma, Mb, Mc, Md, Me)
        logger.info(dids)
        remove_dup(dids)
        dids = []

        logger.info("Total dups:  %s", DUPS)

        time.sleep(30*60)

