# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import requests
import json
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../support'))

import loghelper, config
import proxy_pool

#logger
loghelper.init_logger("BaseCrawler", stream=True)
logger = loghelper.get_logger("BaseCrawler")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

collection = mongo.crawler_v3.projectdata
collection.create_index([("source", pymongo.DESCENDING),
                         ("type", pymongo.DESCENDING),
                         ("key_int", pymongo.DESCENDING)], unique=False)
collection.create_index([("source", pymongo.DESCENDING),
                         ("type", pymongo.DESCENDING),
                         ("key", pymongo.DESCENDING)], unique=True)

class BaseCrawler:
    def __init__(self, max_crawl=10, header=False):
        self.http_session = None
        self.max_crawl = max_crawl
        self.current_crawl = 0
        self.header=header

    def login(self, url):
        self.init_http_session(url)

    def is_crawl_success(self,r):
        return True

    def get_latest_key_int(self,SOURCE,TYPE):
        latest = collection.find({"source":SOURCE, "type":TYPE}).sort("key_int", pymongo.DESCENDING).limit(1)
        if latest.count() > 0:
            return latest[0]["key_int"]
        return None

    def save(self, SOURCE, TYPE, url, key, content):
        try:
            key_int = int(key)
        except:
            key_int = None

        collection_content = {
            "date":datetime.datetime.now(),
            "source":SOURCE,
            "type":TYPE,
            "url":url,
            "key":key,
            "key_int":key_int,
            "content":content
        }

        if collection.find_one({"source":SOURCE, "type":TYPE, "key":key}) != None:
            collection.delete_one({"source":SOURCE, "type":TYPE, "key":key})
        collection.insert_one(collection_content)


    def init_http_session(self,url):
        if url.lower().startswith("https"):
            http_type = "https"
        else:
            http_type = "http"

        proxy = {'type': http_type, 'anonymity':'high'}
        proxy_ip = None
        while proxy_ip is None:
            proxy_ip = proxy_pool.get_single_proxy(proxy)
            if proxy_ip is None:
                time.sleep(60)
        logger.info("Proxy IP(%s): %s" % (http_type, proxy_ip))

        if self.http_session is None:
            self.http_session = requests.Session()
        self.http_session.proxies={http_type:"%s://%s:%s" % (http_type, proxy_ip["ip"], proxy_ip["port"])}

        if self.header:
            self.http_session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"


    def crawl(self, url, headers=None, cookies=None):
        logger.info(url)
        if self.http_session is None:
            self.login(url)
        else:
            if self.current_crawl >= self.max_crawl:
                self.current_crawl = 0
                self.login(url)

        self.current_crawl += 1

        retry_times = 0
        timeout = 20
        while retry_times < 100:
            logger.info("No.%d, %s" % (retry_times+1,url))
            try:
                r = self.http_session.get(url, timeout=timeout, headers=headers, cookies=cookies)
                logger.info("No.%d end, %s" % (retry_times+1,url))
                if r.status_code >=500:
                    logger.info("status_code=%s" % r.status_code)
                else:
                    # use page encoding
                    r.encoding = r.apparent_encoding
                    if self.is_crawl_success(r):
                        return r
            except Exception,ex:
                #logger.exception(ex)
                pass

            self.login(url)
            retry_times += 1

        return None