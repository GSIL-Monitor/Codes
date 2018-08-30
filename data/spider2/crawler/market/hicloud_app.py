# -*- coding: utf-8 -*-

import datetime
import requests
import re
import sys
import os
import random
from Queue import Queue
import threading
import time

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import util, db, traceback_decorator, loghelper, traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("hicloud_app cralwer", stream=True)
logger = loghelper.get_logger("hicloud_app cralwer")

Rule = {'type':'HTTPS', 'anonymous':'high'}
LinkPattern = '/app/C\d+'

Source = 'hicloud'
# Proxies = None


def get_proxy():
    Proxiesr = proxy_pool.get_single_proxy_x(Rule, 1000)
    # if len(Proxiesr) == 0:
    #     Proxiesr = proxy_pool.get_single_proxy_x(HTTP, 1000)
    while True:
        try:
            item = Proxiesr[random.randint(0, len(Proxiesr) - 1)]
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            logger.info('%s:%s' % (ip, port))
            url = "http://www.baidu.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 30
            proxies = {
                'https': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('hao123') >= 0:
                logger.info('ip:%s for %s' % (ip_port,Source))
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)

def deal_jspage_source():
    # deal home game soft topics and brands 翻页链接
    use_hrefs = []
    lis = [('/more/recommend/',3),('/more/all/',10),('/more/soft/',2),('/more/game/',2),
           ('/more/newPo/',10),('/more/newUp/',10),
           ('/topics/',88),('/brands/',4)]

    lis2 = [('/game/list_2_0_', 2), ('/game/list_2_1_', 10), ('/game/list_2_2_', 10),
            ('/soft/list_13_0_', 2), ('/soft/list_13_1_', 10), ('/soft/list_13_2_', 10)]

    for tup in lis:
        for i in range(1,tup[1]):
            href = tup[0] + str(i)
            use_hrefs.append(href)

    for tup2 in lis2:
        for j in range(1,tup2[1]):
            href = tup2[0] + str(j)
            use_hrefs.append(href)

    save_hrefs(use_hrefs)

def save_hrefs(use_hrefs):
    """
    check: N Y href:url  is_app:true false
    source:hicloud createtime:now() modifytime:now()
    """
    mongo = db.connect_mongo()
    collection = mongo.market.links
    if len(use_hrefs) == 0:
        return 0,0
    use_hrefs = list(set(use_hrefs))
    cnt = 0
    for href in use_hrefs:
        try:
            if collection.find_one({'source': Source, 'href': href}) is None:
                item = {'href':href,
                        'check':'N',
                        'is_app':False,
                        'source':Source,
                        'createtime':datetime.datetime.now(),
                        'modifytime':datetime.datetime.now()
                }
                if re.search(LinkPattern, href):
                    item['is_app'] = True
                    cnt += 1
                collection.insert_one(item)
                logger.info('save link:%s done'%href)
        except Exception,e:
            logger.info('mongo error:%s'%e)
    mongo.close()
    return len(use_hrefs), cnt

def links_parser(links):
    if len(links) == 0:
        return []

    hrefs = list(set(links))
    use_hrefs = []
    for href in hrefs:
        href = str(href)
        if href.find('javascript') >=0 or href.startswith('http') or href == '#':
            continue
        if href.find("//app.hicloud.com") >= 0 and href != '//app.hicloud.com':
            href = href.split('.com')[-1]
        if re.search('/(brand)|(topic)/\w{32}',href):
            # 添加 brand topic 子分类中的翻页url
            for i in range(1,11):
                bt_href = href + '/%d'%i
                use_hrefs.append(bt_href)
        use_hrefs.append(href)
    return use_hrefs

def change_check(href):
    mongo = db.connect_mongo()
    collection = mongo.market.links
    try:
        collection.update({'href': href, 'source': Source},{'$set':{'check':'Y','modifytime':datetime.datetime.now()}})
    except Exception, e:
        logger.info('mongo error:%s' % e)
    mongo.close()

def get_allinks(item, proxies):
    link = item['href']
    i = 0
    j = 0
    while True:
        if i >= 3:
            global Proxies
            Proxies = get_proxy()
            i = 0
        url = 'http://app.hicloud.com' + link
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }
        logger.info('start to cralw link:%s'%url)
        try:
            r = requests.get(url, headers=headers, proxies=proxies)
            res = r.text
            re1 = re.findall('href="(.*?)"', res)
            re2 = re.findall("href='(.*?)'", res)
            if re1 is None and re2 is None:return []
            links = re1
            if re2:links.extend(re2)
            change_check(link)
            return links
        except Exception,e:
            logger.info('requests error:%s'%e)
            i += 1
        j += 1
        logger.info('retry times:%d'%j)
        if j >= 20:
            raise ValueError('can not get all links:page error')

def take_link():

    mongo = db.connect_mongo()
    collection = mongo.market.links
    item = None
    try:
        item = collection.find_one({'check': 'N', 'source':Source})
        if item is None:
            collection.update({},{'$set':{'check':'N','modifytime':datetime.datetime.now()}},multi=True)
        item = collection.find_one({'check': 'N', 'source': Source})
    except Exception,e:
        logger.info('mongo error:%s'%e)
    mongo.close()
    return item

@traceback_decorator.try_except
def run():
    global Proxies
    Proxies = get_proxy()
    while True:

        deal_jspage_source()

        item = take_link()

        # if item is None:break

        all_links = get_allinks(item, Proxies)

        use_hrefs = links_parser(all_links)

        cnt1,cnt2 = save_hrefs(use_hrefs)

        logger.info('count: use_links:%d | app_links:%d'%(cnt1,cnt2))



if __name__ == '__main__':
    run()
