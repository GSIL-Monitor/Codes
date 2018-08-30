# -*- coding: utf-8 -*-
import random, math
import os, sys, datetime, re, json, time
import xlwt
import requests
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading
from card_prepare import save_dates, save_unionid
from get_card_data import TransformMd5, get_proxy

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download, traceback_decorator, email_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# logger
loghelper.init_logger("crawler_qmp_incr", stream=True)
logger = loghelper.get_logger("crawler_qmp_incr")


def make_payload():
    # area = ['国内', '国外'][random.randint(0, 1)]
    payload = {
        'area': '国内',
        'page': 1,
        'page_num': 50,
        'debug': 1,
        'tag': '',
        'event': '',
        'version': '1.2.4',
        'ptype': 'qmo_android',
        # '-':1530154931066
    }
    return json.dumps(payload)


def wait_time(f):
    def to_go(*args, **kwargs):
        hours = [8, 13, 16, 20]
        hour = time.localtime()[3]
        if hour in hours:
            f(*args, **kwargs)
    return to_go


def to_crawler(proxies):
    i = 0
    while True:
        while i > 3:
            proxies = get_proxy()
            i = 0
        url = 'http://az.api.qimingpian.com/h/newrongzi3Is'
        headers = {
            'User-Agent': 'okhttp/3.6.0',
            'Host': 'az.api.qimingpian.com',
        }
        postdata = make_payload()
        logger.info('start to crawl ')
        try:
            time.sleep(5)
            r = requests.post(url, headers=headers, data=postdata, timeout=5, proxies=proxies)
            if r.text is None:
                continue
            res = json.loads(r.text)
            if res.has_key('status') and res['status'] == 0:
                data1 = res['data1']
                # print(data1)
                md = TransformMd5()
                data = md.run(data1)
                data = json.loads(data)
                return data, proxies
            else:
                logger.info('wrong msg:%s' % r.text)
                return None, proxies
        except Exception, e:
            logger.info('requests error:%s' % e)
            i += 1


def parser(item):
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_rz_incr
    # date = item.get('date')
    # if date is None or re.match("\d{2}:\d{2}", date):
    #     date = datetime.date.today().strftime('%Y-%m-%d')
    # elif date == '昨天':
    #     date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    # item['Date'] = date
    lunci = item['lunci']
    product = item['product']
    source = item['qmp_url'] # qmp 改版 没有source 字段 改用qmp_url
    item['createtime'] = datetime.datetime.now()
    item['modifytime'] = datetime.datetime.now()
    # logger.info(json.dumps(item,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    try:
        ex_item = collection.find_one({'product': product, 'lunci': lunci})
        if ex_item is not None:
            if ex_item['qmp_url'] == source:
                logger.info('no change')
                mongo.close()
                return
            collection.delete_one({'product': product, 'lunci': lunci})
            logger.info(
                'product:%s lunci:%s old source:%s ---> new source:%s ' % (product, lunci, ex_item['source'], source))
        collection.insert_one(item)
        logger.info('insert product:%s lunci:%s done ' % (product, lunci))
    except Exception, e:
        logger.info('mongo error:%s' % e)


@traceback_decorator.try_except
def run():
    while True:
        # countries = ['国内','国外']
        proxies = get_proxy()
        # for country in countries:
        data, proxies = to_crawler(proxies)
        if data is None or data.has_key('list') is False or len(data['list']) == 0:
            continue
        rz_list = data['list']
        for rz_item in rz_list:
            parser(rz_item)
        time.sleep(60 * 60)


if __name__ == '__main__':
    run()
    # send_email()
