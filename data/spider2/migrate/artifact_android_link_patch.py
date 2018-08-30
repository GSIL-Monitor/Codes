# -*- coding: utf-8 -*-
import os, sys
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, db

#logger
loghelper.init_logger("domain_2_beian", stream=True)
logger = loghelper.get_logger("domain_2_beian")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.android

if __name__ == '__main__':
    logger.info("Begin...")

    cnt = 0
    while True:
        conn = db.connect_torndb()
        items = conn.query("select * from artifact order by id limit %s, 10000", cnt)
        conn.close()
        if len(items) == 0:
            break
        for item in items:
            if item["type"]==4050 and item["active"]!='N' and (item["link"] is None or item["link"] == ""):
                logger.info("%s, %s", item["id"], item["domain"])
                app = collection.find_one({"apkname":item["domain"]})
                if app is not None:
                    conn = db.connect_torndb()
                    conn.update("update artifact set link=%s where id=%s", app["link"], item["id"])
                    conn.close()
                    #exit()
        #break
        cnt += 10000
        logger.info("cnt: %s", cnt)
    logger.info("End.")