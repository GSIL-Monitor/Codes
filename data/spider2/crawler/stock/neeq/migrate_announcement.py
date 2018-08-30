# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import  json,time,datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,extract

#logger
loghelper.init_logger("crawler_neeq_an", stream=True)
logger = loghelper.get_logger("crawler_neeq_an")

SOURCE=13400



def start_run():
    while True:
        # logger.info("neeq announcement start...")
        # announcecrawler = AnnounceCrawler()
        # CURRENT_PAGE = 0
        # run(announcecrawler, startdate, maxpage, concurrent_num)
        #
        # logger.info("announcement end.",)
        #
        # gevent.sleep(60*5)   #3 days
        mongo = db.connect_mongo()
        # collection_neeq = mongo.stock.neeq_announcement
        collection_sse = mongo.stock.sse_announcement
        collection = mongo.stock.announcement

        ans = list(collection_sse.find({}))
        for an in ans:
            item = collection.find_one({"link": an["link"]})
            if item is None:
                logger.info("migrate: %s|%s", an["source"], an["title"])
                content = {
                    'stockExchangeId': 2,
                    'source': 13401,
                    'stockSymbol': str(an["sourceId"]),
                    'title': an["title"],
                    'link': an["link"],
                    "date": an["date"],
                    'createTime': an["createTime"],
                }
                collection.insert(content)
            else:
                logger.info("already existed")
            # break
        mongo.close()

if __name__ == "__main__":
    start_run()