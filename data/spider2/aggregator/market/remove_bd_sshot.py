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
def change_sshots(apkname):
    global cnt
    apps_new = list(collection_android_market.find({"appmarket": {"$ne": 16020}, "apkname": apkname},{"screenshots":1, "apkname": 1, "appmarket":1}))
    if len(apps_new) ==0:
        logger.info("no other app")
        collection_android.update_one({"apkname": apkname},
                                      {"$set": {"screenshots": []}})
        cnt += 1
        #exit()
    else:
        for app in apps_new:
            if len(app["screenshots"]) > 0:
                logger.info("Change with appmarket: %s, %s", app["appmarket"], app["apkname"])
                collection_android.update_one({"apkname": apkname},
                                              {"$set": {"screenshots": app["screenshots"]}})
                cnt += 1
                break
    logger.info("total num : %s", cnt)



def start_run():
    global cnt
    while True:
        logger.info("check screen start...")
        #run(appmkt, WandoujiaCrawler(), "com.ctd.m3gd")
        apps = list(collection_android.find({"screenshotchecked": {"$ne": True}},{"screenshots":1, "apkname": 1}, limit=1000))
        for app in apps:
            sshots = app["screenshots"]
            apkname = app["apkname"]
            collection_android.update_one({"apkname": apkname},
                                          {"$set": {"screenshotchecked": True}})
            logger.info(apkname)
            if len(sshots) == 0:
                continue
            if sshots[0].find("bdimg") >= 0:
                logger.info("**********Change!")
                change_sshots(apkname)

        logger.info("finish")       #break

        if len(apps) == 0:
            break
        #break
    logger.info("total : %s", cnt)

if __name__ == "__main__":
    start_run()