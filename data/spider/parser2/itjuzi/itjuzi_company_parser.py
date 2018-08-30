# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import gridfs
import pymongo
import json
from bson import json_util
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from pyquery import PyQuery as pq

import itjuzi_helper

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import db
import util

#logger
loghelper.init_logger("itjuzi_company_parser", stream=True)
logger = loghelper.get_logger("itjuzi_company_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
collection = mongo.crawler_v3.projectdata
imgfs = gridfs.GridFS(mongo.gridfs)

# kafka
kafkaProducer = None


SOURCE = 13030  #ITJUZI
TYPE = 36001    #公司信息

def initKafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def process():
    logger.info("itjuzi_company_parser begin...")
    initKafka()

    items = collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}).sort("key_int", pymongo.DESCENDING).limit(1000)
    #items = collection.find({"source":SOURCE, "type":TYPE}).sort("key_int", pymongo.DESCENDING)
    for item in items:
        logger.info(item["url"])

        r = parse_base(item)
        if r is None:
            continue
        source_company_id = save_base(r)
        logger.info("source_company_id=%s", source_company_id)

        artifacts = parse_artifact(item)
        artifacts.extend(r["artifacts"])
        save_artifacts(source_company_id, artifacts)

        footprints = parse_footprint(item)
        save_footprints(source_company_id, footprints)

        members = parse_member(item)
        save_members(source_company_id, members)

        collection.update({"_id":item["_id"]},{"$set":{"processed":True}})

        msg = {"type":"company", "id":source_company_id}
        kafkaProducer.send_messages("parser_v2", json.dumps(msg))
        #break
    logger.info("itjuzi_company_parser end.")

def save_base(r):
    company_key = r["sourceId"]
    conn = db.connect_torndb()

    logo_id = None
    source_company = conn.get("select * from source_company where source=%s and sourceId=%s", SOURCE, company_key)
    if source_company is None or source_company["logo"] is None or source_company["logo"] == "":
        log_url = r["logo"]
        if log_url is not None and len(log_url.strip()) > 0:
            logger.info(log_url)
            image_value = None
            retries = 0
            while image_value is None:
                image_value = my_request.get_image(logger,log_url, agent=True)
                retries += 1
                if retries >= 5:
                    break
            if image_value is not None:
                logo_id = imgfs.put(image_value, content_type='jpeg', filename='company_%s_%s.jpg' % (SOURCE, company_key))
    else:
        logo_id = source_company["logo"]
    logger.info("gridfs logo_id=%s" % logo_id)

    if source_company == None:
        source_company_id = conn.insert("insert source_company(name,fullName,description,brief,\
                    round,roundDesc,companyStatus,fundingType,locationId,establishDate,logo,\
                    source,sourceId,createTime,modifyTime,\
                    field,subField,tags) \
                    values(%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,%s,%s,\
                    %s,%s,now(),now(),\
                    %s,%s,%s)",
                    r["productName"], r["fullName"], r["description"], r["brief"],
                    r["round"],r["roundDesc"],r["companyStatus"],r["fundingType"],r["locationId"],r["establishDate"],logo_id,
                    SOURCE,company_key,
                    r["field"],r["subField"],r["tags"]
                    )
    else:
        source_company_id = source_company["id"]
        conn.update("update source_company set \
                    name=%s,fullName=%s,description=%s, brief=%s, \
                    round=%s,roundDesc=%s,companyStatus=%s,fundingType=%s,locationId=%s,establishDate=%s,logo=%s, \
                    field=%s,subField=%s,tags=%s,\
                    modifyTime=now() \
                    where id=%s",
                    r["productName"], r["fullName"], r["description"], r["brief"],
                    r["round"],r["roundDesc"],r["companyStatus"],r["fundingType"],r["locationId"],r["establishDate"],logo_id,
                    r["field"],r["subField"],r["tags"],
                    source_company_id
                    )
    conn.close()

    return source_company_id

