# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util
import time

DATE = None

# logger
loghelper.init_logger("crawler_feixiaohao_marketdata", stream=True)
logger = loghelper.get_logger("crawler_feixiaohao_marketdata")


def save_marketdata(content):
    fileName = 'file/market_data_%s.xls' % datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], fileName)

    logger.info('saving file:%s', path)
    with open(path, "wb") as file:
        file.write(content)

    return fileName


def run(crawler):
    url = "https://api.feixiaohao.com/coins/download/"

    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success' and len(result['content']) > 0:
            save_marketdata(result['content'])
            break


def start_run(flag):
    global DATE
    while True:
        dt = datetime.datetime.now()
        datestr = datetime.date.strftime(dt, '%Y-%m-%d %H')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE:
            logger.info("crawler_feixiaohao_marketdata %s start...", flag)
            crawler = BaseCrawler.BaseCrawler()

            run(crawler)

            logger.info("crawler_feixiaohao_marketdata %s end.", flag)
            DATE = datestr

        if flag == "incr":
            time.sleep(60)
        else:
            exit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run("incr")
        elif param == "all":
            start_run("all")
    else:
        start_run("incr")
        # print os.path.join(os.path.split(os.path.realpath(__file__))[0], '..')
        # fileName = 'file/market_data_%s.xls' % datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
        # print os.path.join(os.path.split(os.path.realpath(__file__))[0], fileName)
