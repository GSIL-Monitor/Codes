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
loghelper.init_logger("delete_dup_deal", stream=True)
logger = loghelper.get_logger("delete_dup_deal")


if __name__ == "__main__":
    conn =db.connect_torndb()
    items = conn.query("select companyId,organizationId,count(*) cnt from deal group by companyId,organizationId having cnt > 1")
    for item in items:
        deals = conn.query("select * from deal where companyId=%s and organizationId=%s", item["companyId"], item["organizationId"])
        i = 0
        for deal in deals:
            i += 1
            if i > 1:
                logger.info("delete: %s - %s", deal["id"], deal["status"])
                conn.execute("delete from deal_user_score where dealId=%s", deal["id"])
                conn.execute("delete from deal_user_rel where dealId=%s", deal["id"])
                conn.execute("delete from deal where id=%s", deal["id"])
    conn.close()