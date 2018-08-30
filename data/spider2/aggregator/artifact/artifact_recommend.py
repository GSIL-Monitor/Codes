# -*- coding: utf-8 -*-
import os, sys
import datetime
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util

#logger
loghelper.init_logger("artifact_recommend", stream=True)
logger = loghelper.get_logger("artifact_recommend")

#
mongo = db.connect_mongo()
trend_itunes = mongo.trend.itunes
trend_android = mongo.trend.android
trend_alexa = mongo.trend.alexa
android = mongo.market.android
android_market = mongo.market.android_market
itunes = mongo.market.itunes

def get_related_app(company_name_like, company_id, type, artifact_ids):
    conn = db.connect_torndb()
    logger.info(artifact_ids)
    artifacts = conn.query("select * from artifact where type=%s and companyId=%s and (active is null or active='Y') and name like %s", type, company_id, company_name_like)
    for artifact in artifacts:
        id = artifact["id"]
        if id in artifact_ids:
            return artifact
    return None

def get_android_update_date(apkname):
    updateDate = None
    appmarkets = [16010,16020,16030,16040]
    for appmarket in appmarkets:
        item = android.find_one({"apkname":apkname, "appmarket":appmarket})
        if item is None:
            continue
        if item.get("updateDate") is None:
            continue
        if updateDate is None or item.get("updateDate") > updateDate:
            updateDate = item.get("updateDate")

    return updateDate


def get_recommend_artifact(company_id):
    artifact = None
    #itunes
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    company_name_like = '%'+company["name"]+'%'
    arts = conn.query("select * from artifact where type=4040 and companyId=%s and (active is null or active='Y')", company_id)
    conn.close()
    cnt = -1
    artifact_nocom = []
    for a in arts:
        trackId = a["domain"]
        if trackId is None or trackId.strip() == "":
            continue
        try:
            trackId = int(trackId)
        except:
            continue
        app = itunes.find_one({"trackId":trackId})
        if app is None:
            continue
        if not app.has_key("screenshotUrls") or len(app["screenshotUrls"]) == 0:
            continue
        currentVersionReleaseDate = app.get("currentVersionReleaseDate")
        if currentVersionReleaseDate is None:
            continue
        r_date = datetime.datetime.strptime(currentVersionReleaseDate,'%Y-%m-%dT%H:%M:%SZ')
        d_day = (datetime.datetime.now() - r_date).days
        if d_day > 180:
            continue

        item = trend_itunes.find_one({"trackId":trackId}, sort=[("date", pymongo.DESCENDING)], limit=1)
        _cnt = 0
        if item and item.has_key("comment"):
            _cnt = item["comment"]
        if _cnt == 0:
            artifact_nocom.append(a["id"])
        if _cnt > cnt:
            cnt = _cnt
            artifact = a

    if artifact is not None:
        if cnt == 0:
            logger.info("No comments, find related app")
            artifact_new = get_related_app(company_name_like, company_id, 4040, artifact_nocom)
            if artifact_new is not None:
                artifact = artifact_new
                logger.info("finded company_name_like app")
        logger.info("recommend artifact(itunes): %s,%s,%s", artifact["id"],artifact["name"],artifact["link"])
        return artifact

    #android
    conn = db.connect_torndb()
    arts = conn.query("select * from artifact where type=4050 and companyId=%s and (active is null or active='Y')", company_id)
    conn.close()
    cnt = 0
    for a in arts:
        apkname = a["domain"]
        if apkname is None or apkname.strip() == "":
            continue
        item = android.find_one({"apkname":apkname})
        if item is None:
            continue

        updateDate = get_android_update_date(apkname)
        if updateDate is None:
            continue
        d_day = (datetime.datetime.now() - updateDate).days
        if d_day > 180:
            continue

        item = trend_android.find_one({"appmarket":16010, "apkname":apkname}, sort=[("date", pymongo.DESCENDING)], limit=1)
        _cnt = 0
        if item is not None and item.has_key("download"):
            _cnt = item["download"]
        if _cnt > cnt:
            cnt = _cnt
            artifact = a

    if artifact is not None:
        logger.info("recommend artifact(android): %s,%s,%s", artifact["id"],artifact["name"],artifact["domain"])
        return artifact

    #website
    conn = db.connect_torndb()
    arts = conn.query("select * from artifact where type=4010 and companyId=%s and (active is null or active='Y')", company_id)
    conn.close()
    cnt = 100000000
    for a in arts:
        domain = a["domain"]
        if domain is None or domain.strip() == "":
            continue
        item = trend_alexa.find_one({"domain":domain}, sort=[("date", pymongo.DESCENDING)], limit=1)
        _cnt = 0
        if item is not None and item.has_key("country_rank"):
            _cnt = item["country_rank"]
        if _cnt > 0 and _cnt < cnt:
            cnt = _cnt
            artifact = a

    if artifact is not None:
        #判断是否在info->website中存在
        mongo = db.connect_mongo()
        website = mongo.info.website.find_one({"url":artifact["link"]})
        mongo.close()
        if website is not None and website["httpcode"] == 200:
            logger.info("recommend artifact(website): %s,%s,%s", artifact["id"],artifact["name"],artifact["link"])
            return artifact

    return None


if __name__ == "__main__":
    #重新计算recommend
    logger.info("Start...")
    if len(sys.argv) > 1:
        param = sys.argv[1]
        company_id = int(param)
        artifact = get_recommend_artifact(param)
        logger.info(artifact)
    else:
        start = 0
        while True:
            conn = db.connect_torndb()
            companies = list(conn.query("select * from company where (active is null or active='Y') "
                                        "order by id limit %s, 1000", start))
            if len(companies) == 0:
                break

            for company in companies:
                company_id = company["id"]
                recommend = conn.get("select * from artifact where companyId=%s and recommend='Y' and (active is null or active='Y') limit 1", company_id)
                if recommend is not None and company["modifyUser"] is not None:
                   continue

                #logger.info("recommemd for %s %s", company_id,company["name"])
                artifact = get_recommend_artifact(company_id)
                if artifact:
                    if recommend is None:
                        conn.update("update artifact set recommend='Y' where id=%s", artifact["id"])
                        logger.info("companyId: %s, recomend: %s", company_id, artifact["name"])
                    elif artifact["id"] != recommend["id"]:
                        conn.update("update artifact set recommend='Y' where id=%s", artifact["id"])
                        conn.update("update artifact set recommend=null where id=%s", recommend["id"])
                        logger.info("company code: %s, recomend: %s -> %s", company["code"], recommend["name"], artifact["name"])
                        #exit()
                else:
                    if recommend:
                        conn.update("update artifact set recommend=null where id=%s", recommend["id"])

            start += 1000
            #exit()
            conn.close()
    logger.info("End.")
