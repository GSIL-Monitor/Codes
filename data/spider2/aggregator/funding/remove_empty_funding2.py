# -*- coding: utf-8 -*-
#删除无金额和投资人的记录
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("remove_empty_funding", stream=True)
logger = loghelper.get_logger("remove_empty_funding")

def get_investors(fundingId):
    conn = db.connect_torndb()
    rels = conn.query("select * from funding_investor_rel where (active is null or active='Y') and fundingId=%s order by investorId", fundingId)
    investorIds = [int(rel["investorId"]) for rel in rels]
    conn.close()
    return investorIds



if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()

    fs = conn.query("select * from funding where active is null or active='Y' order by id")
    num = 0
    for f in fs:
        company = conn.get("select * from company where (active is null or active='Y') and id=%s", f["companyId"])
        if company is None:
            continue
        score = 0
        if f.has_key("fundingDate") and (f["fundingDate"] is not None and str(f["fundingDate"]).strip() != ""):
            score += 1
        if f.has_key("investment") and (f["investment"] is not None and str(f["investment"]).strip() != "" and f["investment"] != 0):
            score += 1
        if f.has_key("round") and (f["round"] is not None and str(f["round"]).strip() != "" and f["round"] != 0):
            score += 1
        if len(get_investors(f["id"])) > 0:
            score += 1
        if score <= 1:
            # logger.info("***********Company:%s|FundId:%s, %s/%s/%s", company["code"], f["id"], f["fundingDate"], f["investment"],f["round"])
            logger.info(company["code"])
            num += 1
    conn.close()
    logger.info("num: %s", num)
    logger.info("End.")