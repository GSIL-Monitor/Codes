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
from pyquery import PyQuery as pq

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
loghelper.init_logger("itjuzi_parser", stream=True)
logger = loghelper.get_logger("itjuzi_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)

#mysql
conn = None

# kafka
kafkaProducer = None
kafkaConsumer = None

#
SOURCE=13030

def initKafka():
    global kafkaProducer
    global kafkaConsumer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("crawler_itjuzi_v2", group_id="itjuzi-parser",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')

def parseCompany(source, company_key):
    logger.info("*****************************************")
    logger.info("parseComany, company_key=%s" % company_key)
    try:
        item = fromdb.company.find_one({"source":source, "company_key":company_key})
        if item is None:
            return

        html = item["content"]
        #doc = lxml.html.fromstring(html)
        d = pq(html)

        company_short_name = ""
        product_name = d('div.line-title> span> b').clone().children().remove().end().text().strip()
        temps = product_name.split("/",1)
        if len(temps) == 2:
            product_name = temps[0].strip()
            company_short_name = temps[1].strip()
        if company_short_name == "":
            company_short_name = product_name
        logger.info("product name: " + product_name)
        logger.info("company short name: " + company_short_name)

        company_name = d('div.des-more> div').eq(0).text().strip().replace("公司全称：","")
        if company_name == "暂无" or company_name == "暂未收录":
            company_name = ""
        company_name = util.norm_company_name(company_name)
        logger.info("company name: " + company_name)

        website = d('div.link-line> a.weblink').attr("href").strip()
        if website=="http://%e6%9a%82%e6%97%a0":
            website = ""
        logger.info("website: " + website)

        if company_short_name == "" and company_name == "" and website == "":
            return

        establish_date = None
        str = d('div.des-more> div').eq(1).text().strip().replace("成立时间：","")
        result = util.re_get_result('(\d*?).(\d*?)$',str)
        if result != None:
            (year, month) = result
            establish_date = datetime.datetime.strptime("%s-%s-1" % (year,month), '%Y-%m-%d')
        logger.info("establish date: %s", establish_date)

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
            result = conn.get("select * from location where locationName=%s", city)
            if result != None:
                locationId = result["locationId"]
            else:
                result = conn.get("select * from location where locationName=%s", province)
                if result != None:
                    locationId = result["locationId"]

        logger.info("locationId: %d" % locationId)

        company_status = 2010
        str = d('div.des-more> div').eq(2).text().strip()
        if str == "已关闭":
            company_status = 2020
        logger.info("company_status: %d" % company_status)

        funding_type = 0
        str = d("span.tag.bg-c").text().strip()
        logger.info(str)
        if str == "融资需求 · 需要融资":
            funding_type = 8020
        elif str == "融资需求 · 寻求收购":
            funding_type = 8020
        logger.info("funding_type=%d" % funding_type)

        field = d("span.scope.c-gray-aset> a").eq(0).text().strip()
        logger.info("field: " + field)

        sub_field = d("span.scope.c-gray-aset> a").eq(1).text().strip()
        logger.info("sub field: " + sub_field)

        tags = d("div.tagset.dbi.c-gray-aset> a >span").text().strip().replace(" ",",")
        logger.info(tags)

        desc = d("div.des").text().strip()
        logger.info("desc: " + desc)

        #logo
        logo_id = None
        source_company = conn.get("select * from source_company where source=%s and sourceId=%s", source, company_key)
        if source_company == None or source_company["logo"] == None or source_company["logo"] == "":
            log_url = d("div.pic >img").attr("src")
            if log_url is not None and len(log_url.strip()) > 0:
                logger.info(log_url)
                image_value = my_request.get_image(logger,log_url)
                if image_value != None:
                    logo_id = imgfs.put(image_value, content_type='jpeg', filename='company_%s_%s.jpg' % (source, company_key))
                    pass
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
                        product_name, company_name, desc, '',
                        0,'',company_status,funding_type,locationId,establish_date,logo_id,
                        SOURCE,company_key,
                        field,sub_field,",".join(tags)
                        )
        else:
            source_company_id = source_company["id"]
            conn.update("update source_company set \
                        name=%s,fullName=%s,description=%s, \
                        companyStatus=%s,fundingType=%s,locationId=%s,establishDate=%s,logo=%s, \
                        field=%s,subField=%s,\
                        modifyTime=now() \
                        where id=%s",
                        product_name, company_name, desc,
                        company_status,funding_type,locationId,establish_date,logo_id,
                        field,sub_field,
                        source_company_id
                        )

        #artifact
        logger.info("*** artifact ***")
        lis = d('ul.list-prod> li> a')
        for li in lis:
            l = pq(li)
            type = l('h4> span').text().strip()
            if type == "网站":
                link = l.attr("href").strip()
                name = l('h4> b').text().strip()
                desc = l('p').text().strip()
                logger.info("name: %s, link: %s, desc: %s" % (name,link,desc))
                if link == "":
                    continue
                link = util.norm_url(link)
                source_artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=4010 and link=%s",
                        source_company_id, link)
                if source_artifact is None:
                    sql = "insert source_artifact(sourceCompanyId,`name`,`description`,`link`,`type`,createTime,modifyTime) \
                          values(%s,%s,%s,%s,4010,now(),now())"
                    conn.insert(sql, source_company_id,name,desc,link)

        if website != "":
            source_artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=4010 and link=%s",
                            source_company_id, website)
            if source_artifact is None:
                sql = "insert source_artifact(sourceCompanyId,name,description,link,type,createTime,modifyTime) \
                      values(%s,%s,%s,%s,4010,now(),now())"
                logger.info("name: %s, link: %s, desc: %s" % (product_name,website,desc))
                conn.insert(sql,source_company_id,product_name,desc,website)

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
            logger.info(footDate)
            logger.info(footDesc)

            fp = conn.get("select * from source_footprint where sourceCompanyId=%s and footDate=%s and description=%s",
                              source_company_id, footDate, footDesc)
            if fp == None:
                conn.insert("insert source_footprint(sourceCompanyId,footDate,description,createTime,modifyTime) \
                            values(%s,%s,%s,now(),now())",
                            source_company_id, footDate, footDesc)

        # funding
        logger.info("*** funding ***")
        lis = d('table.list-round-v2> tr')
        for li in lis:
            l = pq(li)
            dateStr = l('td> span.date').text().strip()
            result = util.re_get_result('(\d*?)\.(\d*?)\.(\d*?)$',dateStr)
            fundingDate = None
            if result != None:
                (year, month, day) = result
                fundingDate = datetime.datetime.strptime("%s-%s-%s" % (year,month,day), '%Y-%m-%d')
            logger.info(fundingDate)

            roundStr = l('td.mobile-none> span.round> a').text().strip().replace("轮","")
            logger.info(roundStr)
            fundingRound = 0
            if roundStr.startswith("种子"):
                fundingRound = 1010
                roundStr = "天使"
            elif roundStr.startswith("天使"):
                fundingRound = 1010
            elif roundStr.startswith("Pre-A"):
                fundingRound = 1020
            elif roundStr.startswith("A"):
                fundingRound = 1030
            elif roundStr.startswith("B"):
                fundingRound = 1040
            elif roundStr.startswith("Pre-B"):
                fundingRound = 1040
            elif roundStr.startswith("C"):
                fundingRound = 1050
            elif roundStr.startswith("D"):
                fundingRound = 1060
            elif roundStr.startswith("E"):
                fundingRound = 1070
            elif roundStr.startswith("F"):
                fundingRound = 1100
            elif roundStr.startswith("IPO"):
                fundingRound = 1110
            elif roundStr.startswith("收购"):
                fundingRound = 1120
            logger.info("fundingRound=%d" % fundingRound)

            moneyStr = l('td> span.finades> a').text().strip()
            (currency, investment, precise) = parseMoney(moneyStr)
            logger.info("%s - %s - %s" % (currency, investment, precise))

            source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and roundDesc=%s",
                                          source_company_id, roundStr)
            if source_funding == None:
                source_funding_id = conn.insert("insert source_funding(sourceCompanyId,investment,round,roundDesc, currency, precise, fundingDate,createTime,modifyTime) \
                                                values(%s,%s,%s,%s,%s,%s,%s,now(),now())",
                                                source_company_id, investment, fundingRound, roundStr,
                                                currency, precise,fundingDate)
            else:
                source_funding_id = source_funding["id"]
                conn.update("update source_funding set investment=%s,currency=%s, precise=%s, fundingDate=%s, modifyTime=now() \
                            where id=%s",
                            investment, currency, precise, fundingDate, source_funding_id
                                )

            hs = l('td:eq(3)> a')
            for h in hs:
                h = pq(h)
                investor_name = h.text().strip()
                investor_url = h.attr("href").strip()
                (investor_key,) = util.re_get_result(r"http://www.itjuzi.com/investfirm/(\d*)$", investor_url)
                logger.info(investor_name)
                logger.info(investor_url)
                logger.info(investor_key)

                item = fromdb.investor.find_one({"source":source, "investor_key":investor_key})
                inv = parseInvestor(item)

                if inv is not None:
                    (name, logo, website, stage, field, desc) = inv
                    source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                                               source, investor_key)
                    logo_id = None
                    if source_investor == None or source_investor["logo"] == None or source_investor["logo"] == "":
                        if logo is not None and logo != "":
                            image_value = my_request.get_image(logger,logo)
                            logo_id = imgfs.put(image_value, content_type='jpeg', filename='investor_%s_%s.jpg' % (source, investor_key))
                            logger.info("gridfs logo_id=%s" % logo_id)
                    else:
                        logo_id = source_investor["logo"]

                    if source_investor is None:
                        sql = "insert source_investor(name,website,description,logo,stage,field,type, \
                        source,sourceId,createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
                        source_investor_id = conn.insert(sql,
                            name,website,desc,logo_id,stage,field,10020,source,investor_key)
                    else:
                        source_investor_id = source_investor["id"]
                        sql = "update source_investor set name=%s,website=%s,description=%s,logo=%s,stage=%s,\
                        field=%s,type=%s,modifyTime=now() where id=%s"
                        conn.update(sql,
                            name,website,desc,logo_id,stage,field,10020, source_investor_id)

                    source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where \
                            sourceFundingId=%s and sourceInvestorId=%s",
                            source_funding_id, source_investor_id)
                    if source_funding_investor_rel is None:
                        conn.insert("insert source_funding_investor_rel(sourceFundingId, sourceInvestorId, \
                                    createTime,modifyTime) \
                                    values(%s,%s, now(),now())", source_funding_id, source_investor_id)

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

            item = fromdb.member.find_one({"source":source, "member_key":member_key})
            m = parseMember(item)

            if m is not None:
                (weibo, introduction, education, work, location, role, pictureUrl) = m

                source_member = conn.get("select * from source_member where source=%s and sourceId=%s",
                                                   source, member_key)
                logo_id = None
                if source_member == None or source_member["photo"] == None or source_member["photo"] == "":
                    if pictureUrl is not None and pictureUrl != "":
                        image_value = my_request.get_image(logger,pictureUrl)
                        logo_id = imgfs.put(image_value, content_type='jpeg', filename='member_%s_%s.jpg' % (source, member_key))
                        logger.info("gridfs logo_id=%s" % logo_id)
                else:
                    logo_id = source_member["photo"]

                if source_member is None:
                    sql = "insert source_member(name,photo,weibo,location,role,description,\
                    education,work,source,sourceId,createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
                    source_member_id = conn.insert(sql,
                        member_name,logo_id,weibo,location,role,introduction,
                        education,work,source,member_key)
                else:
                    source_member_id = source_member["id"]
                    sql = "update source_member set name=%s,photo=%s,weibo=%s,location=%s,role=%s,description=%s,\
                    education=%s,work=%s,modifyTime=now() where id=%s"
                    conn.update(sql,
                        member_name,logo_id,weibo,location,role,introduction,
                        education,work,source_member_id)

                source_company_member_rel = conn.get("select * from source_company_member_rel where \
                        sourceCompanyId=%s and sourceMemberId=%s",
                        source_company_id, source_member_id)
                if source_company_member_rel is None:
                    conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                                position,type,createTime,modifyTime) \
                                values(%s,%s,%s,%s, now(),now())",
                                source_company_id, source_member_id,position,0)

        #news
        logger.info("*** news ***")
        lis = d('ul.list-news> li')
        for li in lis:
            try:
                l = pq(li)
                news_url = l('p.title> a').attr("href").strip()
                (news_key,) = util.re_get_result(r"http://www.itjuzi.com/overview/news/(\d*)$", news_url)

                item = fromdb.news.find_one({"source":source, "company_key":company_key, "news_key":news_key})
                parseNews(item)
            except Exception,ex:
                logger.exception(ex)

        msg = {"type":"company", "id":source_company_id}
        kafkaProducer.send_messages("parser_v2", json.dumps(msg))
    except Exception,ex:
        logger.exception(ex)

