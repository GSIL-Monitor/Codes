# -*- coding: utf-8 -*-
import sys, os
import time
import traceback
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper


#logger
loghelper.init_logger("alexa_parser", stream=True)
logger = loghelper.get_logger("alexa_parser")


# mongo
mongo = db.connect_mongo()
alexa_collection = mongo.trend.alexa_raw
trends_alexa_collection = mongo.trend.alexa


def do_transfer(datas):
    flag = False
    for data in datas:
        logger.info(data["domain"])
        try:
            if 'country_rank' in data and 'page_view' in data:
                rankCountry = data['country_rank']
                logger.info(rankCountry)
                if rankCountry is None or rankCountry == '' or rankCountry == '-':
                    rankCountry = 0
                else:
                    rankCountry = int(str(rankCountry).replace(',', ''))

                rankGlobal = data['global_rank_value']
                if rankGlobal is None or rankGlobal == '' or rankGlobal == '-':
                    rankGlobal = 0
                else:
                    rankGlobal = int(str(rankGlobal).replace(',', ''))

                dailyIP = get_ip(rankGlobal)
                dailyPV = get_pv(dailyIP, data['page_view'])


                result = {
                    'domain': data['domain'],
                    'date': data['date'],
                    'global_rank': rankGlobal,
                    'country_rank': rankCountry,
                    'daily_ip': dailyIP,
                    'daily_pv': dailyPV
                }

                r = trends_alexa_collection.find_one(({"domain": data['domain'], "date": data['date']}))
                if r is None:
                    trends_alexa_collection.insert_one(result)
                # else:
                #     trends_alexa_collection.update_one({"_id": r["_id"]}, {'$set': result})
                flag = True
            else:
                logger.info("lack country_rank or page_view. domain: %s", data["domain"])
        except:
             traceback.print_exc()

        result = {
                "parser": 'Done'
            }
        alexa_collection.update_one({"_id": data["_id"]}, {'$set': result})

    return flag

def get_ip(x):
    if x is None or x == '':
        return 0
    return int(str(x).replace(',', ''))*3000

def get_pv(dailyIP, page_view):
    if len(page_view) == 0:
        return 0

    if page_view[0] == '-' or page_view[0] == '':
        return 0
    else:
        view = float(page_view[0].replace(',',''))
        if view == 0:
            view = 1
        return dailyIP * int(view)


if __name__ == "__main__":
    logger.info("Begin...")
    while True:
        datas = alexa_collection.find({"parser":{"$ne":"Done"}}).limit(10000)
        if datas.count() == 0:
            logger.info("Finish.")
            time.sleep(60)
            logger.info("Begin...")
        else:
            flag = do_transfer(datas)
            if flag is False:   #都是未准备好的
                time.sleep(60)