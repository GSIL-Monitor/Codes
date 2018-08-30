# -*- coding: utf-8 -*-
import os, sys
import datetime, json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import config

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import db

#logger
loghelper.init_logger("fellowPlus_investor_map", stream=True)
logger = loghelper.get_logger("fellowPlus_investor_map")

from pymongo import MongoClient
import gridfs
import pymongo
mongo = db.connect_mongo()
collection_investor = mongo.fellowplus.investor

imgfs = gridfs.GridFS(mongo.gridfs)

def process():
    (num0, num1, num2, num3) = (0,0,0,0)
    users = collection_investor.find({})
    conn = db.connect_torndb()
    for user in users:
        num0 += 1
        name = user["name"]
        if name is not None and name.strip() != "":
            users_mq = conn.query("select * from user where username=%s and (active='Y' or active is null)", name)
            if len(users_mq) > 0:
                num1 += 1
                collection_investor.update_one({"_id": user["_id"]}, {'$set': {"userId": [int(um["id"]) for um in users_mq]}})
            for um in users_mq:
                rel = conn.get("select * from user_organization_rel where userId=%s and (active='Y' or active is null)"
                               "limit 1", um["id"])
                if rel is not None and rel["organizationId"] is not None:
                    org_mq = conn.get("select * from organization where id=%s", rel["organizationId"])
                    if org_mq is not None:
                        if org_mq["name"] is not None and org_mq["name"].strip() != "" and \
                           user["org_name"] is not None and user["org_name"].strip() != "" and \
                           (org_mq["name"] == user["org_name"] or org_mq["name"] in user["org_name"] or
                            user["org_name"] in org_mq["name"]):
                            logger.info("%s *******> %s", user["org_name"], org_mq["name"])
                            num2 += 1
                            break
        pass

    conn.close()
    logger.info("%s/%s/%s", num0, num1, num2)

if __name__ == '__main__':
    process()