def parseInvestor(item):
    if item is None:
        return None

    investor_key = item["investor_key"]
    investor_name = item["investor_name"]

    html = item["content"]
    #logger.info(html)
    d = pq(html)
    name = d('div.picinfo> p> span.title').text().strip()
    logger.info("investor_name: " + name)

    if name != investor_name:
        logger.info("Investor name error!!!!!!!!!!!!!!!!")
        return None

    logo = d('div.pic> img').attr("src").strip().replace("https://","http://")
    logger.info("Investor Logo: %s" % logo)

    website = d('span.links >a[target="_black"]').attr("href").strip()
    if website == "暂无":
        website = ""
    logger.info("Investor website: %s" % website)

    stageStr = d('div.pad.block> div.list-tags.yellow').text().replace(" ",",").strip()
    logger.info("Investor rounds: %s" % stageStr)

    fieldsStr = d('div.pad.block> div.list-tags.darkblue').text().replace(" ",",").strip()
    logger.info("Investor fields: %s" % fieldsStr)

    desc = d('div.des').text().strip()
    logger.info("Investor desc: %s" % desc)

    return (name, logo, website, stageStr, fieldsStr, desc)

def parseMember(item):
    if item is None:
        return None
    try:
        html = item["content"]
        d = pq(html)

        weibo = d('div.bottom-links> a').attr("href")
        if weibo is None:
            weibo = ""
        weibo = weibo.strip()
        logger.info("weibo: " + weibo)

        introduction = d('div.block-v').text().strip()
        logger.info("introduction: " + introduction)

        sec = d('i.fa-briefcase').parents("div.sec")
        work = pq(sec)('div.wp100> ul> li> span> span> a').text().strip()
        logger.info("work: " + work)

        sec = d('i.fa-book').parents("div.sec")
        education = pq(sec)('div.wp100> ul> li> span> span.right> a').text().strip()
        logger.info("education: " + education)

        sec = d('i.fa-map-marker').parents("p")
        location = pq(sec).text().strip()
        logger.info("location: " + location)

        role = d('span.bg-blue').text().strip()
        logger.info("role: " + role)

        pictureUrl = d('div.infohead-person> div> div> p> span> img').attr("src").replace("https://","http://").strip()
        logger.info("picture url: " + pictureUrl)

        return (weibo, introduction, education, work, location, role, pictureUrl)
    except Exception,ex:
        logger.exception(ex)

    return None


