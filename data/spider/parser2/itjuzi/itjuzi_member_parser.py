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
loghelper.init_logger("itjuzi_member_parser", stream=True)
logger = loghelper.get_logger("itjuzi_member_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
collection = mongo.crawler_v3.projectdata
imgfs = gridfs.GridFS(mongo.gridfs)

# kafka
kafkaProducer = None


SOURCE = 13030  #ITJUZI
TYPE = 36005    #公司成员

def process():
    logger.info("itjuzi_member_parser begin...")
    items = collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}).sort("key_int", pymongo.ASCENDING)
    #items = collection.find({"source":SOURCE, "type":TYPE}).sort("key_int", pymongo.DESCENDING)
    for item in items:
        logger.info(item["url"])
        r = parser(item)
        if r is None:
            continue
        save(r)
        collection.update({"_id":item["_id"]},{"$set":{"processed":True}})
        #break
    logger.info("itjuzi_member_parser end.")

def save(r):
    member_key, name, weibo, introduction, education, work, location, role, pictureUrl, company_key, position = r
    conn = db.connect_torndb()
    source_member = conn.get("select * from source_member where source=%s and sourceId=%s",
                                                   SOURCE, member_key)
    logo_id = None
    if source_member == None or source_member["photo"] == None or source_member["photo"] == "":
        if pictureUrl is not None and pictureUrl != "":
            image_value = None
            retries = 0
            while image_value is None:
                try:
                    image_value = my_request.get_image(logger,pictureUrl, agent=True)
                except:
                    pass
                retries += 1
                if retries >= 5:
                    break
            if image_value is not None:
                logo_id = imgfs.put(image_value, content_type='jpeg', filename='member_%s_%s.jpg' % (SOURCE, member_key))
            logger.info("gridfs logo_id=%s" % logo_id)
    else:
        logo_id = source_member["photo"]

    if source_member is None:
        sql = "insert source_member(name,photo,weibo,location,role,description,\
        education,work,source,sourceId,createTime,modifyTime) \
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
        source_member_id = conn.insert(sql,
            name,logo_id,weibo,location,role,introduction,
            education,work,SOURCE,member_key)
    else:
        source_member_id = source_member["id"]
        sql = "update source_member set name=%s,photo=%s,weibo=%s,location=%s,role=%s,description=%s,\
        education=%s,work=%s,modifyTime=now() where id=%s"
        conn.update(sql,
            name,logo_id,weibo,location,role,introduction,
            education,work,source_member_id)

    if company_key is not None:
        source_company = conn.get("select * from source_company where source=%s and sourceId=%s",
                                  SOURCE, company_key)
        if source_company is not None:
            source_company_id = source_company["id"]
            source_company_member_rel = conn.get("select * from source_company_member_rel where \
                    sourceCompanyId=%s and sourceMemberId=%s",
                    source_company_id, source_member_id)
            if source_company_member_rel is None:
                conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                            position,type,createTime,modifyTime) \
                            values(%s,%s,%s,%s, now(),now())",
                            source_company_id, source_member_id,position,0)
    conn.close()

def parser(item):
    if item is None:
        return None

    member_key = item["key"]

    html = item["content"]
    #logger.info(html)
    d = pq(html)
    name = d('span.name').text().strip()
    logger.info("name: %s" % name)
    if name is None or name == "":
        return None

    company_key = None
    position = None
    company_url = d('p.titleset> span> a').attr("href")
    if company_url is not None:
        company_key = company_url.split("/")[-1]
        temp = d('p.titleset> span').text()
        position = temp.split("·")[-1].strip()

    logger.info("company key: %s" % company_key)
    logger.info("position: %s" % position)

    weibo = d('div.bottom-links> a').attr("href")
    if weibo is not None:
        weibo = weibo.strip()
    logger.info("weibo: %s" %  weibo)

    sec = d('i.fa-folder-o').parents("div.sec")
    introduction = pq(sec)('div> div.block-v').text().strip()
    if introduction == u"未收录相关信息":
        introduction = ""
    logger.info("introduction: %s" % introduction)

    sec = d('i.fa-briefcase').parents("div.sec")
    work = pq(sec)('div.wp100> ul> li> span> span> a').text().strip()
    if work == u"未收录相关信息":
        work = ""
    logger.info("work: %s" % work)

    sec = d('i.fa-book').parents("div.sec")
    education = pq(sec)('div.wp100> ul> li> span> span.right> a').text().strip()
    if education == u"未收录相关信息":
        education = ""
    logger.info("education: %s" % education)

    sec = d('i.fa-map-marker').parents("p")
    location = pq(sec).text().strip()
    logger.info("location: %s" % location)

    role = d('span.bg-blue').text().strip()
    logger.info("role: %s" % role)

    pictureUrl = d('div.infohead-person> div> div> p> span> img').attr("src").strip()
    logger.info("picture url: %s" % pictureUrl)

    logger.info("")
    return member_key, name, weibo, introduction, education, work, location, role, pictureUrl, company_key, position
