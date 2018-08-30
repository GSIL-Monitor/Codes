# -*- coding: utf-8 -*-
import os, sys
import pymongo
import traceback
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

#logger
loghelper.init_logger("set_artifact_rank", stream=True)
logger = loghelper.get_logger("set_artifact_rank")

#
mongo = db.connect_mongo()
trend_itunes = mongo.trend.itunes
trend_android = mongo.trend.android
trend_alexa = mongo.trend.alexa

MAX = 2147483647

def set_artifact_rank(art):
    if art["domain"] is None or art["domain"].strip() == "":
        if art["type"] == 4010:
            conn = db.connect_torndb()
            conn.update("update artifact set rank=%s where id=%s", MAX, art["id"])
            conn.close()
        return

    conn = db.connect_torndb()
    try:
        if art["type"] == 4010:
            item = trend_alexa.find_one({"domain":art["domain"].strip()}, sort=[("date", pymongo.DESCENDING)], limit=1)
            if item and item.get("country_rank") is not None:
                rank = item["country_rank"]
                if rank == 0:
                    rank = MAX
                conn.update("update artifact set rank=%s where id=%s", rank, art["id"])
                logger.info("artifactId: %s", art["id"])
            else:
                conn.update("update artifact set rank=%s where id=%s", MAX, art["id"])

            website = mongo.info.website.find_one({"url":art["link"]})
            if website is not None and website["httpcode"] == 200:
                title = website["title"]
                if title is None or title.strip() == "":
                    title = art["name"]
                desc = website["description"]
                if desc is None or desc.strip() == "":
                    desc = art["description"]

                if title is not None and desc is not None:
                    if art["name"] != title or art["description"] != desc:
                        logger.info("title: %s", title)
                        logger.info("description: %s", desc)
                        if len(title) < 200:
                            try:
                                conn.update("update artifact set name=%s, description=%s where id=%s",
                                            title,
                                            desc,
                                            art["id"])
                            except:
                                pass
        elif art["type"] == 4040:
            try:
                item = trend_itunes.find_one({"trackId":int(art["domain"])}, sort=[("date", pymongo.DESCENDING)], limit=1)
                if item and item.get("comment") is not None:
                    conn.update("update artifact set rank=%s "
                                "where id=%s",
                                item["comment"],
                                art["id"])
                    logger.info("artifactId: %s", art["id"])

                itunes = mongo.market.itunes.find_one({"trackId":int(art["domain"])})
                if itunes is not None:
                    name = itunes.get("trackName")
                    desc = itunes.get("description")
                    if name is not None and desc is not None:
                        if art["name"] != name or art["description"] != desc:
                            logger.info("name: %s", name)
                            logger.info("description: %s", desc)
                            if len(name) < 200:
                                try:
                                    conn.update("update artifact set name=%s, description=%s where id=%s",
                                                name,
                                                desc,
                                                art["id"])
                                except:
                                    pass
                    currentVersionReleaseDate = itunes.get("currentVersionReleaseDate")
                    if currentVersionReleaseDate is None:
                        currentVersionReleaseDate = itunes.get("releaseDate")
                    if currentVersionReleaseDate is None:
                        currentVersionReleaseDate = itunes.get("createTime")
                    else:
                        currentVersionReleaseDate = currentVersionReleaseDate.replace("T", " ").replace("Z","")
                    conn.update("update artifact set releaseDate=%s where id=%s",
                                currentVersionReleaseDate, art["id"])
                    logger.info("currentVersionReleaseDate: %s", currentVersionReleaseDate)
            except:
                pass
        elif art["type"] == 4050:
            item1 = trend_android.find_one({"appmarket":16010, "apkname":art["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
            item2 = trend_android.find_one({"appmarket":16020, "apkname":art["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
            item3 = trend_android.find_one({"appmarket":16030, "apkname":art["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
            item4 = trend_android.find_one({"appmarket":16040, "apkname":art["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
            download = 0
            if item1 and item1.get("download") is not None:
                download += item1["download"]
            if item2 and item2.get("download") is not None:
                download += item2["download"]
            if item3 and item3.get("download") is not None:
                download += item3["download"]
            if item4 and item4.get("download") is not None:
                download += item4["download"]
            logger.info("download: %s", download)
            logger.info("artifactId: %s", art["id"])
            conn.update("update artifact set rank=%s where id=%s", download, art["id"])

            android = mongo.market.android.find_one({"apkname":art["domain"]})
            if android is not None:
                name = android.get("name")
                desc = android.get("description")
                if name is not None and desc is not None:
                    if art["name"] != name or art["description"] != desc:
                        logger.info("name: %s", name)
                        logger.info("description: %s", desc)
                        if len(name) < 200:
                            try:
                                conn.update("update artifact set name=%s, description=%s where id=%s",
                                            name,
                                            desc,
                                            art["id"])
                            except:
                                pass
                currentVersionReleaseDate = android.get("updateDate")
                if currentVersionReleaseDate is None:
                    currentVersionReleaseDate = android.get("createTime")
                conn.update("update artifact set releaseDate=%s where id=%s",
                            currentVersionReleaseDate, art["id"])
                logger.info("currentVersionReleaseDate: %s", currentVersionReleaseDate)
    except:
        traceback.print_exc()
        exit()
    conn.close()


if __name__ == "__main__":
    # 定期重算 一周一次
    logger.info("Start...")
    start = 0
    #start = 105101
    while True:
        conn = db.connect_torndb()
        arts = list(conn.query("select * from artifact where (active is null or active='Y') and id>%s order by id limit 1000", start))
        #arts = list(conn.query("select * from artifact where companyId=881 and (active is null or active='Y') and id>%s order by id limit 1000", start))
        conn.close()
        if len(arts) == 0:
            break
        for art in arts:
            if art["id"] > start:
                start = art["id"]
            set_artifact_rank(art)

    conn = db.connect_torndb()
    arts = conn.query("select id from artifact where type=4010 and (active is null or active='Y') and rank=0")
    for art in arts:
        conn.update("update artifact set rank=%s where id=%s", MAX, art["id"])
    conn.close()

    logger.info("End.")