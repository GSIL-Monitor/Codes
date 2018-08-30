# -*- coding: utf-8 -*-

import sys,os
from pymongo import MongoClient
import pymongo
from kafka import KafkaClient, KafkaConsumer, SimpleProducer


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../nlp'))

import config
import loghelper
import my_request
import util
import db
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import time, re, random

from StringIO import StringIO
import requests
from PIL import Image
import gridfs
import json

import trends_tool
import traceback


from score.relatedness_old import RelatednessScorer
try:
    rs = RelatednessScorer()
except:
    traceback.print_exc()

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)

#logger
loghelper.init_logger("aggregator_util", stream=True)
logger = loghelper.get_logger("aggregator_util")

def aggregator_init(spider_name):
    msg_name = "parser_v2"
    #logger
    loghelper.init_logger("aggregator("+spider_name+")", stream=True)
    logger = loghelper.get_logger("aggregator("+spider_name+")")

    mysqldb = db.connect_torndb()


    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafka_producer = SimpleProducer(kafka)
    kafka_consumer = KafkaConsumer(msg_name, group_id="aggregator_"+spider_name,
                                  metadata_broker_list=[url],
                                  auto_offset_reset='smallest')

    return logger, fromdb, mysqldb, kafka_producer, kafka_consumer






def match_company(source, sourceId):
    conn = db.connect_torndb()
    sql = 'select  * from source_company where source= %s and sourceId = %s'
    result = conn.get(sql, source, sourceId)
    if result is None:
        return

    # get companyId


    return True



def insert_company(source, sourceId, conn):
    cursor = conn.cursor()
    sql = 'select  * from source_company where source= %s and sourceId = %s'
    cursor.execute(sql, source, sourceId)
    result = cursor.fetchone()


def get_company_code(name):
    conn = db.connect_torndb()
    datestring = "%s" % time.strftime("%Y%m%d%H%M%S", time.localtime())

    if len(name) <8 :
        pinyin = lazy_pinyin(name.decode('utf-8'))
        company_code = ''.join(pinyin)
    else:
        pinyin = lazy_pinyin(name.decode('utf-8'), style=pypinyin.INITIALS)
        company_code = ''.join(pinyin)

    bs = bytes(company_code)
    st = ''
    for b in bs:
        if re.match('-|[0-9a-zA-Z]', b):
            st +=b
    company_code = st

    if len(company_code) >31:
        company_code = company_code[0:30]

    if len(company_code) < 3:
        company_code = company_code+str(random.randint(1, 100))

    sql = 'select code from company where code = %s'
    result = conn.get(sql, company_code)
    if result != None:
        code = company_code + datestring[4:]
        result2 = conn.get(sql, code)
        if result2 != None:
            company_code = company_code + datestring
        else:
            company_code = code

    conn.close()
    return company_code



def insert_news(item, company_id):

    conn = db.connect_torndb_crawler()
    date = item["date"]

    table_id = get_company_table(conn, company_id)

    result = conn.get("select id, date from news"+table_id+" where companyId=%s and title=%s limit 1", company_id, item["title"])
    if result != None:
        if result['date'] == None:
            conn.update("update news"+table_id+" set date= %s where id=%s", result["date"], result["id"])
        return

    if item["domainId"] == None:
        item["domainId"] = 0


    sql = "insert news"+table_id+"(companyId, date, title, link, domainId, createTime) values(%s,%s,%s,%s,%s, now())"
    newsId = conn.insert(sql, company_id, date, item["title"], item["url"], item["domainId"])

    today =  "%s" %time.strftime("%Y-%m-%d", time.localtime())

    if date != None:
        if today in date:
            sql = "insert news_latest(companyId,newsId,newsTable,date,createTime) values(%s,%s,%s,%s, now())"
            conn.insert(sql, company_id, newsId, table_id, date)


    index = 1
    for c in item["contents"]:
        content = ""
        image_id = ""
        if c["type"] == "text":
            content = c["data"]
        if c["type"] == "img":
            imageUrl = c["data"]
            try:
                r = requests.get(imageUrl, timeout=60)
                img = Image.open(StringIO(r.content))
                (width,height) = img.size
                if width > 640:
                    ratio = 640.0/width
                    img = img.resize( (int(width*ratio),int(height*ratio)), Image.ANTIALIAS)

                output = StringIO()
                img.save(output, format='jpeg')
                image_id = imgfs.put(output.getvalue(), content_type='jpeg', filename='news.jpg')
            except:
                pass

        sql = "insert news_content"+table_id+"(newsId,content,image,rank) values(%s,%s,%s,%s)"
        conn.insert(sql, newsId, content, image_id, index)
        index +=1

    conn.close()

def get_table_id(companyId, tableNum):
    tableid = int(companyId)%tableNum
    if tableid == 0:
        tableid = tableNum
    return tableid


def get_company_table(conn, company_id):
    sql = "select * from company_index where companyId=%s"
    index = conn.get(sql, company_id)
    if index == None:
        table_id = get_table_id(company_id, 100)

        sql = "insert into company_index(companyId, news) values(%s, %s)"
        conn.insert(sql, company_id, table_id)

    else:
        table_id = index["news"]
        if table_id == None:
            table_id = get_table_id(company_id, 100)
            sql = "update company_index set news=%s where companyId=%s"
            conn.update(sql, table_id, company_id)

    table_id = str(table_id)
    return table_id


