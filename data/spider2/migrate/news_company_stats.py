# -*- coding: utf-8 -*-
import os, sys
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, db

#logger
loghelper.init_logger("news_company_stats", stream=True)
logger = loghelper.get_logger("news_company_stats")

#mongo
mongo = db.connect_mongo()
collection = mongo.article.news



if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     exit()
    # source = int(sys.argv[1])
    cs = set()
    items = list(collection.find({"source":{"$in":[13020,13800,13803,13801,13806,13813,13821]}}, projection={'companyId': True, 'companyIds': True}))
    for item in items:
        if item.get("companyId") is not None:
            cs.add(item.get("companyId"))
        if item.get("companyIds") is not None:
            for c in item.get("companyIds"):
                cs.add(c)

    print "count: %s" % len(cs)