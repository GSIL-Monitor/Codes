# -*- coding: utf-8 -*-
import datetime
import os, sys
import time,json
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
import name_helper
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/company/itjuzi'))
import parser_db_util
import itjuzi_helper

# corporateId not companyId
# funding createUser =-557
# if have 2 or more corporates do not do anything
#

#logger
loghelper.init_logger("patch_card_ii", stream=True)
logger = loghelper.get_logger("patch_card_ii")

def check_investorname():
    n = 0; n1 = 0; n2 = 0; n3 = 0; n4 = 0; n5 = 0
    fp = open("cardi.txt")
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    lines = fp.readlines()
    for line in lines:
            xids = []
            invs = line.strip().split(">>>")
            n += 1
            if len(invs) != 3:
                logger.info(invs)
                logger.info("here wrong 1")
                exit()

            investorId = int(invs[0])
            corporateIds = invs[1][1:-1].split(", ")
            iname = invs[2]
            if len(corporateIds) != 1:
                n1 += 1

            corporateId = corporateIds[0]


            fundings = conn.query("select * from funding where (active is null or active='Y') and corporateId=%s",
                                  corporateId)
            for f in fundings:
                frels = conn.query("select * from funding_investor_rel where (active is null or active='Y') and "
                                   "fundingId=%s", f["id"])
                for f in frels:
                    if int(f["investorId"]) not in xids:
                        xids.append(int(f["investorId"]))

            if investorId in xids:
                n2 += 1

            else:
                n3 += 1
                nids = []
                fs = conn.query("select * from funding  where (active is null or active='Y') and investors is not null  and investors != '' " 
                                "and corporateId=%s", corporateId)
                if len(fs) > 0:
                    n5 += 1
                for f in fs:
                    # logger.info("%s",f["id"])
                    # if f["investors"].strip() == "": continue
                    investors = eval(f["investors"].replace("null", "\"abcnull\""))
                    for investor in investors:
                        if investor["type"] == "text":

                            if investor["text"] in ["、", ",", "，", ", ", "-"]: continue

                            invest = investor["text"].replace("、", ",").replace(",", ",").replace("，", ",").replace( ", ", ",").replace("-", ",")
                            invss = invest.split(",")
                            for inv in invss:
                                # n2 += 1
                                invv = inv.replace("领投", "").replace("中国", "").replace("跟投", "").replace("参投","").replace("和", "")
                                if invv.strip() == "": continue

                                investora = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                                                     "ia.investorId=i.id where ia.name=%s and "
                                                     "(i.active is null or i.active='Y') and "
                                                     "(ia.active is null or ia.active='Y') limit 1", invv)
                                if investora is None:
                                    continue
                                else:
                                    if int(investora["id"]) not in nids:
                                        nids.append(int(investora["id"]))

                                    logger.info("%s-%s-%s-%s", invv, investora["id"], f["id"], f["investorsRaw"])

                if investorId in nids:
                    company = conn.get("select * from company where (active is null or active='Y') and corporateId=%s "
                                       "limit 1", corporateId)
                    if company is not None:
                        n4 += 1
                        logger.info("\n\n\n")
                        # logger.info(corporateId)
                        logger.info("find * find here!!!!!!!!! %s/%s", company["code"], iname)
                        logger.info("\n\n\n")


    conn.close()
    mongo.close()
    fp.close()
    logger.info("%s/%s/%s/%s/%s/%s", n, n1, n2, n3, n4, n5)



if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding card start ")
    # check_investor(114, "5b45a8f7deb47174c8a818e0")
    check_investorname()
    logger.info("End.")