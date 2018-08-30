# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import urllib2
import cookielib, Cookie
from pymongo import MongoClient
import pymongo
import gevent
import socket
import ssl
import random

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../support'))

import loghelper, db
import proxy_pool

#logger
loghelper.init_logger("BaseCrawler", stream=True)
logger = loghelper.get_logger("BaseCrawler")

#mongo
#mongo = db.connect_mongo()
#collection = mongo.raw.projectdata


class RedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        pass


class BaseCrawler:
    def __init__(self, max_crawl=50, timeout=10,use_proxy=True):
        self.opener = None
        self.max_crawl = max_crawl
        self.current_crawl = 0
        self.http_proxy = None
        self.https_proxy = None
        self.timeout=timeout
        self.use_proxy = use_proxy
        self.num = random.randint(1, 20)

    def login(self, url, redirect=True):
        self.init_http_session(url, redirect)

    def is_crawl_success(self,url, content):
        return True

    def get(self, SOURCE, TYPE, key):
        mongo = db.connect_mongo()
        collection = mongo.raw.projectdata
        item = collection.find_one({"source":SOURCE, "type":TYPE, "key":key})
        mongo.close()
        return item

    def save(self, SOURCE, TYPE, url, key, content):
        logger.info("Saving: %s", url)
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

        mongo = db.connect_mongo()
        collection = mongo.raw.projectdata
        if collection.find_one({"source":SOURCE, "type":TYPE, "key":key}) is not None:
            collection.delete_one({"source":SOURCE, "type":TYPE, "key":key})
        collection.insert_one(collection_content)
        mongo.close()
        logger.info("Saved: %s", url)

    def get_proxy(self, http_type):
        proxy = {'type': http_type, 'anonymity':'high'}
        proxy_ip = None
        while proxy_ip is None:
            logger.info("Start proxy_pool.get_single_proxy %s", self.num)
            proxy_ip = proxy_pool.get_single_proxy(proxy)
            if proxy_ip is None:
                logger.info("proxy_pool.get_single_proxy return None")
                if socket.socket.__module__ == "gevent.socket":
                    gevent.sleep(30)
                else:
                    time.sleep(30)
        return proxy_ip

    def init_http_session(self,url,redirect=True):
        if self.opener is not None:
            self.opener.close()

        handlers = []
        if self.use_proxy:
            if url.lower().startswith("https"):
                http_type = "https"
            else:
                http_type = "http"

            if self.http_proxy is None or http_type == "http":
                self.http_proxy = self.get_proxy("http")
                logger.info("Proxy: http://%s:%s" % (self.http_proxy["ip"], self.http_proxy["port"]))

            if self.https_proxy is None or http_type == "https":
                self.https_proxy = self.get_proxy("https")
                logger.info("Proxy: https://%s:%s" % (self.https_proxy["ip"], self.https_proxy["port"]))

            handlers.append(urllib2.ProxyHandler({"http":"http://%s:%s" % (self.http_proxy["ip"], self.http_proxy["port"])}))
            handlers.append(urllib2.ProxyHandler({"https":"http://%s:%s" % (self.https_proxy["ip"], self.https_proxy["port"])}))

        context = ssl._create_unverified_context()
        handlers.append(urllib2.HTTPSHandler(0, context))

        self.cookiejar = cookielib.CookieJar()
        handlers.append(urllib2.HTTPCookieProcessor(self.cookiejar))
        if redirect is False:
            handlers.append(RedirectHandler)

        self.opener = urllib2.build_opener(*handlers)

    def crawl(self, url, headers={}, cookies=None, postdata=None, redirect=True, login=True, agent=False):
        logger.info("crawl: %s", url)
        if self.opener is None:
            if login:
                self.login(url,redirect)
            else:
                self.init_http_session(url, redirect)
        else:
            if self.current_crawl >= self.max_crawl:
                self.current_crawl = 0
                if login:
                    self.login(url,redirect)
                else:
                    self.init_http_session(url, redirect)

        self.current_crawl += 1

        #set user-agent: Itjuzi
        if agent is True:
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
            if url.find("itjuzi")>=0:
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0'
            if url.find("zhihu") >= 0:
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            headers['User-Agent'] = user_agent

        content = None
        try:
            if cookies is not None:
                for k in cookies:
                    cookie = Cookie.SimpleCookie()
                    cookie[k] = cookies[k]
                    self.cookiejar.set_cookie(cookie)

            request = urllib2.Request(url, postdata, headers)
            logger.info("Start, %s", url)
            r = self.opener.open(request, timeout=self.timeout)
            logger.info("Got, %s", url)

            content_length = None
            if r.headers.has_key("content-length"):
                content_length = int(r.headers['content-length'])
                #logger.info("Length: %s", content_length)

            content = r.read()

            redirect_url = r.geturl()
            if r.headers.has_key("Location"):
                redirect_url = r.headers["Location"]

            if content_length is None:
                if self.is_crawl_success(url, content):
                    return {'get': 'success', 'content': content, 'redirect_url':redirect_url, 'code':200}
                else:
                    logger.info("Fail at 'is_crawl_success'")
            else:
                if content_length == len(content):
                    if self.is_crawl_success(url, content):
                        return {'get': 'success', 'content': content, 'redirect_url':redirect_url, 'code':200}
                    else:
                        logger.info("Fail at 'is_crawl_success'")
                else:
                    logger.info("Content length error: should be %d, actual %d", content_length, len(content))
        except urllib2.HTTPError, e:
            if e.code >= 500:
                logger.info("Http code: %s", e.code)
                try:
                    content = e.read()
                except:
                    pass
            elif e.code == 301 or e.code == 302:
                logger.info("Http code: %s", e.code)
                redirect_url = e.geturl()
                if e.headers.has_key("Location"):
                    redirect_url = e.headers["Location"]
                return {'get': 'redirect', "url":redirect_url, 'code':e.code}
            else:
                try:
                    content_length = None
                    if e.headers.has_key("content-length"):
                        content_length = int(e.headers['content-length'])

                    content = e.read()

                    redirect_url = e.geturl()
                    if e.headers.has_key("Location"):
                        redirect_url = e.headers["Location"]


                    if content_length is None:
                        if self.is_crawl_success(url, content):
                            return {'get': 'success', 'content': content, 'redirect_url':redirect_url, 'code':e.code}
                        else:
                            logger.info("Fail at 'is_crawl_success'")
                    else:
                        if content_length == len(content):
                            if self.is_crawl_success(url, content):
                                return {'get': 'success', 'content': content, 'redirect_url':redirect_url, 'code':e.code}
                            else:
                                logger.info("Fail at 'is_crawl_success'")
                        else:
                            logger.info("Content length error: should be %d, actual %d", content_length, len(content))
                except Exception, e:
                    #logger.info("exception position 2")
                    #logger.info(e)
                    pass
        except Exception, e:
            #logger.info("exception position 1")
            logger.info(e)
            pass

        logger.info("Fail, %s", url)

        if login:
            self.login(url,redirect)
        else:
            self.init_http_session(url, redirect)
        return {'get': 'fail', 'url': url, "content":content, "code":-1}
