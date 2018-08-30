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


if __name__ == '__main__':
    logger.info("Begin...")
    num = 0
    # conn = db.connect_torndb()
    # investors = conn.query("select * from investor where (active is null or active='Y')")
    # fp = open("investor.txt", "w")
    # for investor in investors:
    #     desc = None
    #     if conn.get("select * from funding_investor_rel where investorId=%s limit 1", investor["id"]) is not None:
    #
    #         if investor["description"] is not None:
    #             desc = investor["description"].replace("\n"," ").replace("\b", " ").replace("\r", " ").replace(" ","")
    #             # " ".join(investor["description"].split())
    #         num += 1
    #         line = "%s####%s####%s####%s\n" %(investor["id"],investor["name"],desc,investor["website"])
    #         fp.write(line)
    #
    # fp.close()
    # conn.close()

    mongo = db.connect_mongo()
    collection_org = mongo.fellowPlus.org
    fp = open("investor_f.txt", "w")
    orgs = list(collection_org.find({}))
    for org in orgs:
        if org.has_key("org_name") is False or org["org_name"] is None or org["org_name"].strip() == "":continue
        num += 1
        line = "%s\n" %(org["org_name"])
        fp.write(line)
    fp.close()
    mongo.close()
    logger.info("num: %s", num)
    logger.info("End.")