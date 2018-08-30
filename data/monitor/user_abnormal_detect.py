# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import requests

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("user_abnormal_detect", stream=True)
logger = loghelper.get_logger("user_abnormal_detect")


def check_ip(ip):
    url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s" % ip
    while True:
        try:
            r = requests.get(url)
            break
        except:
            pass

    return r.json()


def main():
    conn = db.connect_torndb()
    users = conn.query("select * from user where active is null or active !='D' order by id desc")
    for user in users:
        time.sleep(0.3)
        ip = user["loginIP"]
        if ip is None or ip.strip() == "":
            continue
        result = check_ip(ip)
        code = result["code"]
        if code != 0:
            continue
        data = result["data"]
        logger.info("userId: %s, isp: %s, %s", user["id"], data["isp_id"], data["isp"])

    conn.close()


def test():
    mongo = db.connect_mongo()
    for _id in range(8899,8929):
        mongo.log.user_abnormal_log.insert({
            "userId": _id,
            "type": "1m",
            "visit_times": 0,
            "createTime": datetime.datetime.utcnow(),
            "modifyTime": datetime.datetime.utcnow(),
            "processed": "N"
        })
    mongo.close()


if __name__ == '__main__':
    test()
    # while True:
    #     logger.info("Begin...")
    #     main()
    #     logger.info("End.")
    #     time.sleep(60)
