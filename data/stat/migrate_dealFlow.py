# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config
import db

#logger
loghelper.init_logger("dealFlow_2_mongo", stream=True)
logger = loghelper.get_logger("dealFlow_2_mongo")

#mongo
mongo = db.connect_mongo()
collection = mongo.log.deal_log

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    dfs = conn.query("select * from deal_flow")
    for df in dfs:
        if df["status"] is None or df["dealId"] is None or (df["active"] is not None and df["active"] == 'N') \
            or df["createTime"] is None:
            continue
        item = {
            "type": 1,
            "deal_id": int(df["dealId"]),
            "status": int(df["status"]),
            "declineStatus": int(df.get("declineStatus",18010)),
            "createUser": int(df["createUser"]),
            "createTime": df["createTime"] - datetime.timedelta(hours=8)
        }
        # logger.info(item)

        item_m = collection.find_one({"deal_id": item["deal_id"], "status": item["status"], "declineStatus": item["declineStatus"]})
        if item_m is None:
            logger.info(item)
            collection.insert(item)

