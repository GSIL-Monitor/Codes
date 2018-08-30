# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from bson.objectid import ObjectId
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db, download


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import parser_db_util

#logger
loghelper.init_logger("feixiaohao_p", stream=True)
logger = loghelper.get_logger("feixiaohao_p")

#parse data from feixiaohao directly
download_crawler = download.DownloadCrawler(use_proxy=False)

def parse(item, tt=1):

    if item["bz_code"] is not None and item["bz_code"].strip() != "":
        logger.info("parsing : %s/%s", item["bz_code"],item["coinEnglishName"])
        publishDate = None
        try:
            publishDate = datetime.datetime.strptime(item["publishDateStr"], "%Y-%m-%d")
        except:
            pass

        source_feixiaohao = {
            "companyId": None,
            "symbol": item["bz_code"].strip(),
            "name": item["coinChineseName"],
            "enname": item["coinEnglishName"],
            "publishDate": publishDate,
            "websites": "|".join(item["websites"]) if len(item["websites"])>0 else None,
            "browsers": "|".join(item["blockchainWebsites"]) if len(item["blockchainWebsites"])>0 else None,
            "description": item["description"],
            "whitepaper": item["whitebookLink"],
            "logo": item["logo_url"],
        }

        parser_db_util.save_blockchain_standard_feixiaohao(source_feixiaohao, download_crawler)



if __name__ == '__main__':
    logger.info("Begin...")
    # noo = 0
    # conn = db.connect_torndb()
    while True:

        mongo = db.connect_mongo()
        collection = mongo.raw.blockchain

        while True:
            # items = list(collection.find({"_id" : ObjectId("5ab9b0cadeb47110109ab4b0")}).limit(100))
            items = list(collection.find({"processStatus":0}))
            logger.info("step 1 items : %s", len(items))
            for item in items:
                parse(item)
                collection.update({"_id": item["_id"]}, {"$set": {"processStatus": 1}})
            break
            # if len(items) == 0:
            #     break

        # break

        while True:
            # items = list(collection.find({"_id" : ObjectId("5ab9b0cadeb47110109ab4b0")}).limit(100))
            items = list(collection.find({"processStatus":1}))
            logger.info("step 2 items : %s", len(items))
            for item in items:
                if item.has_key("cq") is True and item["cq"] is not None:
                    s = {
                        "symbol": item["bz_code"].strip(),
                        "name": item["coinChineseName"],
                        "enname": item["coinEnglishName"],
                        "cq": item["cq"]
                    }
                    ff = parser_db_util.save_blockchain_cq(s)
                    if ff is True:
                        collection.update({"_id": item["_id"]}, {"$set": {"processStatus": 2}})
                else:
                    collection.update({"_id": item["_id"]}, {"$set": {"processStatus": 2}})
            break
            # if len(items) == 0:
            #     break

        # break
            mongo.close()
            conn.close()
        time.sleep(30*60)
        # break
