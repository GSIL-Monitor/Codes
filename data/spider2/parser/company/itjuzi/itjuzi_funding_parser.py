# -*- coding: utf-8 -*-
import os, sys
import datetime
from pyquery import PyQuery as pq

import itjuzi_helper

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("itjuzi_funding_parser", stream=True)
logger = loghelper.get_logger("itjuzi_funding_parser")

SOURCE = 13030  #ITJUZI
TYPE = 36002    #融资事件
nokeys =[]

def process():
    logger.info("itjuzi_funding_parser begin...")

    items = parser_db_util.find_process(SOURCE, TYPE)
    # items = [parser_db_util.find_process_one(SOURCE, TYPE, 34128)]

    for item in items:
        logger.info(item["url"])

        f = parse(item)
        if f is None:
            continue
        if f == -1:
            parser_db_util.update_processed(item["_id"])
            continue

        flag, source_funding_id= parser_db_util.save_funding(f,SOURCE)
        if flag:
            # pass
            parser_db_util.update_processed(item["_id"])

        # break
    logger.info("itjuzi_funding_parser end.")
    logger.info(nokeys)


def parse(item):
    if item is None:
        return None

    funding_key = item["key"]
    logger.info("funding_key: %s", funding_key)
    html = item["content"]
    #logger.info(html)
    d = pq(html)
    logger.info("*** funding ***")

    str = d("a.name").attr("href")
    if str is None:
        return -1

    company_key = str.strip().split("/")[-1]
    logger.info("company_key: %s", company_key)

    source_company = parser_db_util.get_company(SOURCE, company_key)

    if source_company is None:
        logger.info("this source company doesn't exist yet")
        if int(company_key) not in nokeys:
            nokeys.append(int(company_key))
        return None
    else:
        source_company_id = source_company["id"]
        logger.info("sourceComapnyId: %s", source_company_id)
        dateStr = d('div.title> h1> span').text().strip()
        result = util.re_get_result('(\d*?)\.(\d*?)\.(\d*?)$',dateStr)
        fundingDate = None
        if result != None:
            (year, month, day) = result
            y = int(year)
            if y >= 2100 and y <= 2109:
                year = 2010 + y%10
            m = int(month)
            if m > 12:
                m = 12
                month = "12"
            if (m==4 or m==6 or m==9 or m==11) and int(day)>30:
                day = "30"
            elif itjuzi_helper.isRunnian(int(year)) and m==2 and int(day)>29:
                day = 29
            elif itjuzi_helper.isRunnian(int(year)) == False and m==2 and int(day)>28:
                day = 28
            elif int(day) > 31:
                day = 31

            fundingDate = datetime.datetime.strptime("%s-%s-%s" % (year,month,day), '%Y-%m-%d')
        logger.info(fundingDate)

        roundStr = d('div.block-inc-fina> table> tbody> tr> td> span.round').text().strip()
        fundingRound, roundStr = itjuzi_helper.getFundingRound(roundStr)
        logger.info("fundingRound=%d, roundStr=%s", fundingRound, roundStr)

        moneyStr = d('div.block-inc-fina> table> tbody> tr> td> span.fina').text().strip()
        (currency, investment, precise) = itjuzi_helper.getMoney(moneyStr)
        logger.info("%s - %s - %s" % (currency, investment, precise))

        investors = []
        # fs = d('div.right> h4 >a.title')
        # for f in fs:
        #     l = pq(f)
        #     investor_name = l.text().strip()
        #     if investor_name == "":
        #         continue
        #     investor_url = l.attr("href")
        #     if investor_url is not None and investor_url != "":
        #         investor_key = investor_url.strip().split("/")[-1]
        #         investor = {
        #             "name":investor_name,
        #             "key":investor_key,
        #             "url":investor_url,
        #             "type":38001
        #         }
        #         investors.append(investor)
        #         logger.info("Investor: %s, %s, %s", investor_key, investor_name, investor_url)
        #     else:
        #         investor_key = None
        #         temps = investor_name.split(";")
        #         for name in temps:
        #             name = name.strip()
        #             if name == "":
        #                 continue
        #             investor = {
        #                 "name":name,
        #                 "key":None,
        #                 "url":None,
        #                 "type":38001
        #             }
        #             investors.append(investor)
        #             logger.info("Investor: %s, %s, %s", investor_key, name, investor_url)
        fs = pq(d('div.pad.finan-history> table >tr> td').eq(2))('span> a')
        for f in fs:
            l = pq(f)
            investor_name = l.text().strip()
            if investor_name == "":
                continue
            investor_url = l.attr("href")
            if investor_url is not None and investor_url != "":
                investor_key = investor_url.strip().split("/")[-1]
                investor = {
                    "name": investor_name,
                    "key": investor_key,
                    "url": investor_url,
                    "type": 38001
                }
                investors.append(investor)
                logger.info("Investor: %s, %s, %s", investor_key, investor_name, investor_url)
            else:
                investor_key = None
                temps = investor_name.split(";")
                for name in temps:
                    name = name.strip()
                    if name == "":
                        continue
                    investor = {
                        "name": name,
                        "key": None,
                        "url": None,
                        "type": 38001
                    }
                    investors.append(investor)
                    logger.info("Investor: %s, %s, %s", investor_key, name, investor_url)
    return {
        "sourceCompanyId":source_company_id,
        "fundingDate":fundingDate,
        "fundingRound":fundingRound,
        "roundStr":roundStr,
        "currency":currency,
        "investment":investment,
        "precise":precise,
        "investors":investors
    }



if __name__ == "__main__":
    process()