# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from bson import json_util
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import lxml.html
import time

import lagou_job_parser

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, download, name_helper,url_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("lagou_company_parser", stream=True)
logger = loghelper.get_logger("lagou_company_parser")

SOURCE = 13050 #Lgou
TYPE = 36001    #公司信息
aa =0
cnt = 0
download_crawler = download.DownloadCrawler(use_proxy=True)

def process():
    global aa,cnt
    logger.info("lagou_company_parser begin...")
    while True:

        items = parser_db_util.find_all_limit(SOURCE, TYPE, aa,1000)
        #items = [parser_db_util.find_process_one(SOURCE, TYPE, 128040)]
        aa += 1000
        for item in items:

            r = parse_company(item)

            if r["status"] == "Sub_company":
                #parser_db_util.update_active(SOURCE, item["key"], 'N')
                #parser_db_util.update_processed(item["_id"])
                logger.info("Fullname %s, %s", r["name"], item["url"])
                cnt += 1
                continue

            #exit()

        if len(items) == 0:
                break

    logger.info("total : %s", cnt)
        #break

    logger.info("lagou_company_parser end.")


def parse_company(item):
    if item is None:
        return None

    #logger.info("*** base ***")
    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    logo = d('.top_info_wrap > img').attr('src')
    if logo.startswith("http") or logo.startswith("https"):
        pass
    else:
        logo = "http:"+logo

    name = d('.company_main > h1 > a').text()
    fullName = d('.company_main > h1 > a').attr('title')
    fullName = name_helper.company_name_normalize(fullName)
    if name is None or fullName is None:
        return {
            "status": "No_Name",
        }
    if len(name) > len(fullName):
        name = fullName

    if fullName.find("分公司") >= 0:
        return {
            "status": "Sub_company",
            "name": fullName
        }

    return {
        "status": "good"
    }



if __name__ == "__main__":
    while True:
        process()
        time.sleep(60*30)