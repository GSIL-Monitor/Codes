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
loghelper.init_logger("proxy_kuaidaili", stream=True)
logger = loghelper.get_logger("proxy_kuaidaili")


#mongo
# mongo = db.connect_mongo()
# collection = mongo.raw.proxy


pmap = {
    "https" : "protocol=2",
    "http" : "protocol=1",
    "high": "an_ha=1",          #高匿名
    "normal": "an_tr=1&an_an=1"    #非高匿名
}
def get_proxy():
    while True:
        try:
            # sleep_time = random.randint(10, 30)
            proxy_api('https', 'high')
            time.sleep(10)
            proxy_api('https', 'normal')
            time.sleep(10)
            proxy_api('http', 'high')
            time.sleep(10)
            proxy_api('http', 'normal')
            time.sleep(10)

            time.sleep(10)
        except Exception,e:
            logger.info(e)

        time.sleep(60)


def proxy_api(httpflag, anonymous):

    url = 'http://dev.kdlapi.com/api/getproxy/?orderid=992403232032123&num=100&b_pcchrome=1&b_pcie=1&b_pcff=1&method=2&sep=1'

    if pmap.has_key(httpflag):
        url = url + '&' + pmap[httpflag]
    if pmap.has_key(anonymous):
        url = url + '&' + pmap[anonymous]

    result = None
    while True:
        try:
            logger.info(url)
            r = requests.get(url, timeout=60)
            result = r.text
            logger.info(result)
            if result.find(".") >=0 and result.find("8") >=0:
                break
        except:
            time.sleep(10)
            pass

    if result is not None:
        ips = result.split()
        for ipp in ips:
            if ipp.split(":") >= 2:
                ip = ipp.split(":")[0].strip()
                port = ipp.split(":")[1].strip()
                logger.info("ip :%s, port: %s",ip, port)
                source_proxy = {
                    "type": "HTTP" if httpflag == "http" else "HTTPS",
                    "ip": ip,
                    "port": port,
                    "country": "",
                    "anonymous": "high" if anonymous == "high" else "normal",
                    "source": "kuaidaili.com",
                }
                parser_mongo_util.save_mongo_proxy(source_proxy)

    time.sleep(10)

    # old_proxys = list(collection.find({'type': type, 'anonymity': anonymous}))
    # old_arr = []
    # for old_one in old_proxys:
    #     old_arr.append(old_one)
    #
    #
    # if len(ip_list) > 10:
    #     for proxy_one in ip_list:
    #         proxy_one['anonymity'] = anonymous
    #         proxy_one['type'] = type
    #         collection.insert_one(proxy_one)
    #
    #     for old_one in old_arr:
    #         collection.delete_one(old_one)





if __name__ == '__main__':
    get_proxy()