def get_android_table_id(conn, company_id):
    sql = "select * from company_index where companyId=%s"
    index = conn.get(sql, company_id)
    if index == None:
        table_id = get_table_id(company_id, 100)
        sql = "insert into company_index(companyId, android) values(%s, %s)"
        conn.insert(sql, company_id, table_id)
    else:
        table_id = index["android"]
        if table_id == None:
            table_id = get_table_id(company_id, 100)
            sql = "update company_index set android=%s where companyId=%s"
            conn.update(sql, table_id, company_id)
    table_id = str(table_id)
    return table_id


def get_ios_table_id(conn, company_id):
    sql = "select * from company_index where companyId=%s"
    index = conn.get(sql, company_id)
    if index == None:
        table_id = get_table_id(company_id, 100)
        sql = "insert into company_index(companyId, ios) values(%s, %s)"
        conn.insert(sql, company_id, table_id)
    else:
        table_id = index["ios"]
        if table_id == None:
            table_id = get_table_id(company_id, 100)
            sql = "update company_index set ios=%s where companyId=%s"
            conn.update(sql, table_id, company_id)
    table_id = str(table_id)
    return table_id


################  merge ################
def merge_news(source_company_id, company_id, conn):
    result = conn.get('select * from source_company where id = %s', source_company_id)
    source = result["source"]
    company_key = result['sourceId']
    result = fromdb.source_news.find({"source":source,"company_key":company_key})

    if result is not None:
        for news in result:

            if news.get('site_name'):
                site_name = news['site_name']
            else:
                site_name = None

            contents = news['contents']

            contentStr = ''
            for c in contents:
                if c['type'] == 'text':
                    contentStr += c['data']

            if news.has_key("news_date"):
                thedate = news["news_date"]
            else:
                thedate = news["date"]

            compare = { 'title' : news['title'],
                     'url': news['url'],
                     'date': thedate,
                     'content': contentStr,
                     'sitename': site_name
                   }

            try:
                flag, domain_id = rs.compare(company_id, **compare)
                logger.info(flag)
                logger.info(domain_id)

                news = { 'title' : news['title'],
                         'url': news['url'],
                         'date': thedate,
                         'contents': contents,
                         'domainId': domain_id
                       }
                if source == 13080 or source == 13081:
                    if flag:
                        insert_news(news, company_id)
                else:
                    insert_news(news, company_id)
            except:
                traceback.print_exc()




def merge_job(source_company_id, company_id, conn):
    jobs = conn.query('select * from source_job where sourceCompanyId = %s', source_company_id)
    if jobs is not None:
        for job in jobs:
            sql = 'select * from job where companyId=%s and position=%s  and startDate=%s'
            result = conn.get(sql, company_id, job['position'], job['startDate'])
            if result is None:
                sql = 'insert job(companyId, position, salary, description, domain,' \
                      ' locationId, educationType, workYearType, startDate, updateDate,' \
                      'createTime) values(' \
                      '%s, %s, %s, %s, %s,' \
                      '%s, %s, %s, %s, %s,' \
                      'now())'
                job_id = conn.insert(sql, company_id, job['position'], job['salary'], job['description'], job['domain'],
                        job['locationId'], job['educationType'], job['workYearType'], job['startDate'], job['updateDate'])
            else:
                job_id = result['id']
                sql = 'update job set updateDate = %s where id =%s'
                conn.update(sql, result['updateDate'], job_id)

            conn.update('update source_job set jobId = %s where id=%s', job_id, job['id'])



###### merge artifact #######
def merge_weibo(company_id, name, full_name, conn):
    weibos = trends_tool.find_weibo(name)
    handle_weibo(company_id, weibos, conn)

    weibos = trends_tool.find_weibo(full_name)
    handle_weibo(company_id, weibos, conn)


def handle_weibo(company_id, weibos, conn):
    type = 4030
    if weibos is None:
        return

    for weibo in weibos:
        other = {'location': weibo['location'], 'follow': weibo['follow'], 'fans': weibo['fans'], 'msg': weibo['publish']}
        other = json.dumps(other)
        result = conn.get('select * from artifact where companyId=%s and type=%s', company_id, type)
        if result is None:
            sql = 'insert artifact(companyId, name, description, link, type,' \
                  ' tags, other, active, createTime) values(' \
                  '%s, %s, %s, %s, %s,' \
                  '%s, %s, %s, now())'

            conn.insert(sql, company_id, weibo['name'], weibo['desc'], weibo['link'], type,
                        weibo['tags'], other, 'Y')

        else:
            sql = 'update artifact set description=%s, link=%s, other=%s where id=%s'
            conn.update(sql, weibo['desc'], weibo['link'], other, result['id'])


def merge_wechat(company_id, name, full_name, conn):
    type = 4020
    wechats = trends_tool.find_wechat(name, full_name)
    if wechats is None:
        return

    for wechat in wechats:
        result = conn.get('select * from artifact where companyId=%s and type=%s', company_id, type)
        if result is None:
            sql = 'insert artifact(companyId, name, description, link, type,' \
                  ' tags, other, active, createTime) values(' \
                  '%s, %s, %s, %s, %s,' \
                  '%s, %s, %s, now())'
            conn.insert(sql, company_id, wechat['name'], wechat['brief'], wechat['id'], type,
                        '', '', 'Y')
        else:
            sql = 'update artifact set description=%s, link=%s where id=%s'
            conn.update(sql, wechat['brief'], wechat['id'], result['id'])









