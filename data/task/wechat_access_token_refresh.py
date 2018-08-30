# -*- coding: utf-8 -*-
import os, sys
import datetime, time
from pymongo import MongoClient
import requests

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("wechat_access_token_refresh", stream=True)
logger = loghelper.get_logger("wechat_access_token_refresh")

WXS = [
    {"appid": "wxfb8740586a0d4601", "secret": "2a81eb3202bf3b3facda6bd070ac71b6"}, # 创投播报
    {"appid": "wx8737601219beba22", "secret": "3b7ce248a628d7b6f9fdea99eb78ed83"}, # 创投新榜
    # {"appid": "wx766854150052d912", "secret": "d4fc5ea387e938c7641dd434a4d7a891"}, # 烯牛小助手 - 公众号
    # {"appid": "wx9aa7c074c4463a45", "secret": "e1fc76e6eae66587e0df8c3fc0ffe837"}, # 烯牛数据 - 公众号
]

def get_dev_mongo():
    return MongoClient("10.44.202.51")


def main():
    mongo = db.connect_mongo()
    mongo_dev = get_dev_mongo()
    for wx in WXS:
        appid = wx["appid"]
        secret = wx["secret"]
        now = datetime.datetime.utcnow()

        token = None
        tokens = list(mongo.xiniudata.wechat_accesstoken.find({"appid": appid}))
        if len(tokens)== 1:
            access_token_refresh_time = tokens[0]["access_token_refresh_time"]

            time_diff = (now - access_token_refresh_time).seconds
            logger.info("time_diff: %s", time_diff)
            if time_diff < 6000:
                token = tokens[0]
        elif len(tokens) > 1:
            mongo.xiniudata.wechat_accesstoken.delete_many({"appid": appid})

        if token is None:
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + secret
            r = requests.get(url)
            result = r.json()
            logger.info(result)
            access_token = result.get("access_token")

            if access_token is not None:
                # update
                mongo.xiniudata.wechat_accesstoken.delete_many({"appid": appid})
                mongo.xiniudata.wechat_accesstoken.insert_one({
                    "appid": appid,
                    "access_token": access_token,
                    "access_token_refresh_time": now
                })

                # update dev
                mongo_dev.xiniudata.wechat_accesstoken.delete_many({"appid": appid})
                mongo_dev.xiniudata.wechat_accesstoken.insert_one({
                    "appid": appid,
                    "access_token": access_token,
                    "access_token_refresh_time": now
                })

    mongo_dev.close()
    mongo.close()



if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)