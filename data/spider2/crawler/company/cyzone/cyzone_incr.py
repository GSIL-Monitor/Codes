# -*- coding: utf-8 -*-
import random, math
import os, sys, datetime, re, json, time
import xlwt
import requests
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download, traceback_decorator, email_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# logger 投资界
loghelper.init_logger("crawler_cyzone_incr", stream=True)
logger = loghelper.get_logger("crawler_cyzone_incr")

Rule = {'type': 'http', 'anonymity': 'high'}
Headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}


def get_proxy():
    while True:
        try:
            item = proxy_pool.get_single_proxy(Rule)
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            logger.info('%s:%s' % (ip, port))
            url = "http://www.cyzone.cn/event"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 10
            proxies = {
                'http': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('cyzone') >= 0:
                logger.info('ip:%s for cyzone' % ip_port)
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)


def save(item):
    mongo = db.connect_mongo()
    collection = mongo.raw.cyz_rz_incr
    lunci = item['lunci']
    product = item['product']
    money = item['money']
    date = item['date']
    item['createtime'] = datetime.datetime.now()
    item['modifytime'] = datetime.datetime.now()

    try:
        ex_item = collection.find_one({'product': product, 'lunci': lunci, 'money': money, 'date': date})
        if ex_item is None:
            collection.insert_one(item)
            logger.info('insert product:%s | lunci:%s done' % (product, lunci))
        else:
            logger.info('no change')
    except Exception, e:
        logger.info('mongo error:%s' % e)
    mongo.close()


def to_parser(page):
    d = pq(html.fromstring(page.decode('utf-8', 'ignore')))
    trs = d('div.list-table3> table> tr.table-plate3')
    for tr in trs:
        item = {'img_url': '',
                'product': '',
                'project_url': '',
                'id': '',
                'fullname': '',
                'money': '',
                'lunci': '',
                'investment': [],
                'tag': '',
                'date': '',
                'invest_url': ''}

        td1 = d(tr)('td.tp1>a >img')
        td2_tit = d(tr)('td.tp2> span> a')
        td2_com = d(tr)('td.tp2> span.tp2_com')
        td_money = d(tr)('td.tp-mean> div.money')
        td_lunci = d(tr)('td.tp-mean').next()
        td3 = d(tr)('td.tp3')
        td_tag = td3.next()('a')
        td_date = td3.next().next()
        td_rz = td_date.next()('a')

        if td1:
            item['img_url'] = td1.attr('src')
        if td2_tit:
            item['product'] = td2_tit.text().strip()
            # project 公司项目地址
            item['project_url'] = td2_tit.attr('href')
            if item['project_url']:
                item['id'] = item['project_url'].split('/')[-1].split('.')[0]
        if td2_com:
            item['fullname'] = td2_com.text().strip()
        if td_money:
            item['money'] = td_money.text().strip()
        if td_lunci:
            item['lunci'] = td_lunci.text().strip()
        if td3:
            lis = []
            investr = td3.attr('title')
            for i in investr.split(','):
                if i.strip() != '':
                    lis.append(i.strip())
            if investr.find('未披露') >= 0:
                lis = []
            item['investment'] = lis
        if td_tag:
            item['tag'] = td_tag.text().strip()
        if td_date:
            item['date'] = td_date.text().strip()
        if td_rz:
            item['invest_url'] = td_rz.attr('href')
        # print(json.dumps(item, ensure_ascii=False, indent=2, cls=util.CJsonEncoder))

        save(item)


def to_cralwer(num):
    logger.info('start to calw page:%d' % num)
    global Proxies
    i = 0
    while True:
        if i >= 3:
            Proxies = get_proxy()
            i = 0

        try:
            url = 'http://www.cyzone.cn/event/list-764-0-%d-0-0-0-0/' % num
            r = requests.get(url, headers=Headers, proxies=Proxies, timeout=20)

            if r.text.find('table-plate3') >= 0:
                return r.text

        except Exception, e:
            logger.info('requests error:%s' % e)
            i += 1
            time.sleep(5)


@traceback_decorator.try_except
def run():
    while True:
        global Proxies
        Proxies = get_proxy()

        for num in range(1, 4):
            page = to_cralwer(num)

            to_parser(page)

        time.sleep(60 * 60)
        logger.info('sleep 1 hour')


if __name__ == '__main__':
    run()
