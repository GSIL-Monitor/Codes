# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time
import json
import traceback
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util

#logger
loghelper.init_logger("360_parser", stream=True)
logger = loghelper.get_logger("360_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

market_collection = mongo.crawler_v2.market_360
other_collection = mongo.crawler_v2.market_other

if __name__ == "__main__":
    logger.info("Start...")
    apps = market_collection.find({"parsed":{"$ne":True}})
    #apps = market_collection.find({})
    for app in apps:
        if app.get("html_parsed") is not None:
            if app.get("parsed") is None:
                market_collection.update_one({"_id":app["_id"]},{'$set':{'parsed':True}})
                #break
            continue

        try:
            content = app.get("content")
            if content is None:
                continue
            logger.info(app["url"])
            r = "var detail = \(function \(\) \{\s*?return\s*?(.*?);\s*?\}\)"
            result = util.re_get_result(r,content)
            (b,) = result
            base = json.loads(b.replace("'",'"'),strict=False)
            name = base["sname"]
            type = base["type"]
            package = base["pname"].strip()
            logger.info("%s, %s, %s" % (type, name, package))

            soup = BeautifulSoup(content, 'html.parser')
            prettified_content = soup.prettify()

            d = pq(prettified_content)
            desc = ""
            try:
                # desc = d('div.breif').contents()[0].strip()
                desc = d('div.breif').text().strip()
                ts = desc.split("【基本信息】")
                desc = ts[0].strip()
            except:
                pass
            if desc == "":
                try:
                    desc = d('div#html-brief').text().strip()
                except:
                    pass

            #logger.info(desc)

            author = d('div.base-info> table> tbody> tr> td').eq(0).contents()[2].strip()
            #logger.info(author)
            modify_date_str = d('div.base-info> table> tbody> tr> td').eq(1).contents()[2].strip()
            #logger.info(modify_date_str)
            modify_date =  datetime.datetime.strptime(modify_date_str,"%Y-%m-%d")
            #logger.info(modify_date)
            versionname = None
            try:
                versionname = d('div.base-info> table> tbody> tr> td').eq(2).contents()[2].strip()
            except:
                pass
            #logger.info(version)

            icon = d('div#app-info-panel> div> dl> dt >img').attr("src").strip()
            #logger.info(icon)

            screenshots = []
            try:
                screenshots = d('div#scrollbar').attr("data-snaps").split(",")
            except:
                pass

            html_parsed = {
                "type": type,
                "name": name,
                "package": package,
                "versionname": versionname,
                "icon": icon,
                "author": author,
                "screenshots": screenshots,
                "desc":desc,
                "modifydate":modify_date
            }
            #logger.info(html_parsed)

            market_collection.update_one({"_id":app["_id"]},{'$set':{'html_parsed':html_parsed, 'parsed':True}})

            if other_collection.find_one({"package":package}) is None:
                other_collection.insert_one({"package":package})

            #break
        except Exception,e :
            logger.error(e)
            traceback.print_exc()

