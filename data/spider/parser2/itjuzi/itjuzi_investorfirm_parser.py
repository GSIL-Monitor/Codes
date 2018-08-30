# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import gridfs
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import db

#logger
loghelper.init_logger("itjuzi_investorfirm_parser", stream=True)
logger = loghelper.get_logger("itjuzi_investorfirm_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
collection = mongo.crawler_v3.projectdata
imgfs = gridfs.GridFS(mongo.gridfs)

# kafka
kafkaProducer = None


SOURCE = 13030  #ITJUZI
TYPE = 36003    #投资公司

def process():
    logger.info("itjuzi_investorfirm_parser begin...")
    items = collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}).sort("key_int", pymongo.ASCENDING)
    for item in items:
        logger.info(item["url"])
        r = parser(item)
        if r is None:
            continue
        save(r)
        collection.update({"_id":item["_id"]},{"$set":{"processed":True}})
    logger.info("itjuzi_investorfirm_parser end.")

def save(r):
    investor_key, investor_name, logo, website, stageStr, fieldsStr, desc = r
    conn = db.connect_torndb()
    source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                                               SOURCE, investor_key)
    logo_id = None
    if source_investor == None or source_investor["logo"] == None or source_investor["logo"] == "":
        if logo is not None and logo != "":
            image_value = None
            retries = 0
            while image_value is None:
                image_value = my_request.get_image(logger,logo, agent=True)
                retries += 1
                if retries >= 5:
                    break
            if image_value is not None:
                logo_id = imgfs.put(image_value, content_type='jpeg', filename='investor_%s_%s.jpg' % (SOURCE, investor_key))
                logger.info("gridfs logo_id=%s" % logo_id)
    else:
        logo_id = source_investor["logo"]

    if source_investor is None:
        sql = "insert source_investor(name,website,description,logo,stage,field,type, \
        source,sourceId,createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
        source_investor_id = conn.insert(sql,
            investor_name,website,desc,logo_id,stageStr,fieldsStr,10020,SOURCE,investor_key)
    else:
        source_investor_id = source_investor["id"]
        sql = "update source_investor set name=%s,website=%s,description=%s,logo=%s,stage=%s,\
        field=%s,type=%s,modifyTime=now() where id=%s"
        conn.update(sql,
            investor_name,website,desc,logo_id,stageStr,fieldsStr,10020, source_investor_id)

    conn.close()

def parser(item):
    if item is None:
        return None

    investor_key = item["key"]

    html = item["content"]
    #logger.info(html)
    d = pq(html)
    investor_name = d('div.picinfo> p> span.title').text().strip()
    logger.info("investor_name: " + investor_name)

    if investor_name is None:
        logger.info("No investor name!!!")
        return None

    logo = d('div.pic> img').attr("src")
    if logo is not None:
        logo = logo.strip()
    logger.info("Investor Logo: %s" % logo)

    website = d('span.links >a[target="_black"]').attr("href")
    if website is None or website.strip() == "暂无":
        website = None
    else:
        website = website.strip()
    logger.info("Investor website: %s" % website)

    stageStr = d('div.pad.block> div.list-tags.yellow').text().replace(" ",",").strip()
    logger.info("Investor rounds: %s" % stageStr)

    fieldsStr = d('div.pad.block> div.list-tags.darkblue').text().replace(" ",",").strip()
    logger.info("Investor fields: %s" % fieldsStr)

    desc = d('div.des').text().strip()
    logger.info("Investor desc: %s" % desc)

    return investor_key, investor_name, logo, website, stageStr, fieldsStr, desc
