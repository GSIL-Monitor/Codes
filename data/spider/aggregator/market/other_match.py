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
loghelper.init_logger("other_match", stream=True)
logger = loghelper.get_logger("other_match")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)
market_collection = mongo.crawler_v2.market_other

#mysql
conn = db.connect_torndb()

# wandoujia & myapp
if __name__ == "__main__":
    logger.info("Start...")

    apps = market_collection.find({})
    for app in apps:
        if app.get("wdj") is None and app.get("myapp") is None:
            continue

        package = app.get("package")
        logger.info(package)

        companyId = app.get("companyId")
        artifact_id = None

        # check package
        if companyId is None:
            a = conn.get("select * from artifact where type=4050 and domain=%s limit 1", package)
            if a is not None:
                artifact_id = a["id"]
                companyId = a["companyId"]

        # check domain name
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

        # check by author
        if companyId is None:
            if app.get("wdj") is not None:
                author = app.get("wdj").get("author")
                if author is not None and author.strip() != "":
                    d = conn.get("select * from company_alias where name=%s and type=12010 limit 1",author.strip())
                    if d is not None:
                        companyId = d["companyId"]

        if companyId is None:
            if app.get("myapp") is not None:
                author = app.get("myapp").get("author")
                if author is not None and author.strip()!="":
                    d = conn.get("select * from company_alias where name=%s and type=12010 limit 1",author.strip())
                    if d is not None:
                        companyId = d["companyId"]

        if companyId is not None:
            if artifact_id is None:
                a = conn.get("select * from artifact where type=4050 and domain=%s limit 1", package)
                if a is None:
                    if app.get("wdj") is not None:
                        name = app.get("wdj").get("name")
                        description = app.get("wdj").get("desc")
                    else:
                        name = app.get("myapp").get("name")
                        description = app.get("myapp").get("desc")

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

            logger.info("companyId=%s, artifactId=%s" % (companyId, artifact_id))

            if app.get("wdj") is not None:
                link = "http://www.wandoujia.com/apps/%s" % package
                m = conn.get("select * from artifact_market where type=16030 and artifactId=%s and link=%s limit 1",
                             artifact_id, link
                             )
                if m is None:
                    sql = "insert artifact_market(artifactId,name,description,link, domain, \
                        type, active, createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s, \
                        16030,'Y',now(),now())"
                    conn.insert(sql,
                                artifact_id,
                                app.get("wdj").get("name"),
                                app.get("wdj").get("desc"),
                                link,
                                package
                                )

            if app.get("myapp") is not None:
                link = "http://android.myapp.com/myapp/detail.htm?apkName=%s" % package
                m = conn.get("select * from artifact_market where type=16040 and artifactId=%s and link=%s limit 1",
                             artifact_id, link
                             )
                if m is None:
                    sql = "insert artifact_market(artifactId,name,description,link, domain, \
                        type, active, createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s, \
                        16040,'Y',now(),now())"
                    conn.insert(sql,
                                artifact_id,
                                app.get("myapp").get("name"),
                                app.get("myapp").get("desc"),
                                link,
                                package
                                )

            if app.get("companyId") is None:
                market_collection.update_one({"_id":app["_id"]},{'$set':{'companyId':companyId}})

            #break