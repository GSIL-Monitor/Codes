# -*- coding: utf-8 -*-
import os, sys, time

import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper



#logger
loghelper.init_logger("remove_bd_sshot", stream=True)
logger = loghelper.get_logger("remove_bd_sshot")

#mongo
mongo = db.connect_mongo()

collection_android = mongo.market.android
collection_android_market = mongo.market.android_market

cnt = 0
def change_update(apkname, Appp):
    global cnt
    apps_new = list(collection_android_market.find({"appmarket": {"$in": [16010,16020,16030,16040]}, "apkname": apkname},{"apkname": 1, "appmarket":1, "link":1,"version":1,"updateDate":1}))
    if len(apps_new) ==0:
        logger.info("no other app")
        # collection_android.update_one({"apkname": apkname},
        #                               {"$set": {"screenshots": []}})
        return 1
    else:
        updateDate = None
        link = None
        for app in apps_new:
            if app["version"] == Appp["version"] and app["updateDate"] is not None and (updateDate is None or updateDate < app["updateDate"]) :
                logger.info("Change with appmarket: %s, %s", app["appmarket"], app["apkname"])
                link = app["link"]
                updateDate = app["updateDate"]
        if updateDate is not None and link is not None:
            collection_android.update_one({"apkname": apkname},{"$set": {"updateDate": updateDate, "link": link}})
            return 2
        else:
            collection_android.update_one({"apkname": apkname}, {"$set": {"updateDate": Appp["createTime"]}})
            return 3




def start_run():
    global cnt
    (num0,num1,num2,num3)=(0,0,0,0)
    while True:
        logger.info("check screen start...")
        #run(appmkt, WandoujiaCrawler(), "com.ctd.m3gd")
        apps = list(collection_android.find({"updateDateChecked": {"$ne": True},"apkname":{"$ne":None}},{"updateDate":1, "apkname": 1,"version":1,"createTime":1}, limit=1000))
        for app in apps:
            # logger.info(app["_id"])
            apkname = app["apkname"]
            # logger.info(apkname)
            ud = app["updateDate"]
            collection_android.update_one({"apkname": apkname},
                                          {"$set": {"screenshotchecked": True}})
            logger.info(apkname)
            if ud is not None:
                pass
            else:
                num0 += 1
                logger.info("change************")
                result = change_update(apkname, app)
                if result == 1: num1+=1
                if result == 2: num2+=1
                if result == 3: num3+=1

            collection_android.update_one({"apkname": apkname},
                                      {"$set": {"updateDateChecked": True}})
        logger.info("finish")
        logger.info("*******************total : %s/%s/%s/%s", num0, num1, num2, num3)#break
        logger.info("\n\n\n\n")
        # break
        if len(apps) == 0:
            break
        #break
    # logger.info("total : %s/%s/%s/%s", num0,num1,num2,num3)

if __name__ == "__main__":
    start_run()