# -*- coding: utf-8 -*-
import os, sys
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, url_helper, name_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("itjuzi_investorfirm_parser", stream=True)
logger = loghelper.get_logger("itjuzi_investorfirm_parser")


SOURCE = 13030  #ITJUZI
TYPE = 36003    #投资公司

download_crawler = download.DownloadCrawler()

def process():
    logger.info("itjuzi_investorfirm_parser begin...")
    items = parser_db_util.find_process(SOURCE, TYPE)
    for item in items:
        logger.info(item["key"])
        logger.info(item["url"])
        r = parser(item)
        if r is None:
            continue
        parser_db_util.save_investfirm(r, SOURCE, download_crawler)
        parser_db_util.update_processed(item["_id"])
    logger.info("itjuzi_investorfirm_parser end.")


def parser(item):
    if item is None:
        return None

    investor_key = item["key"]

    html = item["content"]
    #logger.info(html)
    d = pq(html)
    investor_name = d('div.picinfo> p> span.title').text()
    investor_name = name_helper.company_name_normalize(investor_name)
    logger.info("investor_name: " + investor_name)

    if investor_name is None:
        logger.info("No investor name!!!")
        return None

    logo = d('div.pic> img').attr("src")
    if logo is not None:
        logo = logo.strip()
    logger.info("Investor Logo: %s" % logo)

    website = d('span.links >a[target="_black"]').attr("href")
    if website is None or website.strip() == "暂无":
        website = None

    website = url_helper.url_normalize(website)
    flag, domain = url_helper.get_domain(website)
    if flag is None:
        website = None

    logger.info("Investor website: %s" % website)

    stageStr = d('div.pad.block> div.list-tags.yellow').text().replace(" ",",").strip()
    logger.info("Investor rounds: %s" % stageStr)

    fieldsStr = d('div.pad.block> div.list-tags.darkblue').text().replace(" ",",").strip()
    logger.info("Investor fields: %s" % fieldsStr)

    desc = d('div.des').text().strip()
    logger.info("Investor desc: %s" % desc)

    return investor_key, investor_name, logo, website, stageStr, fieldsStr, desc



if __name__ == "__main__":
    process()