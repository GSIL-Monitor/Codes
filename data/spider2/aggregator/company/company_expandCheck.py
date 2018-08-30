# -*- coding: utf-8 -*-
import os, sys, time
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import check_expand_diff
import company_info_expand_mongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper
import util
import download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian'))
import icp_chinaz
import beian_links

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/screenshot'))
import screenshot_website

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util

#logger
loghelper.init_logger("company_expand_check_diff", stream=True)
logger = loghelper.get_logger("company_expand_check_diff")

COMPANIES =[]

def expand():
    #init crawler
    beian_links_crawler = beian_links.BeianLinksCrawler()
    icp_chinaz_crawler = icp_chinaz.IcpchinazCrawler()
    screenshot_crawler = screenshot_website.phantomjsScreenshot()
    download_crawler_itjuzi = download.DownloadCrawler(max_crawl=200, timeout=10)
    download_crawler_kr36 = download.DownloadCrawler(use_proxy=False)
    download_crawler_lagou = download.DownloadCrawler(use_proxy=True)
    download_crawler = download.DownloadCrawler()
    while True:
        # gevent -> list of source_companies

        if len(COMPANIES) == 0:
            return
        sc = COMPANIES.pop(0)
        source = sc["source"]
        sourceId = sc["sourceId"]

        # company_info_expand_mongo.expand_source_company(source, sourceId, beian_links_crawler, icp_chinaz_crawler, screenshot_crawler)

        if source == 13030:
            diff_sourceCompanyId = check_expand_diff.check_diff(source, sourceId, download_crawler_itjuzi)
        elif source == 13020:
            diff_sourceCompanyId = check_expand_diff.check_diff(source, sourceId, download_crawler_kr36)
        elif source == 13050:
            diff_sourceCompanyId = check_expand_diff.check_diff(source, sourceId, download_crawler_lagou)
        else:
            diff_sourceCompanyId = check_expand_diff.check_diff(source, sourceId, download_crawler)
        logger.info("Source: %s, sourceId: %s, Diff: %s", source, sourceId, diff_sourceCompanyId)
        #Set processStatus in mysql and mongo
        mongo = db.connect_mongo()
        collection_source_company = mongo.source.company
        collection_source_company.update_one({"source": source, "sourceId": sourceId}, {'$set': {"processStatus": 1}})
        mongo.close()
        if diff_sourceCompanyId is not None:
            # #Set recommendIds
            # # insert audit_source_company
            # parser_mysql_util.insert_audit_source_company(diff_sourceCompanyId)
            # parser_mysql_util.update_db_processStatus(source, sourceId, 1)
            pass



def start_run(concurrent_num):
    while True:
        logger.info("Company expand start...")

        # 查询所有需要扩展的公司源
        mongo = db.connect_mongo()
        collection_source_company = mongo.source.company
        source_companies = list(collection_source_company.find({"processStatus": 0}, limit=1))
        mongo.close()
        for source_company in source_companies:
            sourceId = source_company["sourceId"]
            source = source_company["source"]
            if sourceId is None:
                continue
            sc = {
                "sourceId": sourceId,
                "source": source
            }
            COMPANIES.append(sc)

        threads = [gevent.spawn(expand) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        #break
        logger.info("Company expand end.")
        exit()
        if len(COMPANIES) == 0:
            gevent.sleep(1*60)

if __name__ == "__main__":
    start_run(1)