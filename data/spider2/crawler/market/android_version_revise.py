# -*- coding: utf-8 -*-
import os, sys
import pymongo
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper


#logger
loghelper.init_logger("acr", stream=True)
logger = loghelper.get_logger("acr")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.android
android_market = mongo.market.android_market

def chooseApp(apkname):

   apps = list(android_market.find({"apkname":apkname, "appmarket":{"$in":[16010,16020,16030,16040]}}))
   for app in apps:
       if app.get("version") is not None:
           if app["version"].startswith("V") or app["version"].find("ersion ")>=0:
               nv = app["version"].replace("V", "").replace("ersion ","")

               logger.info("%s/16030 -> %s/%s", app["apkname"], app["version"], nv)
               # nv = item["version"].replace("&nbsp;","").strip()
               android_market.update({"_id": app["_id"]}, {'$set':{"version":nv}})

               flag = False

               nitem = android_market.find_one({"_id": app["_id"]})
               if nitem.has_key("histories"):
                    his = nitem["histories"]
                    for hi in his:
                       if hi.get("version") is not None:
                           if hi["version"].startswith("V") or hi["version"].find("ersion ")>=0:
                               nv = hi["version"].replace("V", "").replace("ersion ","")
                               hi["version"] = nv
                               flag = True
                    if flag is True:
                        android_market.update_one({"_id": app["_id"]}, {"$set": {"histories": his}})



   # return None

if __name__ == '__main__':
    logger.info("Begin...")
    cnt = 0
    n1 = 0
    while True:
        # com.hexin.zhanghu
        # items = list(collection.find({"apkname":"com.itjuzi.app"}))
        items = list(collection.find(projection={'histories': False}).sort([("_id",pymongo.ASCENDING)]).skip(cnt).limit(10000))
        if len(items) == 0:
            break
        for item in items:
            if item.get("version") is not None:
                if item["version"].startswith("V") or item["version"].find("ersion ")>=0:
                    nv = item["version"].replace("V", "").replace("ersion ","")
                    n1 += 1

                    logger.info("%s -> %s/%s", item["apkname"], item["version"],nv)
                    # nv = item["version"].replace("V", "").replace("ersion ","")
                    collection.update({"_id":item["_id"]},{'$set':{"version":nv}})
                    chooseApp(item["apkname"])
            flag = False
            nitem = collection.find_one({"_id": item["_id"]})
            if nitem.has_key("histories"):
                his = nitem["histories"]
                for hi in his:
                    if hi.get("version") is not None:
                        if hi["version"].startswith("V") or hi["version"].find("ersion ")>=0:
                            nv = hi["version"].replace("V", "").replace("ersion ","")
                            hi["version"] =  nv
                            flag = True
                if flag is True:
                    collection.update_one({"_id": item["_id"]},{"$set":{"histories":his}})

                    #break
        # break
        cnt += 10000
        logger.info("********************cnt: %s/%s", cnt,n1)
    logger.info("End.")