def parse_base(item):
    if item is None:
        return None

    logger.info("*** base ***")
    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    company_short_name = ""
    product_name = d('div.line-title> span> b').clone().children().remove().end().text().strip()
    temps = product_name.split("/",1)
    if len(temps) == 2:
        product_name = temps[0].strip()
        company_short_name = temps[1].strip()
    if company_short_name == "":
        company_short_name = product_name
    logger.info("product name: %s" % product_name)
    logger.info("company short name: %s" % company_short_name)

    company_name = d('div.des-more> div').eq(0).text().strip().replace("公司全称：","")
    if company_name == "暂无" or company_name == "暂未收录":
        company_name = ""
    company_name = util.norm_company_name(company_name)
    logger.info("company name: %s" % company_name)

    if company_short_name == "" and company_name == "":
        return

    establish_date = None
    str = d('div.des-more> div').eq(1).text().strip().replace("成立时间：","")
    result = util.re_get_result('(\d*?).(\d*?)$',str)
    if result != None:
        (year, month) = result
        try:
            if int(month) > 12:
                month = "1"
        except:
            month = "1"
        establish_date = datetime.datetime.strptime("%s-%s-1" % (year,month), '%Y-%m-%d')
    logger.info("establish date: %s" % establish_date)

    locationId=0
    str = d('span.loca').text().strip()
    #logger.info(str)
    result = util.re_get_result(u'(.*?)·(.*?)$',str)
    if result != None:
        (province, city) = result
        province = province.strip()
        city = city.strip()
        logger.info("location: %s-%s" % (province, city))

        locationId = 0
        conn = db.connect_torndb()
        result = conn.get("select * from location where locationName=%s", city)
        if result != None:
            locationId = result["locationId"]
        else:
            result = conn.get("select * from location where locationName=%s", province)
            if result != None:
                locationId = result["locationId"]
        conn.close()
    logger.info("locationId: %d" % locationId)

    company_status = 2010
    str = d('div.des-more> div').eq(2).text().strip()
    if str == "已关闭":
        company_status = 2020
    logger.info("company_status: %d" % company_status)

    funding_type = 0
    str = d("span.tag.bg-c").text().strip()
    logger.info("融资需求: %s" % str)
    if str == "融资需求 · 需要融资":
        funding_type = 8020
    elif str == "融资需求 · 寻求收购":
        funding_type = 8020
    logger.info("funding_type=%d" % funding_type)

    field = d("span.scope.c-gray-aset> a").eq(0).text().strip()
    logger.info("field: %s" % field)

    sub_field = d("span.scope.c-gray-aset> a").eq(1).text().strip()
    logger.info("sub field: %s" % sub_field)

    tags = d("div.tagset.dbi.c-gray-aset> a >span").text().strip().replace(" ",",")
    logger.info("tags: %s" % tags)

    desc = d("div.des").text().strip()
    logger.info("desc: %s" % desc)

    #logo
    logo = d("div.pic >img").attr("src")
    logger.info("logo: %s", logo)

    website = d('div.link-line> a').attr("href").strip()
    if website=="http://%e6%9a%82%e6%97%a0":
        website = ""
    website = util.norm_url(website)
    logger.info("website: %s" % website)

    artifacts = [{
            "type":4010,
            "name":product_name,
            "desc":desc,
            "link":website
    }]

    #获投状态
    roundStr = d('span.t-small.c-green').text().replace("(","").replace(")","").replace("获投状态：","").strip()
    fundingRound,roundStr = itjuzi_helper.getFundingRound(roundStr)
    logger.info("获投状态: %d, %s", fundingRound, roundStr)

    logger.info("")


    return {
        "shortName": company_short_name,
        "fullName": company_name,
        "productName": product_name,
        "description": desc,
        "brief": "",
        "round": 0,
        "roundDesc": "",
        "companyStatus": company_status,
        "fundingType": funding_type,
        "locationId": locationId,
        "establishDate": establish_date,
        "logo": logo,
        "sourceId": company_key,
        "field": field,
        "subField": sub_field,
        "tags": tags,
        "artifacts":artifacts
    }


def save_artifacts(source_company_id, artifacts):
    conn = db.connect_torndb()
    conn.execute("delete from source_artifact where sourceCompanyId=%s", source_company_id)

    for a in artifacts:
        source_artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=%s and link=%s",
                        source_company_id, a["type"], a["link"])
        if source_artifact is None:
            sql = "insert source_artifact(sourceCompanyId,`name`,`description`,`link`,`type`,createTime,modifyTime) \
                  values(%s,%s,%s,%s,%s,now(),now())"
            conn.insert(sql, source_company_id,a["name"],a["desc"],a["link"],a["type"])
    conn.close()

