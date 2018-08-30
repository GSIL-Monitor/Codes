#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import os, sys
import random
import pymongo
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db

#mongo
#mongo = db.connect_mongo()
#collection = mongo.raw.proxy

def get_single_proxy(proxy_rule):
    try:
        mongo = db.connect_mongo()
        collection = mongo.raw.proxy
        proxies = list(collection.find(proxy_rule))
        mongo.close()

        if len(proxies) > 0:
            rint = random.randint(0, len(proxies)-1)
            proxy = proxies[rint]
            temps = proxy["ip:port"].split(":")
            proxy["ip"] = temps[0]
            try:
                proxy["port"] = int(temps[1])
            except:
                return None
            return proxy
    except:
        pass

    return None

def get_single_proxy_x(proxy_rule,max):
    proxiesr = []
    try:
        mongo = db.connect_mongo()
        collection = mongo.xiniudata.proxy
        # proxies = list(collection.find(proxy_rule))
        proxies = list(collection.find(proxy_rule).sort("modifyTime", pymongo.DESCENDING).limit(max))
        mongo.close()
        print ("got %s proxies"%len(proxies))
        for pro in proxies:
            proxy = {}
            proxy["ip"] = pro["ip"]
            proxy["type"] = pro["type"]
            try:
                proxy["port"] = int(pro["port"])
            except:
                continue
            proxiesr.append(proxy)
    except Exception, e:
        print e
        pass

    return proxiesr

def get_single_proxy_x_one(proxy_rule,max):
    try:
        mongo = db.connect_mongo()
        collection = mongo.xiniudata.proxy
        # proxies = list(collection.find(proxy_rule))
        proxies = list(collection.find(proxy_rule).sort("modifyTime", pymongo.DESCENDING).limit(max))
        mongo.close()
        print ("got %s proxies"%len(proxies))
        # for pro in proxies:
        #     proxy = {}
        #     proxy["ip"] = pro["ip"]
        #     proxy["type"] = pro["type"]
        #     try:
        #         proxy["port"] = int(pro["port"])
        #     except:
        #         continue
        #     proxiesr.append(proxy)
        if len(proxies) > 0:
            rint = random.randint(0, len(proxies)-1)
            proxy = proxies[rint]
            try:
                proxy["port"] = int(proxy["port"])
            except:
                return None
            return proxy
    except Exception, e:
        print e
        pass

    return None

if __name__ == '__main__':
    # proxy_rule = {'type': 'http', 'anonymity':'high'}
    # print get_single_proxy(proxy_rule)
    rule = {'type': 'HTTP', 'anonymous': 'high'}
    proxy_ips = get_single_proxy_x(rule, 5000)