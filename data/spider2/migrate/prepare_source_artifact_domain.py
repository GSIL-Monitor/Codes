# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config, util, db, url_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../crawler/website'))
import website

#logger
loghelper.init_logger("prepare_source_artifact_domain", stream=True)
logger = loghelper.get_logger("prepare_source_artifact_domain")




if __name__ == "__main__":
    start = 0
    conn =db.connect_torndb()
    while True:
        items = list(conn.query("select * from source_artifact order by id limit %s,1000",start))
        for item in items:
            if item["domain"] is not None and item["domain"].strip() != "":
                continue

            if item["type"] == 4010:
                link = url_helper.url_normalize(item["link"])
                (flag, domain) = url_helper.get_domain(link)
                if flag is True:
                    logger.info("%s, %s %s %s", item["id"], item["type"], link, domain)
                    conn.update("update source_artifact set domain=%s where id=%s", domain, item["id"])

            elif item["type"] == 4040 or item["type"] == 4050:
                (apptype, appmarket, trackid) = url_helper.get_market(item["link"])
                if (apptype == 4040 or apptype == 4050) and trackid is not None:
                    logger.info("%s %s %s %s", item["id"], apptype, item["link"], trackid)
                    conn.update("update source_artifact set type=%s, domain=%s where id=%s",apptype,trackid,item["id"])
        start += 1000
        if len(items) == 0:
            break
    conn.close()
