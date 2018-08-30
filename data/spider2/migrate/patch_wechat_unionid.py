# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback
import requests
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_wechat_unionid", stream=True)
logger = loghelper.get_logger("patch_wechat_unionid")

appid="wx766854150052d912"
appsecret="d4fc5ea387e938c7641dd434a4d7a891"
ACCESS_TOKEN = None     #有效期为7200秒,开发者必须在自己的服务全局缓存access_token
ACCESS_TOKEN_TIME = 0

def refreshToken():
    global ACCESS_TOKEN, ACCESS_TOKEN_TIME

    if ACCESS_TOKEN is None or ACCESS_TOKEN_TIME + 7000 < time.time():
        print "get ACCESS_TOKEN and JSAPI_TICKET"
        ACCESS_TOKEN_TIME = time.time()
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (appid,appsecret)
        retry = 0
        while True:
            if retry > 3:
                break
            retry += 1
            try:
                r = requests.get(url)
            except:
                time.sleep(2)
                continue
            if r.status_code != 200:
                time.sleep(2)
                continue
            break
        if r is None or r.status_code != 200:
            return "{}"
        j = r.json()
        ACCESS_TOKEN = j["access_token"]


if __name__ == "__main__":
    refreshToken()

    conn = db.connect_torndb()
    us = conn.query("select * from user_wechat")
    for u in us:
        logger.info("nickname=%s, openid=%s", u["nickname"], u["openid"])
        url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (ACCESS_TOKEN, u["openid"])
        r = requests.get(url)
        j = r.json()
        if j.has_key("errcode"):
            logger.info(j)
        else:
            unionid = j["unionid"]

            if j["subscribe"] == 1:
                logger.info("unionid=%s, nickname=%s", unionid, j["nickname"])
                conn.update("update user_wechat set nickname=%s,sex=%s,province=%s,city=%s,country=%s,"
                            "headimgurl=%s, unionid=%s where id=%s",
                            j["nickname"],j["sex"],j["province"],j["city"],j["country"],
                            j["headimgurl"],j["unionid"], u["id"])
            elif j.has_key("unionid"):
                logger.info("unionid=%s", unionid)
                conn.update("update user_wechat set unionid=%s where id=%s", j["unionid"], u["id"])
        logger.info("")
    conn.close()