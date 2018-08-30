# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util2'))
import parser_mongo_util

# logger
loghelper.init_logger("amac_fund_parser", stream=True)
logger = loghelper.get_logger("amac_fund_parser")

SOURCE = 13631  # amac fund
TYPE = 36001  # 公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


def find_amac_manager(managerId):
    mongo = db.connect_mongo()
    collection = mongo.amac.manager
    result = collection.find_one({"sourceId": managerId})
    mongo.close()
    return result


def process():
    logger.info("amac fund parser begin...")

    start = 0
    while True:
        items = parser_mongo_util.find_process_limit(SOURCE, TYPE, start, 1000)
        # items = [parser_mongo_util.find_process_one(SOURCE,TYPE,1705190831105336)]
        for item in items:
            # logger.info(item)
            r = parse_company(item)
            if r["status"] == "Fail":
                exit()
            else:
                manager = find_amac_manager(r['managerId'])
                if manager is None:
                    logger.info("lack manager:  %s", item["url"])
                    continue
                else:
                    r['managerId'] = str(manager['_id'])
                    parser_mongo_util.save_mongo_amac_fund(r["source"], r["sourceId"], r)
                    parser_mongo_util.update_processed(item["_id"])
                    logger.info("processed %s", item["url"])

        # break
        if len(items) < 1000:
            break

    logger.info("amac fund parser end.")


def parse_company(item):
    logger.info("parse_company")
    company_key = item["key"]

    record = {}
    d = pq(html.fromstring(item["content"].decode("utf-8")))

    fundName = d(':contains("基金名称:")+ .td-content').text()
    establishDate = d(':contains("成立时间:")+ .td-content').text()
    fundCode = d(':contains("基金编号:")+ .td-content').text()
    regDate = d(':contains("备案时间:")+ .td-content').text()
    fundType = d(':contains("基金类型:")+ .td-content').text()
    currency = d(':contains("币种:")+ .td-content').text()
    managerName = d(':contains("基金管理人名称:")+ .td-content').text()
    managerId = d(':contains("基金管理人名称:")+ .td-content a').attr('href').split('/manager/')[-1].replace('.html', '')
    manageType = d(':contains("管理类型:")+ .td-content').text()
    trustee = d(':contains("托管人名称:")+ .td-content').text()
    field = d(':contains("主要投资领域:")+ .td-content').text()
    status = d(':contains("运作状态:")+ .td-content').text()
    lastUdpateDate = d(':contains("基金信息最后更新时间:")+ .td-content').text()

    if fundName is None or fundName == "":
        return {"status": "Fail"}
    else:
        record = {
            "status": "Success",
            "fundCode":fundCode,
            "fundName": fundName.replace("(", "（").replace(")", "）"),
            "regDate": regDate if regDate != "" else None,
            "establishDate": establishDate if establishDate != "" else None,
            "lastUpdateDate": lastUdpateDate if lastUdpateDate != "" else None,
            "fundType": fundType if fundType != "" else None,
            "currency": currency if currency != "" else None,
            "trustee": trustee if trustee != "" else None,
            "field": field if field != "" else None,
            "Fundstatus": status if status != "" else None,
            "managerName": managerName if managerName != "" else None,
            "managerId": managerId if managerId != "" else None,
            "manageType": manageType if manageType != "" else None,
            "source": SOURCE,
            "sourceId": company_key,
            "sourceUrl": item["url"]
        }
        return record


if __name__ == "__main__":
    while True:
        process()
        # break   #test
        time.sleep(30 * 60)
