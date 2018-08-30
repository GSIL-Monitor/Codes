# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from pyquery import PyQuery as pq
import chuangyepu_helper

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("Chuangyepu_company_parser", stream=True)
logger = loghelper.get_logger("Chuangyepu_company_parser")

SOURCE = 13040  #Chuangyepu
TYPE = 36003    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


def process():
    logger.info("Chuangyepu_investfirm_parser begin...")

    start = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)

        for item in items:

            r = parse_investor(item)
            if r is not None:
                parser_db_util.save_investor_standard(r, download_crawler)
            parser_db_util.update_processed(item["_id"])

        #break
        if len(items) == 0:
            break


    logger.info("Chuangyepu_investfirm_parser end.")


def parse_investor(item):

    logger.info("*** investfirm ***")

    investor_key = item["key"]
    html = item["content"]
    logger.info(investor_key)
    d = pq(html)

    logo = d('.logo-block > img').attr('src')

    if logo == "http://assets3.chuangyepu.com/chuangyepu/images/big-screenshot.png":
        logo = None
    basic_info = d('div.col-md-9> div> table> tr> td').eq(1)
    #logger.info(logo)
    name = pq(basic_info)('div.name').text().strip()
    if name is None:
        logger.info("No investor name!!!")
        return None
    desc = pq(basic_info)('div.desc').eq(0).text().strip()
    #logger.info(name+" "+desc)
    try:
        website = pq(basic_info)('div').eq(2)('a').text().strip()
    except:
        website = None

    if website is None or website.strip() == "暂无":
        website = None

    website = url_helper.url_normalize(website)
    flag, domain = url_helper.get_domain(website)
    if flag is None:
        website = None

    #logger.info(website)

    main_blocks = d('div.col-md-3> div.col-sm-12')
    #no js data
    #
    # for block in main_blocks:
    #     info = pq(block)
    #     h4 = info('h4.list_title').text().strip()
    #     logger.info(h4)
    #
    #     if h4 == "投资行业分布图":
    #         field = info('g.highcharts-axis-labels').text().strip()

    source_investor = {
        "name": name,
        "website": website,
        "description": desc,
        "logo_url": logo,
        "stage": None,
        "field": None,
        "type": 10020,
        "source": SOURCE,
        "sourceId": investor_key
    }
    logger.info(json.dumps(source_investor, ensure_ascii=False, cls=util.CJsonEncoder))


    return source_investor



if __name__ == "__main__":
    # while True:
    #     process()
    #     #break   #test
    #     time.sleep(30*60)
    process()