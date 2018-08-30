#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import datetime
import random
import json
import lxml.html
import pymongo


reload(sys)
sys.setdefaultencoding("utf-8")
import my_request
import util
import spider_util
import time
from pyquery import PyQuery as pq
import trends_tool
import proxy_pool

import gevent.monkey
gevent.monkey.patch_socket()

import gevent


def start():
    count = mysql.get('select count(*) cnt from artifact where type =4010')
    #count = count['cnt']
    count = 1
    for i in xrange(0, (count+99)/100):
        result = mysql.query('select domain from artifact where type = 4010 limit %s, 100', i*100)

        threads = []
        for artifact in result:
            domain = artifact["domain"]
            if domain is not None and domain.strip() !="":
                threads.append(gevent.spawn(fetch_alexa, domain.strip()))

        gevent.joinall(threads)



def fetch_alexa(domain):

    alexa = trends_tool.get_alexa(domain)

    url = 'http://www.alexa.cn/index.php?url='+domain
    proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
    while True:
        s = my_request.get_single_session(proxy, new=True, agent=False)
        (flag, r) = my_request.get(logger, url)
        if flag == 0:
            break

    d = pq(r.text)
    data = d('script').text()
    data = ''.join(data)
    (ids, ) = util.re_get_result("showHint\('(\S*)'\);", data)
    id_arr = ids.split(',')

    domain = id_arr[0]
    while True:
        timeout = 10
        try:
            r = s.post("http://www.alexa.cn/api_150710.php",
                       data={"url": id_arr[0],
                             "sig": id_arr[1],
                             "keyt":id_arr[2]
                             },
                       timeout=timeout)
            break
        except Exception,ex:
            logger.exception(ex)
            timeout = 20

    pv = r.text
    info = pv.split('*')

    page_view= []
    for i in xrange(0, len(info)):
        if i > 7 and i < 16:
            page_view.append(info[i])

    dt = datetime.date.today()
    today = datetime.datetime(dt.year,dt.month,dt.day)

    global_rank = alexa['global_rank']
    country_rank = alexa['country_rank']
    search_visits = alexa['search_visits']
    global_rank_value = None
    try:
        global_rank_value = int(global_rank.replace(",",""))
    except:
        pass
    country_rank_value = None
    try:
        country_rank_value = int(country_rank.replace(",",""))
    except:
        pass
    search_visits_value = None
    try:
        search_visits_value = float(search_visits.replace("%",""))/100
    except:
        pass

    result = {
              'date': today,
              'domain': domain,
              'global_rank':global_rank ,
              'country_rank': country_rank,
              'search_visits': search_visits,
              'global_rank_value':global_rank_value ,
              'country_rank_value': country_rank_value,
              'search_visits_value': search_visits_value,
              'page_view': page_view
              }

    logger.info(result)

    if alexa_collection.find_one({"domain": domain, "date":today }) is None:
        alexa_collection.insert_one(result)




# def get_ip(x):
#     return int(x.replace(',', ''))*3000
#
# def get_pv(x, y):
#     return int(x.replace(',', '')) * int(y.split('.')[0])*3000



if __name__ == "__main__":
    (logger, mongo, mysql, kafka_producer, alexa_collection) \
        = spider_util.spider_trends_init('alexa')

    start()


    # domain = 'teambition.com'
    #
    # fetch_alexa(domain)

    # while True:

