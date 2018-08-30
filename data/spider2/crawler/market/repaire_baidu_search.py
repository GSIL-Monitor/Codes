# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, db

#logger
loghelper.init_logger("repair_baidu", stream=True)
logger = loghelper.get_logger("repair_baidu")

#mongo
mongo = db.connect_mongo()
collection_search = mongo.market.baidu_search


if __name__ == "__main__":
    pipeline = [
        {"$group":{"_id":"$apkname","count":{"$sum":1}}},
        {"$match": {"count":{"$gt":1}}}
    ]
    items = list(collection_search.aggregate(pipeline))
    for item in items:
        apkname = item["_id"]
        logger.info(item)

        apps = list(collection_search.find({"apkname":apkname}))
        i = 0
        for app in apps:
            i += 1
            #logger.info(app)
            if i == 1:
                continue

            logger.info(app["_id"])
            collection_search.delete_one({"_id":app["_id"]})