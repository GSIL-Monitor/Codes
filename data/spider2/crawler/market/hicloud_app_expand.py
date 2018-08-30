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
from hicloud_app import get_proxy

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import util, db, traceback_decorator, loghelper, traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("hicloud_app_expand cralwer", stream=True)
logger = loghelper.get_logger("hicloud_app_expand cralwer")

Rule = {'type':'HTTPS', 'anonymous':'high'}
LinkPattern = '/app/C\d+'

Source = 'hicloud'

def see_clear_num():
    # 查看app数字分布规律
    mongo = db.connect_mongo()
    collection = mongo.market.links
    items = []
    try:
        items = list(collection.find({'is_app':True}))
    except Exception, e:
        logger.info('mongo error:%s' % e)
    mongo.close()

    if items is None:return

    lis = []
    for item in items:
        href = item['href']
        h_num = int(href.split('/C')[-1])
        lis.append(h_num)
    lis.sort()
    return lis

def get_url_queue(lis):

    # 找出差别值
    index = 0
    for i in lis:
        j = lis[lis.index(i) - 1]
        if i // j >= 20 and j <= 1000000:
            index = j
            break

    url_list = list('http://app.hicloud.com/app/C%d' % i for i in range(0, index))
    logger.info('0--->%d'%index)
    # 10 000000 -> 10 999999

    url_list2 = list('http://app.hicloud.com/app/C10%s' % str(i).zfill(6) for i in range(0, 999999))
    url_list.extend(url_list2)
    # 100 000000 -> 100 999999

    url_list3 = list('http://app.hicloud.com/app/C100%s' % str(i).zfill(6) for i in range(0, 999999))
    url_list.extend(url_list3)

    for url in url_list:
        url_queue.put(url)

def get_use_hrefs():
    global Proxies
    while True:
        url = url_queue.get()
        logger.info('start to cralw url:%s'%url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }
        time.sleep(1)
        try:
            r = requests.get(url,headers=headers,proxies=Proxies)
            if r.text.find('hicloud') >= 0:
                href_queue.put(url.split('.com')[-1])
                logger.info('got url:%s'%url)
        except Exception,e:
            logger.info('requests error:%s'%e)
            Proxies = get_proxy()
        url_queue.task_done()

def save_href_queue():
    mongo = db.connect_mongo()
    collection = mongo.market.links
    while True:
        href = href_queue.get()
        try:
            if collection.find_one({'source': Source, 'href': href}) is None:
                item = {'href': href,
                        'check': 'N',
                        'is_app': False,
                        'source': Source,
                        'createtime': datetime.datetime.now(),
                        'modifytime': datetime.datetime.now()
                        }
                if re.search(LinkPattern, href):
                    item['is_app'] = True
                collection.insert_one(item)
                logger.info('save link:%s done' % href)

        except Exception, e:
            logger.info('mongo error:%s' % e)
        href_queue.task_done()
    mongo.close()


url_queue = Queue()
href_queue = Queue()
Proxies = get_proxy()
@traceback_decorator.try_except
def run():

    while True:

        t_list = []

        lis = see_clear_num()

        t_url = threading.Thread(target=get_url_queue,args=(lis,))
        t_list.append(t_url)

        for i in range(5):
            t_href = threading.Thread(target=get_use_hrefs)
            t_list.append(t_href)

        for i in range(2):
            t_save = threading.Thread(target=save_href_queue)
            t_list.append(t_save)

        for t in t_list:
            # t.setDaemon(True)  # 设置守护线程，说明该线程不重要，主线程结束，子线程结束
            t.start()

        for q in [url_queue, href_queue]:
            q.join() #等待，让主线程等待，队列计数为0之后才会结束，否则会一直等待

        logger.info('sleep 24 hours')
        time.sleep(60*60*24)

if __name__ == '__main__':
    run()
