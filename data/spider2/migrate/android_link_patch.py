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
android_market = mongo.market.android_market

def chooseApp(apkname):
   app = android_market.find_one({"apkname":apkname, "appmarket":16040})
   if app is not None:
       return app
   app = android_market.find_one({"apkname":apkname, "appmarket":16030})
   if app is not None:
       return app
   app = android_market.find_one({"apkname":apkname, "appmarket":16010})
   if app is not None:
       return app
   app = android_market.find_one({"apkname":apkname, "appmarket":16020})
   if app is not None:
       return app

   return None

if __name__ == '__main__':
    logger.info("Begin...")
    cnt = 0
    while True:
        items = list(collection.find(projection={'histories': False}).sort([("_id",pymongo.ASCENDING)]).skip(cnt).limit(10000))
        if len(items) == 0:
            break
        for item in items:
            if item.get("link") is None:
                logger.info(item["apkname"])
                app = chooseApp(item["apkname"])
                if app is not None:
                    #logger.info(app)
                    collection.update({"_id":item["_id"]},{'$set':{"link":app["link"]}})
                    #break
        #break
        cnt += 10000
        logger.info("cnt: %s", cnt)
    logger.info("End.")