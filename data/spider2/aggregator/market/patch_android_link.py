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
import url_helper



#logger
loghelper.init_logger("remove_bd_sshot", stream=True)
logger = loghelper.get_logger("remove_bd_sshot")

#mongo
mongo = db.connect_mongo()

collection_android = mongo.market.android
collection_itunes= mongo.market.itunes

collection_android_market = mongo.market.android_market


cnt = 0

def copy_from_itunes(app, artifactId):
    conn = db.connect_torndb()
    if app.has_key("description"):
        sql = "update artifact set name=%s, description=%s, link=%s, domain=%s, modifyTime=now(), type=4040 where id=%s"
        conn.update(sql, app["trackName"], app["description"], app["trackViewUrl"], app["trackId"], artifactId)
    else:
        sql = "update artifact set name=%s, link=%s, domain=%s, modifyTime=now(), type=4040 where id=%s"
        conn.update(sql, app["trackName"], app["trackViewUrl"], app["trackId"], artifactId)
    conn.close()

def copy_from_android(app, artifactId):
    conn = db.connect_torndb()
    sql = "update artifact set name=%s, description=%s, domain=%s, link=%s, modifyTime=now(), type=4050 where id=%s"
    conn.update(sql, app["name"], app["description"], app["apkname"], app["link"], artifactId)
    conn.close()



def find(artifact):
    # app = collection_android.find_one({"apkname": apkname})
    # if app is not None:
    #     # logger.info("find domain:%s app: link:%s", apkname, app["link"])
    #     return app["link"]
    # else:
    #     logger.info("cannot find domain:%s ", apkname)
    #     return None
    apkname = None

    (apptype, appmarket, appid) = url_helper.get_market(artifact["link"])
    # Get apkname of baidu and 360 from android market
    if apptype not in [4040,4050]:
        return None

    if appmarket == 16010 or appmarket == 16020:
        android_app = collection_android_market.find_one({"appmarket": appmarket, "key_int": appid})
        if android_app:
            apkname = android_app["apkname"]
    else:
        apkname = appid

    app = None

    if apkname is not None:
        if apptype == 4040:
            app = collection_itunes.find_one({"trackId": appid})
        else:
            app = collection_android.find_one({"apkname": apkname})

    if app is None:
        return None
    else:
        return app

def find2(artifact):
    if artifact["type"] == 4040:
        app = collection_android.find_one({"apkname": artifact["domain"]})
    else:
        app = collection_itunes.find_one({"trackId": artifact["domain"]})
    if app is not None:
        # logger.info("find domain:%s app: link:%s", apkname, app["link"])
        return app
    else:
        logger.info("cannot find domain:%s ", artifact["domain"])
        return None


def start_run():
    global cnt
    c1 = 0; c2 = 0; c3 = 0
    conn = db.connect_torndb()
    ans = conn.query("select id,domain,link,type from artifact where domain is null and type in (4040,4050) and (active is null or active='Y') order by id desc")
    for an in ans:

        c1 += 1
        link = an["link"]
        # link =find(an["domain"])
        if link is None or link.strip() == "":
            logger.info("id : %s", an["id"])
            conn.update("update artifact set active='N' where id=%s", an["id"])
        else:
            apppp = find(an)
            if apppp is None:
                c2 += 1
                # logger.info("id : %s", an["id"])
                conn.update("update artifact set link=null,active='N' where id=%s", an["id"])
            else:
                logger.info("id : %s", an["id"])
                if apppp.has_key("trackName") is True:
                    copy_from_itunes(apppp, an["id"])
                else:
                    copy_from_android(apppp, an["id"])
                c3 += 1

    # conn.close()
    logger.info("%s/%s/%s", c1, c2,c3)
    # logger.info("total : %s", len(ans))
    ans = conn.query("select id,domain,link,type from artifact where link is null and type in (4040,4050) and (active is null or active='Y') order by id desc")
    for an in ans:
        c1 += 1
        domain = an["domain"]
        # link =find(an["domain"])
        if domain is None or domain.strip() == "":
            c2+= 1
            logger.info("id : %s", an["id"])
            conn.update("update artifact set active='N' where id=%s", an["id"])
        else:
            apppp = find2(an)
            if apppp is None:
                conn.update("update artifact set active='N' where id=%s", an["id"])
                c2+= 1
            else:
                c3+= 1

    conn.close()
    logger.info("%s/%s/%s", c1, c2, c3)
if __name__ == "__main__":
    start_run()