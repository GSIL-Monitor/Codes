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
from tld import get_tld

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
loghelper.init_logger("360_match", stream=True)
logger = loghelper.get_logger("360_match")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)
market_collection = mongo.crawler_v2.market_360

#mysql
conn = db.connect_torndb()

if __name__ == "__main__":
    logger.info("Start...")

    apps = market_collection.find({})
    for app in apps:
        html_parsed= app.get("html_parsed")
        if html_parsed is None:
            continue

        package = html_parsed.get("package")
        author = html_parsed.get("author")
        name = html_parsed["name"]
        description = html_parsed["desc"]
        link = app["url"]

        companyId = app.get("companyId")
        if companyId is None:
            # match by author
            if author is not None:
                d = conn.get("select * from company_alias where name=%s and type=12010 limit 1",author)
                if d is not None:
                    companyId = d["companyId"]

        if companyId is None:
            domain = "http://" + ".".join(package.split(".")[::-1])
            # logger.info(domain)
            try:
                domain = get_tld(domain)
            except:
                pass

            # logger.info(domain)

            if domain is not None:
                d = conn.get("select * from domain where domain=%s limit 1",domain)
                if d is not None:
                    companyId = d["companyId"]

        if companyId is not None:
            logger.info("companyId=%s, app=%s" % (companyId,app["url"]))
            a = conn.get("select * from artifact where type=4050 and domain=%s limit 1", package)
            if a is None:
                sql = "insert artifact(companyId, name, description, domain, \
                    type, active, createTime,modifyTime) \
                    values(%s,%s,%s,%s, \
                    4050,'Y',now(),now())"
                artifact_id = conn.insert(sql,
                                companyId,
                                name,
                                description,
                                package
                                )
            else:
                artifact_id = a["id"]

            m = conn.get("select * from artifact_market where type=16010 and artifactId=%s and link=%s limit 1",
                         artifact_id, link
                         )
            if m is None:
                sql = "insert artifact_market(artifactId,name,description,link, domain, \
                    type, active, createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s, \
                    16010,'Y',now(),now())"
                conn.insert(sql,
                            artifact_id,
                            name,
                            description,
                            link,
                            package
                            )
                #break

            if app.get("companyId") is None:
                market_collection.update_one({"_id":app["_id"]},{'$set':{'companyId':companyId}})

