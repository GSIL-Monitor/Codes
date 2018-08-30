# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db

#logger
loghelper.init_logger("gongshang_2_mongo", stream=True)
logger = loghelper.get_logger("gongshang_2_mongo")

#mongo
mongo = db.connect_mongo()
collection = mongo.info.gongshang


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    gs = conn.query("select * from source_gongshang_base")
    for g in gs:
        if g["name"] is None:
            continue
        logger.info(g["name"])
        g.pop("id")
        g.pop("gongshangBaseId")
        g.pop("source")
        g.pop("sourceId")
        g.pop("verify")

        gongshang = collection.find_one({"name":g["name"]})
        if gongshang is None:
            if g["modifyTime"] is None:
                g["modifyTime"] = g["createTime"]
            collection.insert(g)
        #break


    conn.close()

    logger.info("End.")