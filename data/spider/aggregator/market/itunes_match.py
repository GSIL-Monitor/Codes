# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import gridfs
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from tld import get_tld
from urlparse import urlsplit
import tldextract
import re

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import db
import extract

#logger
loghelper.init_logger("itunes_match", stream=True)
logger = loghelper.get_logger("itunes_match")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)
itunes_collection = mongo.crawler_v2.market_itunes

#mysql
conn = db.connect_torndb()

if __name__ == "__main__":
    logger.info("Start...")
    #rexExp = re.compile(r"[一-龥]+")
    apps = itunes_collection.find({"parsed":True})
    for app in apps:
        html_parsed= app.get("html_parsed")
        if html_parsed is None:
            continue
        json_content = app.get("json")
        if json_content is None:
            continue

        urls = html_parsed.get('urls')
        if urls == None:
            continue

        companyId = app.get("companyId")
        if companyId is None:
            for url in urls:
                try:
                    domain = util.get_domain(url)
                except:
                    continue

                if domain is None:
                    continue

                d = conn.get("select * from domain where domain=%s limit 1",domain)
                if d is not None:
                    companyId = d["companyId"]
                    break

        if companyId is not None:
            logger.info("companyId=%s, app=%s" % (companyId,app["url"]))
            a = conn.get("select * from artifact where type=4040 and domain=%s limit 1", app["appId"])
            if a is None:
                try:
                    highpoints = re.compile(u'[\U00010000-\U0010ffff]')
                except re.error:
                    # UCS-2 build
                    highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                json_content = highpoints.sub(u'', json_content)

                j = json.loads(json_content)
                r = j["results"][0]
                name=r["trackName"]
                description=r["description"]
                link=app["url"]
                type=4040
                other=json_content
                domain = app["appId"]

                sql = "insert artifact(companyId, name, description, link, domain, others, \
                    type, active, createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s, \
                    4040,'Y',now(),now())"
                artifact_id = conn.insert(sql,
                                companyId,
                                name,
                                description,
                                link,
                                domain,
                                json_content
                                )
                #break
            if app.get("companyId") is None:
                itunes_collection.update_one({"_id":app["_id"]},{'$set':{'companyId':companyId}})


