# -*- coding: utf-8 -*-
import sys, os
import datetime, time
import json, re

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper
import simhash

# logger
loghelper.init_logger("artifact_assign", stream=True)
logger = loghelper.get_logger("artifact_assign")

'''company artifactid newsid

return {{news},{artifact}}

'''


def getArtiStr_mongo(aid):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    sql = 'select id,type,link,domain from artifact where id=%s' % aid
    result = conn.query(sql)
    aType, link, domain = result[0]['type'], result[0]['link'], result[0]['domain']
    str = ''
    if aType == 4010:
        collection = mongo.info.website
        result = collection.find_one({'url': link})
        if result is None:
            return ''
        else:
            str += result['title'] * 10 + result['description']
    elif aType == 4040:
        collection = mongo.market.itunes
        trackId = int(re.findall('id(\d+)', link)[0])
        result = collection.find_one({'$or': [{'trackId': trackId}, {'link': link}]})
        if result is None:
            return ''
        else:
            str += result['trackName'] * 10 + result['description']
    elif aType == 4050:
        collection = mongo.market.android
        result = collection.find_one({'$or': [{'apkname': domain}, {'link': link}]})
        if result is None:
            return ''
        else:
            str += result['title'] * 10 + result['description']

    conn.close()
    mongo.close()
    return str


def getArtiStr(aid):
    conn = db.connect_torndb()
    sql = 'select * from artifact where id=%s' % aid
    result = conn.query(sql)[0]
    conn.close()
    str = ''
    if result['name'] is not None:
        str += result['name'] * 10
    if result['description'] is not None:
        str += result['description']
    # if str=='':
    #     str=getArtiStr_mongo(aid)
    return str


def getNewsStr(nid):
    mongo = db.connect_mongo()
    collection = mongo.article.news
    result = collection.find_one({'_id': nid})
    str = result['title'] * 10
    for c in result['contents']:
        if c['content'] is not None and c['content'] != '':
            str += c['content']
    return str


def getComStr(cid):
    conn = db.connect_torndb()
    sql = 'select * from company where id=%s' % cid
    result = conn.query(sql)[0]
    conn.close()
    str = result['name'] * 10 + result['description']
    return str


def resort(companies, artifacts, news):
    dic = {'artifact': {}, 'news': {}}
    for a in artifacts:
        str_a = getArtiStr(a)
        simhash_a = simhash.Simhash(simhash.get_features(str_a))
        minDistance = 99999999
        minCompany = ''
        for c in companies:
            str_c = getComStr(c)
            simhash_c = simhash.Simhash(simhash.get_features(str_c))
            distance = simhash_a.distance(simhash_c)
            if distance < minDistance:
                minDistance = distance
                minCompany = c
        dic['artifact'][a] = minCompany

    for n in news:
        str_a = getNewsStr(n)
        simhash_a = simhash.Simhash(simhash.get_features(str_a))
        minDistance = 99999999
        minCompany = ''
        for c in companies:
            str_c = getComStr(c)
            simhash_c = simhash.Simhash(simhash.get_features(str_c))
            distance = simhash_a.distance(simhash_c)
            if distance < minDistance:
                minDistance = distance
                minCompany = c
        dic['news'][n] = minCompany

    return dic


def run_111():
    def get_artifacts(companyIds):
        conn = db.connect_torndb()
        artifacts = conn.query("select * from artifact where companyId in %s and (active is null or active='Y')",
                               companyIds)
        conn.close()
        artifact_ids = [int(a["id"]) for a in artifacts]
        return artifact_ids

    def get_news(companyIds):
        mongo = db.connect_mongo()
        collection = mongo.article.news
        news = list(
            collection.find({'$or': [{'companyIds': {'$in': companyIds}}, {'companyId': {'$in': companyIds}}]}))
        news_ids=[i['_id'] for i in news]
        return news_ids

    companies = [1047, 11388]
    artifacts = get_artifacts(companies)
    news = get_news(companies)
    return resort(companies, artifacts, news)

def tes():
    a = '车牛是大搜车打造的一款专为中小车商服务的APP。自2014年初上线以来，车牛已经累积了20万车商用户，占二手车行业从业人员总量的80%以上。每天10000多台的新增车源，占全网商品发布量的30%以上。每日上万新增优质车源，二手车行情一手掌握；一键推广车辆信息到30多个网站，客源轻松找上门；更有二手车估价、违章查询、限迁查询、车牌查询、车管所查询、二手车物流查询等实用工具。车商可以在车牛高效的完成线上营销、收车、卖车等工作。同时，车牛还提供异地验车、担保交易、金融贷款、质保服务，解决车况不透明、支付不安全和资金周转等核心问题，让车商收车更放心，卖车更省心！车牛，您的二手车经营好伙伴！'
    b = '大搜车'
    c = '大V店'

    def sim(str):
        return simhash.Simhash(simhash.get_features(str))

    simhash_a = sim(a)
    simhash_b = sim(b)
    simhash_c = sim(c)


if __name__ == "__main__":
    logger.info("Start...")
    run_111()
