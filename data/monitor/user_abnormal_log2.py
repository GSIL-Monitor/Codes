# -*- coding: utf-8 -*-
import os, sys
import time, datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("user_abnormal_log2", stream=True)
logger = loghelper.get_logger("user_abnormal_log2")


def main():
    logger.info("cookie cnt > 50 in 60m")
    ips = {}
    mongo = db.connect_mongo()
    logs = list(mongo.log.user_log.find({"code": 0, "time": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(minutes=60)}}))
    for log in logs:
        ip = log.get("ip")
        if ip is None:
            continue
        if ip.startswith("10."):
            continue

        user_cookie = log.get("userCookie")
        if user_cookie is None:
            continue

        if ips.has_key(ip):
            if user_cookie not in ips[ip]:
                ips[ip].append(user_cookie)
        else:
            ips[ip] = [user_cookie]

    spider_ips = load_spider_ip()
    for k, v in ips.items():
        if len(v) > 50:
            bip = mongo.xiniudata.blackwhitelist.find_one({"ip" : k})
            if bip is None:
                if not spider_ips.has_key(k):
                    logger.info("ip: %s, cookie cnt: %s", k, len(v))
                    mongo.xiniudata.blackwhitelist.insert_one({"type" : "black", "ip" : k, "status": "Y",
                                                               "createTime": datetime.datetime.utcnow(),
                                                               "memo": "in 1 hour cookie cnt: %s" % (len(v))})


def main2():
    logger.info("cookie cnt > 5 in 1m")
    ips = {}
    ips_cnt = {}
    mongo = db.connect_mongo()
    logs = list(mongo.log.user_log.find({"code": 0, "time": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(minutes=1)}}))
    for log in logs:
        ip = log.get("ip")
        if ip is None:
            continue
        if ip.startswith("10."):
            continue

        user_cookie = log.get("userCookie")
        if user_cookie is None:
            continue

        if ips.has_key(ip):
            if user_cookie not in ips[ip]:
                ips[ip].append(user_cookie)
        else:
            ips[ip] = [user_cookie]

        if ips_cnt.has_key(ip):
            ips_cnt[ip] += 1
        else:
            ips_cnt[ip] = 1

    spider_ips = load_spider_ip()
    for k, v in ips.items():
        if len(v) >= 5:
            bip = mongo.xiniudata.blackwhitelist.find_one({"ip" : k})
            if bip is None:
                if not spider_ips.has_key(k):
                    total = ips_cnt[k]
                    cnt = len(v)
                    rate = (cnt+0.0) / total
                    logger.info("ip: %s, cookie cnt: %s, total cnt:%s, rate: %s", k, cnt, total, rate)
                    if rate > 0.9 or cnt > 10:
                        mongo.xiniudata.blackwhitelist.insert_one({"type" : "black", "ip" : k, "status": "Y",
                                                                   "createTime": datetime.datetime.utcnow(),
                                                                   "memo": "in 1 minute cookie cnt: %s, total cnt:%s" % (cnt, total)})


def load_spider_ip():
    ips = {}
    fp = open('spider_ip.txt')
    for line in fp.readlines():
        ip = line.strip()
        ips[ip] = 1
    return ips


if __name__ == '__main__':
    if len(sys.argv) > 1:
        p = sys.argv[1]
        if p == "test":
            main2()
            exit()

    while True:
        main2()
        time.sleep(10)