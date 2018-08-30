# -*- coding: utf-8 -*-
import os, sys, datetime, time
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper,db,extract,util,url_helper

#logger
loghelper.init_logger("hongdongxing_fix", stream=True)
logger = loghelper.get_logger("hongdongxing_fix")

TYPE = 60002
SOURCE =13804

if __name__ == "__main__":
    mongo = db.connect_mongo()
    items = mongo.article.news.find({"type":TYPE, "source":SOURCE})
    for item in items:
        contents = item["contents"]
        flag = True
        dcontents = []
        rank = 1
        for c in contents:
            if c.get("type") is None:
                flag = False
                break

            if c["type"] == "text":
                dc = {
                    "rank": rank,
                    "content": c["data"],
                    "image": "",
                    "image_src": "",
                }
            else:
                dc = {
                    "rank": rank,
                    "content": "",
                    "image": "",
                    "image_src": c["data"],
                }
            dcontents.append(dc)
            rank += 1

        if flag is False:
            continue

        logger.info(item["_id"])
        logger.info(dcontents)

        mongo.article.news.update_one({"_id":item["_id"]},{"$set":{"contents":dcontents}})

    mongo.close()