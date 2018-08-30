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
loghelper.init_logger("crawler_pedaily_incr", stream=True)
logger = loghelper.get_logger("crawler_pedaily_incr")

Rule = {'type': 'http', 'anonymity': 'high'}
Headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}


def get_proxy():
    while True:
        try:
            item = proxy_pool.get_single_proxy(Rule)
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            logger.info('%s:%s' % (ip, port))
            url = "http://www.pedaily.cn/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 10
            proxies = {
                'http': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('pedaily') >= 0:
                logger.info('ip:%s for pedaily' % ip_port)
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)


def save(item):
    mongo = db.connect_mongo()
    collection = mongo.raw.tzj_rz_incr
    lunci = item['lunci']
    product = item['product']
    money = item['money']
    date = item['date']
    item['createtime'] = datetime.datetime.now()
    item['modifytime'] = datetime.datetime.now()

    try:
        ex_item = collection.find_one({'product': product, 'lunci': lunci, 'money':money, 'date':date})
        if ex_item is  None:
            collection.insert_one(item)
            logger.info('insert product:%s | lunci:%s done' % (product, lunci))
        else:
            logger.info('no change')
    except Exception, e:
        logger.info('mongo error:%s' % e)
    mongo.close()


def to_parser(page):
    d = pq(html.fromstring(page.decode('utf-8', 'ignore')))
    trs = d('tbody> tr')
    for tr in trs:
        if d(tr).html().find('受资方') >= 0:
            continue
        item = {
            'id': '',
            'tag': '',
            'date': '',
            'lunci': '',
            'money': '',
            'img_url': '',
            'product': '',
            'investment': '',
            'investr':'',
            'createtime': '',
            'modifytime': '',
            'invest_url': '',
            'project_url': '',
        }
        td1 = d(tr)('td.td1> a> img')
        td2_tit = d(tr)('td.td2> span> a')
        td2_com = d(tr)('td.td2> span> span')
        td3 = d(tr)('td.td3')
        td4 = d(tr)('td.td4> span')
        td5 = d(tr)('td.td5')
        td6 = d(tr)('td.td6')
        td7 = d(tr)('td.tools> a')
        if td1:
            item['img_url'] = td1.attr('src')
        if td2_tit:
            item['product'] = td2_tit.text().strip()
            # project 公司项目地址
            item['project_url'] = td2_tit.attr('href')
            item['id'] = item['project_url'].split('project/')[-1]
        if td2_com:
            item['tag'] = td2_com.text().split('：')[-1].strip()
        if td3:
            item['date'] = td3.text().strip()
        if td4:
            item['lunci'] = td4.text().strip()
        if td5:
            item['money'] = ''.join(td5.text().split(' '))
        if td6.html().find('不详') >= 0:
            item['investment'] = []
        else:
            lis = []
            aa = d(td6)('a')
            ss = d(td6)('span')
            if aa:
                for a in aa:
                    inves = d(a).text().strip()
                    inves_link = d(a).attr('href')
                    lis.append([inves, inves_link])
            if ss:
                for s in ss:
                    inves = d(s).text().strip()
                    inves_link = ''
                    lis.append([inves, inves_link])
            item['investment'] = lis
            investr = ''
            for l in lis:
                investr += ' ' + l[0] + ' '
            item['investr'] = investr
        if td7:
            # invest 融资事件详情地址
            item['invest_url'] = td7.attr('href')
        # print(json.dumps(item, ensure_ascii=False, indent=2, cls=util.CJsonEncoder))
        save(item)


def to_cralwer(num):
    logger.info('start to crawl page:%d'%num)
    global Proxies
    i = 0
    while True:
        if i >= 3:
            Proxies = get_proxy()
            i = 0

        try:
            url = 'http://newseed.pedaily.cn/data/invest/p%d'%num
            r = requests.get(url, headers=Headers, proxies=Proxies, timeout=20)
            if r.text.find('table-list') >= 0:
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

        for num in range(1,4):

            page = to_cralwer(num)

            to_parser(page)

        time.sleep(60 * 60)

        logger.info('sleep 1 hour')


if __name__ == '__main__':
    run()
