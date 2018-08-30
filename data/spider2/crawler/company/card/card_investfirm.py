# -*- coding: utf-8 -*-
import random, math
import os, sys, datetime, re, json, time
import xlwt
import requests
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading
from get_card_data import TransformMd5, get_proxy

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download, traceback_decorator, email_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# logger
loghelper.init_logger("crawler_qmp_investfirm", stream=True)
logger = loghelper.get_logger("crawler_qmp_investfirm")

def make_payload(id,ticket,unionid,year=None):

    payload = {
        'src':'magic',
        'ticket':ticket,
        'id':id,
        'page':1,
        'num':50,
        'hangye':'',
        'time':year,
        'ptype':'qmp_pc',
        'version':2.0,
        'unionid':unionid,
        'jtype':'vip',
        'time_token':''
    }
    return payload

def to_crawl(headers,postdata,item,first=True,timeout=5):
    retry = 0
    while True:
        logger.info('retry:%d'%retry)
        proxies = item[1]
        if retry >= 3:
            proxies = get_proxy()
            item = (item[0],proxies)
            save_unionid_item(item)
            logger.info('retry>3 new proxies item here')
            logger.info(item)
            continue
        try:
            url = 'http://vip.api.qimingpian.com/d/j3tz_touzi2'
            r = requests.post(url, headers=headers, data=postdata, proxies=proxies, timeout=timeout)
            res = json.loads(r.text)
            if res.has_key('status') and res['status'] != 0:
                logger.info('**********')
                logger.info(r.text)
                logger.info('**********')
                save_unionid_item(item,active=0)
                item = get_unionid_item()
                logger.info('bad status--->change new item')
                logger.info(item)
                continue
            data1 = res['data1']
            md = TransformMd5()
            data = md.run(data1)
            data = json.loads(data)
            return data, item
        except Exception,e:
            logger.info('to_cralw request error:%s'%e)
            retry += 1

def save_unionid_item(item,active=1):
    unionid = item[0]
    proxies = item[1]
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_id
    try:
        record = collection.find_one({'unionid': unionid})
        if active == 1:
            if proxies != record['proxy']:
                collection.update({'unionid': unionid},{'$set':{'proxy':proxies}})
        else:
            collection.update({'unionid':unionid},{'$set':{'active':0}})
    except Exception,e:
        logger.info(e)
        logger.info('mongo error')
    mongo.close()

def get_unionid_item():
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_id
    try:
        item = collection.find_one({'active': 1, 'used': 0})
        if item is None:
            logger.info('no unionid can use.')
            return None, None
        unionid = item.get('unionid')
        proxies = item.get('proxy')
        if proxies is None:
            proxies = get_proxy()
        mongo.close()
        return unionid,proxies
    except Exception, E:
        logger.info(E)
        logger.info('mongo error')
        mongo.close()

def request_prepare(url,item,year=None):
    p = re.search(r'ticket=(.*?)&id=(.*)', url)
    ticket = p.groups()[0]
    id = p.groups()[1]
    unionid = item[0]
    postdata = make_payload(id, ticket,unionid,year=year)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    return headers, postdata

def save_data(investor,data,year):
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_tz
    data.update({'investor':investor})
    data.update({'year':year})
    try:
        collection.insert_one(data)
        logger.info('save investor:%s | year:%s data done'%(data,year))
    except Exception,e:
        logger.info('mongo error:%s' % e)
    mongo.close()


def save(data, investor): # todo 将investor换为 id 和 ticket
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_tz_parser
    tzs = data['touzi1']
    # cnt = 0
    # for tz in tzs:
    #     try:
    #         product = tz['product']
    #         lunci = tz['lunci']
    #         record = collection.find_one({'product':product, 'lunci':lunci, 'investor':investor})
    #         if record is None:
    #             tz.update({'investor':investor})
    #             collection.insert_one(tz)
    #         cnt += 1
    #     except Exception,e:
    #         logger.info('mongo error:%s'%e)
    # mongo.close()
    # return cnt

def run():
    urls = ['http://vip.qimingpian.com/#/detailorg?src=magic&ticket=89c8dd468c6553ceacc01a3a2d4b7488&id=00981f03342bf67cd235a5c84c3f6263']
    item = get_unionid_item()
    logger.info(item)
    # todo item 使用次数 , save_unionid_item used=1
    for url in urls:
        headers, postdata = request_prepare(url,item)
        data, item = to_crawl(headers,postdata,item)
        year_count = data['year_count_total']
        investor = ''
        for t in data['touzi1']:
            if t['tzr'].find('、') < 0:
                investor = t['tzr']
                break
        logger.info('start to crawl investor:%s'%investor)

        # 判断 如果 所有投资事件数目不大于50 则直接保存
        if year_count[0]['count'] <= 50:
            save_data(investor,data,'all')
            cnt = save(data, investor)
            logger.info('investor:%s all tz events:%s save done'%(investor,cnt))
            continue

        gg = 1
        for year in year_count[1:]:
            if year['count'] > 50:
                gg = 0
        if gg == 0:
            # 将此tz机构的url记录
            # todo
            continue

        # 对总数目超过50单个年份小于50的进行分类处理
        for y_count in year_count[1:]:
            year = y_count['name']
            headers2, postdata2 = request_prepare(url, item, year=year)
            data2, item = to_crawl(headers2,postdata2,item)
            save_data(investor,data2,year)
            cnt2 = save(data2,investor)
            logger.info('investor:%s | year:%s tz events:%s save done' % (investor, year, cnt2))





if __name__ == '__main__':
    print(920+ 1264)
    # run()