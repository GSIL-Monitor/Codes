# -*- coding: utf-8 -*-
#删除无金额和投资人的记录
import os, sys
import time
from bson.objectid import ObjectId

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
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    collection_news = mongo.raw.qmp_rz
    strs = []

    items = list(collection_news.find({'postdata.lunci':{'$ne':"全部融资"}}))
    for item in items:

        if int(item["content"]["rzcount"])>=40:
            sstr = item["postdata"]["endTime"] + "+" + item["postdata"]["lunci"] + "+" +item["content"]["rzcount"]
            if sstr not in strs:
                strs.append(sstr)

    mongo.close()
    conn.close()
    print len(strs)
    for s in strs:
        print s
    # logger.info("End.")