def parseNews(item):
    if item is None:
        return None

    try:
        company_key = item["company_key"]
        news_key = item["news_key"]
        url = item["url"]
        news_source_domain = item["news_source_domain"]
        news_date = item["news_date"]
        html = item["content"]

        if html.find("404未找到页面") != -1:
            logger.info("404未找到页面")
            return None

        if fromdb.source_news.find_one({"source":item["source"],"company_key":company_key,"news_key":news_key}) == None:
            contents = extract.extractContents(item["url"], html)
            data = {"source":item["source"], "news_key":news_key, "company_key":company_key,
                    "url":url, "title":item["news_title"],"source_domain":news_source_domain,
                    "date":news_date, "contents":contents}
            fromdb.source_news.insert_one(data)
    except Exception,ex:
        logger.exception(ex)

def parseMoney(moneyStr):
    investment = 0
    currency = 3020
    precise = 'Y'

    investmentStr = ""

    if investment == 0:
        result = util.re_get_result(u'(数.*?)万人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000
            elif investmentStr == u"数十":
                investment = 10*10000
            elif investmentStr == u"数百":
                investment = 100*10000
            elif investmentStr == u"数千":
                investment = 1000*10000

    if investment == 0:
        result = util.re_get_result(u'(数.*?)亿人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000*10000
            elif investmentStr == u"数十":
                investment = 10*10000*10000
            elif investmentStr == u"数百":
                investment = 100*10000*10000
            elif investmentStr == u"数千":
                investment = 1000*10000*10000

    if investment == 0:
        result = util.re_get_result(u'(\d*?)万人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(investmentStr) * 10000
        else:
            result = util.re_get_result(u'(\d*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(investmentStr) * 10000

    if investment == 0:
        result = util.re_get_result(u'(\d*?)亿人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(investmentStr) * 100000000
        else:
            result = util.re_get_result(u'(\d*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(investmentStr) * 100000000

    if investment == 0:
        result = util.re_get_result(u'亿元及以上美元',moneyStr)
        if result != None:
            currency = 3020
            investment = 100000000
            precise = 'N'
        else:
            result = util.re_get_result(u'亿元及以上人民币',moneyStr)
            if result != None:
                currency = 3010
                investment = 100000000
                precise = 'N'

    return (currency, investment, precise)

if __name__ == '__main__':
    logger.info("itjuzi-parser start")
    initKafka()

    while True:
        try:
            for message in kafkaConsumer:
                try:
                    conn = db.connect_torndb()
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    #{"source": 13020, "type": "company", "company_key": "158523"}
                    source = msg["source"]
                    type = msg["type"]
                    company_key = msg["company_key"]

                    if type == "company":
                        if source == SOURCE:
                            parseCompany(source, company_key)
                except Exception,e :
                    logger.exception(e)
                finally:
                    kafkaConsumer.task_done(message)
                    kafkaConsumer.commit()
                    conn.close()
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            initKafka()
