# -*- coding: utf-8 -*-
# 处理funding表 investor和 funding_investor_rel不一致的情况
import os, sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("news_domain_patch", stream=True)
logger = loghelper.get_logger("news_domain_patch")


def main():
    mongo = db.connect_mongo()
    items = list(mongo.article.news.find({"type":61000, "modifyUser":{"$exists":True}}).sort("_id", -1))
    for item in items:
        logger.info("_id: %s", item["_id"])
        mongo.article.news.update({"_id": item["_id"]}, {"$set":{"domain":"xiniudata.com"}})
        # exit(0)
    mongo.close()


if __name__ == "__main__":
    main()