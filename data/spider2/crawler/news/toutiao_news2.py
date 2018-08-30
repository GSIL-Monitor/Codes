# -*- coding: utf-8 -*-
import sys, os
import requests
import time, datetime
import traceback
from lxml import html
from pyquery import PyQuery as pq

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db, extract, loghelper, url_helper, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util


#logger
loghelper.init_logger("toutiao_news", stream=True)
logger = loghelper.get_logger("toutiao_news")


SOURCE = 13837


def get_proxy():
    try:
        mongo = db.connect_mongo()
        proxy = mongo.raw.proxy_tyc.find_one({}, sort=[("fail", 1)])
        return proxy
    finally:
        mongo.close()
    return None


def request(proxy, url, headers=None):
    logger.info("request: %s" % url)
    if headers is None:
        headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.4.8 (KHTML, like Gecko)"
    headers["Accept-Language"] = "zh-CN,zh;q=0.5,en;q=0.3"
    headers["Accept-Encoding"] = ""

    stype = "socks5"
    if proxy["type"].lower() == "socks4":
        stype = "socks4"
    proxy = "%s://%s:%s" % (stype, proxy["ip"], proxy["port"])
    # logger.info(proxy)
    proxies = {
        'http': proxy,
        'https': proxy
    }

    response = None
    retries = 0
    while True:
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
        except Exception as e:
            if retries < 3:
                retries += 1
                time.sleep(3)
                continue
            else:
                traceback.print_exc()
                logger.info("fetch error!")
        break

    if response is not None:
        if response.status_code != 200:
            logger.info("Error: %s, %s" % (response.status_code, url))
            logger.info("proxy: %s" % (proxy))
        else:
            return response

    return None


def run(url):
    proxy = get_proxy()
    if proxy is None:
        logger.info("Error: no proxy!")
        return
    logger.info(proxy)

    response = request(proxy, url)
    if response is None:
        return
    text = response.text
    # logger.info(html)
    key = url.split("/")[-1].strip()
    download_crawler = None
    d = pq(html.fromstring(text.decode("utf-8")))
    title = d('h1.article-title').text().strip()
    str_time = d('span.time').text().strip()
    str_content = d('div.article-content').html()
    brief = d("meta[name='description']").attr("content")
    logger.info(title)
    logger.info(str_time)
    # logger.info(str_content)
    contents = extract.extractContents(url, str_content)
    # logger.info(contents)

    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    if collection_news.find_one({"title": title}) is not None:
        mongo.close()
        return

    flag, domain = url_helper.get_domain(url)
    news_time = datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M")
    dnews = {
        "date": news_time - datetime.timedelta(hours=8),
        "title": title,
        "link": url,
        "createTime": datetime.datetime.now(),
        "source": SOURCE,
        "key": key,
        "key_int": None,
        "type": 60001,
        "original_tags": [],
        "processStatus": 0,
        # "companyId": None,
        "companyIds": [],
        "domain": domain,
        "category": None,
        "categoryNames": []
    }
    dcontents = []
    rank = 1
    for c in contents:

        if c["type"] == "text":
            dc = {
                "rank": rank,
                "content": c["data"],
                "image": "",
                "image_src": "",
            }
        else:
            if download_crawler is None:
                dc = {
                    "rank": rank,
                    "content": "",
                    "image": "",
                    "image_src": c["data"],
                }
            else:
                imgurl = parser_mysql_util.get_logo_id(c["data"], download_crawler, SOURCE, key, "news")
                if imgurl is not None:
                    dc = {
                        "rank": rank,
                        "content": "",
                        "image": str(imgurl),
                        "image_src": "",
                    }
                else:
                    continue

        logger.info(c["data"])
        dcontents.append(dc)
        rank += 1
    dnews["contents"] = dcontents
    if brief is None or brief.strip() == "":
        brief = util.get_brief_from_news(dcontents)

    post = util.get_posterId_from_news(dcontents)

    if download_crawler is None:
        dnews["post"] = post
    else:
        dnews["postId"] = post
    dnews["brief"] = brief

    if news_time > datetime.datetime.now():
        logger.info("Time: %s is not correct with current time", news_time)
        dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

    id = collection_news.insert(dnews)
    mongo.close()
    logger.info("*************DONE************* %s", id)



if __name__ == "__main__":
    # http://www.toutiao.com/a6394949522091409665/
    if len(sys.argv) <= 1:
        logger.info("usage: python toutiao_news2.py <url>")
        exit()
    url = sys.argv[1]
    run(url)