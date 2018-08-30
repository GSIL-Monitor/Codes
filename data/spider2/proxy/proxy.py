#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-
import sys, os
import random, time, json
import requests

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../parser/util2'))
import parser_mongo_util
# logger
loghelper.init_logger("proxy", stream=True)
logger = loghelper.get_logger("proxy")


#mongo
mongo = db.connect_mongo()
collection = mongo.raw.proxy

def get_proxy():
    while True:
        try:
            # sleep_time = random.randint(10, 30)
            proxy_api('http', 'high')
            time.sleep(5)
            proxy_api('https', 'high')
            time.sleep(5)
            proxy_api('socks4', 'high')
            time.sleep(5)
            proxy_api('socks5', 'high')
            time.sleep(30)
        except Exception,e:
            logger.info(e)


def proxy_api(type, anonymous):
    t = 1
    if type == 'http':
        t = '1'
        stype = "HTTP"
    elif type == 'https':
        t = '2'
        stype = "HTTPS"
    elif type == 'socks4':
        t = '4'
        stype = "SOCKS4"
    elif type == 'socks5':
        t = '5'
        stype = "SOCKS5"
    else:
        return

    if anonymous == 'high':
        a = '3,5'
    else:
        a = '2'

    url = 'http://proxy.mimvp.com/api/fetch.php?orderid=860150908143212810&num=100&country_group=1' \
          '&http_type='+t+'&anonymous='+a+'&result_fields=1,2,3,4,5,6,7,8,9&result_format=json'
    logger.info(url)

    while True:
        try:
            r = requests.get(url, timeout=60)
            result = json.loads(r.text)
            ip_list = result['result']
            logger.info("cnt: %d", len(ip_list))
            if len(ip_list) > 0:
                break
        except:
            pass
        time.sleep(10)

    old_proxys = list(collection.find({'type': type, 'anonymity': anonymous}))
    old_arr = []
    for old_one in old_proxys:
        old_arr.append(old_one)


    if len(ip_list) > 10:
        for proxy_one in ip_list:
            proxy_one['anonymity'] = anonymous
            proxy_one['type'] = type
            collection.insert_one(proxy_one)

            source_proxy = {
                "type": stype,
                "ip": proxy_one["ip:port"].split(":")[0],
                "port": proxy_one["ip:port"].split(":")[1],
                "country": "国内" if proxy_one.has_key("country") and proxy_one["country"] is not None and proxy_one["country"].find("中国")>=0 else "国外",
                "anonymous": "high" if anonymous == "high" else "normal",
                "source": "mimvp.com",
            }
            parser_mongo_util.save_mongo_proxy(source_proxy)

        for old_one in old_arr:
            collection.delete_one(old_one)



if __name__ == '__main__':
    # if len(sys.argv) > 2:
    #     type = sys.argv[1]
    #     anonymity = sys.argv[2]
    #     print type
    #     print anonymity
    #     get_proxy(type, anonymity)
    get_proxy()
