# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_report_source", stream=True)
logger = loghelper.get_logger("patch_report_source")


def main():
    mongo = db.connect_mongo()
    items = mongo.article.report.find({"source": None, "type":78001, "createTime":{"$gt": datetime.datetime(2018,6,20)}})
    for item in items:
        title = item["title"]
        if u"：" in title:
            strs = title.split(u"：", 1)
            source = strs[0]
            title = strs[1]
            logger.info(item)

            mongo.article.report.update_one({"_id": item["_id"]}, {"$set":{"title": title, "source": source}})
            # exit()
    mongo.close()


if __name__ == "__main__":
    main()