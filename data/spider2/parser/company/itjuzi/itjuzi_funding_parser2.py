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
loghelper.init_logger("itjuzi_funding_parser2", stream=True)
logger = loghelper.get_logger("itjuzi_funding_parser2")

SOURCE = 13032  #ITJUZI
TYPE = 36002    #融资事件
nokeys =[]

def process():
    logger.info("itjuzi_funding_parser2 begin...")

    items = parser_db_util.find_process(SOURCE, TYPE)
    # items = [parser_db_util.find_process_one(SOURCE, TYPE, 9551657)]

    for item in items:
        logger.info(item["url"])

        f = parse(item)
        if f is None:
            continue
        if f == -1:
            parser_db_util.update_processed(item["_id"])
            continue

        flag, source_funding_id= parser_db_util.save_funding(f,13030)
        if flag:
            # pass
            parser_db_util.update_processed(item["_id"])

        # break
    logger.info("itjuzi_funding_parser2 end.")
    logger.info(nokeys)


def parse(item):
    if item is None:
        return None

    funding_key = item["key"]
    logger.info("funding_key: %s", funding_key)
    data = item["content"]
    logger.info("*** funding ***")



    company_key = data["com_id"]
    logger.info("company_key: %s", company_key)

    source_company = parser_db_util.get_company(13030, company_key)

    if source_company is None:
        logger.info("this source company doesn't exist yet")
        if int(company_key) not in nokeys:
            nokeys.append(int(company_key))
        return None
    else:
        source_company_id = source_company["id"]
        logger.info("sourceComapnyId: %s", source_company_id)
        fundingDate = datetime.datetime.strptime(data["date"], '%Y-%m-%d')
        logger.info(fundingDate)

        roundStr = data["round"]
        fundingRound, roundStr = itjuzi_helper.getFundingRound(roundStr)
        logger.info("fundingRound=%d, roundStr=%s", fundingRound, roundStr)

        moneyStr = data["money"] + data["currency"]
        (currency, investment, precise) = itjuzi_helper.getMoney(moneyStr)
        logger.info("%s - %s - %s" % (currency, investment, precise))

        investors = []
        if data.has_key("invsest_with") and isinstance(data["invsest_with"],dict):
            for fi in data["invsest_with"]:
                f = data["invsest_with"][fi]
                investor_name = f["invst_name"]
                if investor_name == "" or investor_name == "未透露":
                    continue
                investor_url = None
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
            "sourceCompanyId": source_company_id,
            "fundingDate": fundingDate,
            "fundingRound": fundingRound,
            "roundStr": roundStr,
            "currency": currency,
            "investment": investment,
            "precise": precise,
            "investors": investors
        }

        #
        # except Exception, E:
        #     logger.info(E)
        #     return None


if __name__ == "__main__":
    process()