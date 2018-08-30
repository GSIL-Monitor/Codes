# -*- coding: utf-8 -*-
import random, math
import os, sys, datetime, re, json, time
import xlwt
import requests
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download, traceback_decorator, email_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# logger
loghelper.init_logger("crawler_jingdata_incr", stream=True)
logger = loghelper.get_logger("crawler_jingdata_incr")

def get_proxy(http_type='http'):
    """
    获取可以访问的ip
    """

    proxy = {'type': http_type, 'anonymity': 'high'}
    url = "https://www.jingdata.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    timeout = 5
    while True:
        logger.info("Start proxy_pool.get_single_proxy")
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            logger.info("proxy_pool.get_single_proxy return None")
            continue
        proxies = {
            'http': proxy_ip['ip:port']
        }
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('var UA') >= 0:
                logger.info('ip:%s for jingdata' % proxy_ip['ip:port'])
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)


def parser(res):
    mongo = db.connect_mongo()
    collection = mongo.raw.jingdata_rz_incr
    items = res['data']['item']
    for item in items:
        data = item['data']
        date = item.get('dateStr')
        Date = ''
        if date is None or re.match("\d{2}:\d{2}", date):
            Date = datetime.date.today().strftime('%Y-%m-%d')
        elif re.match("\d{2}-\d{2}", date):
            Date = str(time.localtime()[0]) + '-' + date
        item['Date'] = Date
        seq = item['seq']
        type = item['type']
        data['date'] = date
        data['Date'] = Date
        data['seq'] = seq
        data['type'] = type
        data['createtime'] = datetime.datetime.now()
        data['modifytime'] = datetime.datetime.now()
        # logger.info(json.dumps(data,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
        product = data['name']
        lunci = data['phase']
        link = data['link']
        try:
            ex_item = collection.find_one({'name': product, 'phase': lunci})
            if ex_item is not None:
                if ex_item['link'] == link:
                    logger.info('no change')
                    mongo.close()
                    continue
                collection.delete_one({'name': product, 'phase': lunci})
                logger.info(
                    'product:%s lunci:%s old source:%s ---> new source:%s ' % (
                    product, lunci, ex_item['link'], link))
            collection.insert_one(data)
            logger.info('insert product:%s lunci:%s done ' % (product, lunci))
        except Exception, e:
            logger.info('mongo error:%s' % e)

def to_cralw():
    i = 0
    proxies = get_proxy(http_type='https')
    while True:
        while i > 3:
            proxies = get_proxy(http_type='https')
            i = 0
        url = 'https://rong.36kr.com/api/mobi-investor/company/finance-new/group/v4?seq=&pageSize=20'
        headers = {'User-Agent': '36kr-Tou-Android/4.1.0 (MIX 2; Android 8.0.0; Scale/2030x1080)',
                   'Host': 'rong.36kr.com'}
        logger.info('start to crawl ')

        try:
            time.sleep(5)
            r = requests.get(url,headers=headers,timeout=5,proxies=proxies)
            res = json.loads(r.text)
            if res is None or res.get('msg')!= '操作成功！':
                continue
            if res.get('code') == 0:
                parser(res)
                return 1
            else:
                logger.info('wrong msg:%s' % r.text)
                return 0

        except Exception,e:
            logger.info('requests error:%s'%e)
            i += 1

def wait_time(f):
    def to_go(*args, **kwargs):
        hours = [8, 13, 16, 20]
        hour = time.localtime()[3]
        if hour in hours:
            f(*args, **kwargs)
    return to_go


@traceback_decorator.try_except
def run():
    i = 0
    while True:
        if i >= 5:
            raise ValueError('five times got wrong response')
        flag = to_cralw()
        if flag == 0:
            i += 1
            continue
        logger.info('sleeping')
        time.sleep(60*60)


if __name__ == '__main__':
    run()