def parse_artifact(item):
    if item is None:
        return None

    artifacts = []
    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    #artifact
    logger.info("*** artifact ***")
    lis = d('ul.list-prod> li> a')
    for li in lis:
        l = pq(li)
        type = l('h4> span').text().strip()
        if type != u"网站" and type != "app":
            continue

        link = l.attr("href").strip()
        if link == "":
            continue

        if type == u"网站":
            type = 4010
            link = util.norm_url(link)
        else:
            continue
            #TODO
            '''
            if link.find("itunes.apple.com") >= 0 and link.find("/app/") >=0:
                type = 4040
                result = util.re_get_result('(id\d*)',link)
                if result is None:
                    continue
                app_id, = result
                link = "https://itunes.apple.com/cn/app/%s" % app_id
            elif link.find("www.wandoujia.com/apps/") >= 0:
                type = 4050
            else:
                continue
            '''

        name = l('h4> b').text().strip()
        desc = l('p').text().strip()
        logger.info("type: %s, name: %s, link: %s, desc: %s" % (type, name,link,desc))
        link = util.norm_url(link)
        artifact = {
            "type":type,
            "name":name,
            "desc":desc,
            "link":link
        }
        artifacts.append(artifact)

    logger.info("")
    return artifacts


def save_footprints(source_company_id, footprints):
    conn = db.connect_torndb()
    for f in footprints:
        fp = conn.get("select * from source_footprint where sourceCompanyId=%s and footDate=%s and description=%s",
                    source_company_id, f["footDate"], f["footDesc"])
        if fp is None:
            conn.insert("insert source_footprint(sourceCompanyId,footDate,description,createTime,modifyTime) \
                        values(%s,%s,%s,now(),now())",
                        source_company_id, f["footDate"], f["footDesc"])
    conn.close()

def parse_footprint(item):
    if item is None:
        return None

    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    footprints = []
    #footprint
    logger.info("*** footprint ***")
    lis = d('ul.list-milestone> li')
    for li in lis:
        l = pq(li)
        footDesc = l('p').eq(0).text().strip()
        if footDesc is None or footDesc == "":
            continue
        footDateText = l('p> span').text().strip()
        if footDateText is None or footDateText == "":
            continue
        result = util.re_get_result('(\d*?)\.(\d*?)$',footDateText)
        if result == None:
            continue
        (year, month) = result
        year = int(year)
        try:
            month = int(month)
        except:
            month = 1

        if month<=0 or month>12:
            month = 1
        if year < 1970 or year > 3000:
            year = 1970
        footDate = datetime.datetime.strptime("%s-%s-1" % (year,month), '%Y-%m-%d')
        logger.info("%s: %s", footDate, footDesc)
        footprint = {"footDate":footDate, "footDesc":footDesc}
        footprints.append(footprint)
    logger.info("")
    return footprints


def save_members(source_company_id, members):
    conn = db.connect_torndb()
    for m in members:
        member_key = m["key"]
        source_member = conn.get("select * from source_member where source=%s and sourceId=%s",
                                                   SOURCE, member_key)
        if source_member is None:
            continue

        source_member_id = source_member["id"]
        source_company_member_rel = conn.get("select * from source_company_member_rel where \
                sourceCompanyId=%s and sourceMemberId=%s",
                source_company_id, source_member_id)
        if source_company_member_rel is None:
            conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                        position,type,createTime,modifyTime) \
                        values(%s,%s,%s,%s, now(),now())",
                        source_company_id, source_member_id,m["position"],0)
    conn.close()

def parse_member(item):
    if item is None:
        return None

    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    members = []
    # members
    logger.info("*** member ****")
    lis = d('ul.list-prodcase> li')
    for li in lis:
        l = pq(li)
        member_name = l('h4> a> b> span.c').text().strip()
        position = l('h4> a> b> span.c-gray').text().strip()
        str = l('h4> a').attr("href").strip()
        (member_key,) = util.re_get_result(r'person/(\d*?)$',str)
        logger.info("member_key: %s, member_name: %s, position: %s" % (member_key, member_name, position))
        member = {
            "key":member_key,
            "name":member_name,
            "position":position
        }
        members.append(member)

    logger.info("")
    return members