#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import datetime
import json
import pymongo


reload(sys)
sys.setdefaultencoding("utf-8")
import my_request
import util
import spider_util


source = 'pencil_news'
def fetch_news(url):
    news_key = url.split('=')[1]
    logger.info("news_key=%s" % news_key)

    (flag, r) = my_request.get(logger, url)
    logger.info("flag=%d", flag)

    if flag == -1:
        return -1

    if r.status_code == 404:
        logger.info("Page Not Found!!!")
        return r.status_code

    if r.status_code != 200:
        return r.status_code

    # print url
    # print r.url

    if r.url != url:
        logger.info("Page Redirect <--")
        return 302

    news_content = {"date":datetime.datetime.now(), "source":source, "url":url,
                       "news_key":news_key, "content":r.text}

    # save
    if news_collection.find_one({"source":source, "news_key":news_key}) is None:
        news_collection.insert_one(news_content)

    msg = {"type":"direct_news", "source":source, "news_key":news_key}
    logger.info(json.dumps(msg))
    kafka_producer.send_messages("pencil_news", json.dumps(msg))

    return 200

if __name__ == "__main__":
    (logger, mongo, kafka_producer, news_collection) \
        = spider_util.spider_direct_news_init('pencil_news')

    type = 'incr'
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            type = 'all'
        else:
            type = 'incr'


    cnt = 0
    latest_news = []
    if type == 'incr':
        latest_news = news_collection.find({"source":source}).sort("news_key", pymongo.DESCENDING).limit(1)
    if latest_news.count() == 0:
        i = 0
    else:
        i = int(latest_news[0]["news_key"])

    latest = i
    logger.info("From: %d" % i)

    while True:
        i += 1
        url = "http://www.pencilnews.cn/?p=%d" % (i)

        if cnt <= 0:
            proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
            my_request.get_single_session(proxy, new=True, agent=False)
            cnt = 100

        status = -1
        retry_times = 0
        while status != 200 and status !=404 and status !=302:
            try:
                status = fetch_news(url)
            except Exception,ex:
                logger.exception(ex)

            if status == -1:
                my_request.get_http_session(new=True, agent=False)
                cnt = 100

            retry_times += 1
            if retry_times >= 3:
                break

        cnt -= 1

        if status == 200:
            latest = i

        if latest < i - 500:
            break

