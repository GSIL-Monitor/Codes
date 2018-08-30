# -*- coding: utf-8 -*-
import os, sys, datetime
import re

from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey
import requests

monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util
import time

# logger
loghelper.init_logger("crawler_jinsecaijing_newfs", stream=True)
logger = loghelper.get_logger("crawler_jinsecaijing_newfs")

# mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

SOURCE = 13860
TYPE = 60008

class jinsecaijingCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('news') >= 0:
                return True
        return False


def get_proxy(http_type):
    proxy = {'type': http_type, 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        print("Start proxy_pool.get_single_proxy")
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            print("proxy_pool.get_single_proxy return None")
        print(proxy_ip['ip:port'])
        return {proxy_ip['ip']:proxy_ip['port']}


def get_headers():
    while True:
        try:
            proxy = get_proxy('https')
            session = requests.session()
            r = session.get('https://www.jinse.com/',proxies=proxy)
            cookies = []
            cookie = r.cookies.get_dict()
            if cookie is not None:
                for i in cookie:
                    cookies.append(i + '=' + cookie[i])
                cookiestr = ';'.join(cookies)
                logger.info('cookie:%s',cookiestr)
                headers = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                    'referer': 'https://www.jinse.com/lives',
                    'origin': 'https://www.jinse.com',
                    'cookie': cookiestr}
                return headers
        except Exception as e:
            logger.info('wrong:',e)


def has_content(content):
    if content is not None:
        if content.has_key('list'):
            logger.info('success to get newsf list')
            return True
    else:
        logger.info("Fail to get content")
    return False


def process_news(item):
    if 1:
        con = item['content']
        title = con.split('【')[-1].split('】')[0]
        key = str(item['id'])
        news_time = datetime.datetime.fromtimestamp(float(item['created_at']))
        url = 'https://www.jinse.com/lives/' + key + '.htm'

        flag, domain = url_helper.get_domain(url)


        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": TYPE,
            "original_tags": [],
            "processStatus": 0,
            # "companyId":companyId,
            "companyIds": [],
            "category": None,
            "domain": domain,
            "categoryNames": []
        }

        dcontents = []
        description = con
        if description is not None:
            dc = {
                "rank": 1,
                "content": "金色财经快讯",
                "image": "",
                "image_src": "",
            }

            dcontents.append(dc)
            dc = {
                "rank": 2,
                "content": description,
                "image": "",
                "image_src": "",
            }
            dcontents.append(dc)

            if item['link'] is not None and item['link'].strip() != '':
                linkcon = item['link_name'] + ':' + item['link']
                dc = {
                    "rank": 3,
                    "content": linkcon,
                    "image": "",
                    "image_src": "",
                }
                dcontents.append(dc)

            # logger.info(description)

        dnews["contents"] = dcontents


        brief = util.get_brief_from_news(dcontents)

        post = util.get_posterId_from_news(dcontents)

        dnews["postId"] = post
        # dnews["post"] = post
        dnews["brief"] = brief
        logger.info(json.dumps(dnews,ensure_ascii=False,cls=util.CJsonEncoder,indent=2))
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)


def process_page(content, flag):
    if len(content['list']) == 1:
        infos = content['list'][0]['lives']
        for info in infos:
            con = info['content']
            title = con.split('【')[-1].split('】')[0]
            key = info['id']
            date = datetime.datetime.fromtimestamp(float(info['created_at']))
            logger.info("%s, %s, %s", key, date, title)

            if collection_news.find_one({"source": SOURCE, "key_int": int(key), "type": TYPE}) is None or flag == "all":
                craw = True
                newses = list(collection_news.find({"title": title}))
                for news in newses:
                    if news.has_key("type") and news["type"] > 0:
                        craw = False
                        break
                if craw:
                    logger.info("%s, %s, %s", key, date, title)
                    process_news(info)


def start_run(flag):
    while True:
        logger.info("jinsecaijing flashes %s start...", flag)
        crawler = jinsecaijingCrawler()
        headers = get_headers()
        while True:
            page_url = "https://api.jinse.com/v4/live/list?limit=20"
            result = crawler.crawl(page_url, agent=True,headers=headers)
            if result['get'] == 'success':
                content = json.loads(result['content'])
                # print(json.dumps(content, ensure_ascii=False,indent=4))
                if has_content(content):
                    process_page(content, flag)
                break
        logger.info("jinsecaijing news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60 * 5)  # 10 minutes
        else:
            gevent.sleep(86400 * 3)  # 3 days


if __name__ == '__main__':
    flag = 'incr'
    start_run('incr')
