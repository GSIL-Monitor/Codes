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
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


def process():
    logger.info("Chuangyepu_company_parser begin...")

    start = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)
        #items = [parser_db_util.find_process_one(SOURCE, TYPE, 1)]

        for item in items:
            #if item['key_int'] != 1:
            #    continue
            r = parse_company(item)
            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

            if r["status"] == "No_Data" or r["status"] == "No_Name" :
                 parser_db_util.update_active(SOURCE, item["key"], 'N')
                 parser_db_util.update_processed(item["_id"])
                 logger.info("No infos for %s" ,item["url"])
                 exit()
                 continue

            source_company_id = parser_db_util.save_company_standard(r, download_crawler)
            parser_db_util.delete_source_company_name(source_company_id)
            parser_db_util.delete_source_mainbeianhao(source_company_id)
            parser_db_util.save_source_company_name(source_company_id, r["name"],12020)

            logger.info("source_company_id=%s", source_company_id)

            artifacts = []
            artifacts.extend(r["artifacts"])
            logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))
            parser_db_util.save_artifacts_standard(source_company_id, artifacts)

            parser_db_util.delete_funding(source_company_id)
            flag = parseFinance_save(source_company_id,r['fundings'], download_crawler)
            if flag:
                 parser_db_util.update_processed(item["_id"])
                 logger.info("processed %s" ,item["url"])
            else:
                logger.info("lack something:  %s", item["url"])
                exit()

        break


    logger.info("Chuangyepu_company_parser end.")


def parse_company(item):

    logger.info("*** base ***")
    company_key = item["key"]
    html = item["content"]
    logger.info(company_key)
    d = pq(html)

    logo = d('.logo-block > img').attr('src')
    if logo == 'http://assets3.chuangyepu.com/chuangyepu/images/big-screenshot.png':
        logo = None

    basic_info = d('div.col-md-9> div> table> tr> td').eq(1)
    #logger.info(basic_info)
    name = pq(basic_info)('div.name').text().strip()
    brief = pq(basic_info)('div.desc').eq(0).text().strip()
    if name is None:
        return {
            "status": "No_Name",
        }
    #logger.info(name+" "+brief)
    try:
        website = pq(basic_info)('div.desc').eq(1)('a').text().strip()
    except:
        website = None

    #logger.info("website: %s",website)

    #parser artifact

    tags = pq(basic_info)('div.line-block').text().strip().replace(" ",",")
    #logger.info(tags)

    main_blocks = d('div.col-md-9> div.col-sm-12')
    h4s = d('div.col-md-9> h4')
    logger.info("main: %d, h4: %d",len(main_blocks),len(h4s))

    #产品介绍/团队成员/媒体报道/融资历史
    if len(h4s) != len(main_blocks) - 1:
        return {
            "status": "No_Data",
        }

    desc = None
    round = None
    roundDesc = None
    source_fundings = []

    for i in xrange(len(h4s)):
        h4 = h4s.eq(i).text().strip()
        d = main_blocks.eq(i + 1)
        #DESC
        if h4 == "产品介绍":
            desc = d('div.content> div> p.desc').text().strip()
        #parser finance
        if h4 == "融资历史":
            lines = d('table> tr')
            for li in lines:
                line = pq(li)
                if line.text().find("时间") >= 0:
                    continue
                #logger.info(line)

                date =  line('td.investment_date> span').text().strip()+"/01"
                try:
                    fundingDate = datetime.datetime.strptime(date,'%Y/%m/%d')
                except:
                    fundingDate = None
                #logger.info(fundingDate)

                roundStr = line('td.investment-round').text().strip()
                fundingRound, roundStr = chuangyepu_helper.getFundingRound(roundStr)
                #logger.info("fundingRound=%d, roundStr=%s", fundingRound, roundStr)

                moneyStr = line('td.money').text().strip()
                (currency, investment, precise) = chuangyepu_helper.getMoney(moneyStr)
                #logger.info("%s - %s - %s" % (currency, investment, precise))

                fs = line('td').eq(3)('p> a')
                investors = []
                for f in fs:
                    iv = pq(f)
                    investor_url = iv.attr("href")
                    investor_name = iv.text().strip()
                    if investor_name is not None and investor_url is not None and investor_url != "" and investor_url.find("institutions") >=0:
                        investor_key = investor_url.strip().split("/")[-1]

                        investor = {
                            "name": investor_name,
                            "key": investor_key
                        }
                        investors.append(investor)
                source_funding = {
                    "investment": investment,
                    "precise": precise,
                    "round": fundingRound,
                    "roundDesc": roundStr,
                    "currency": currency,
                    "fundingDate": fundingDate,
                    "investors": investors

                }
                #logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))

                source_fundings.append(source_funding)
                if round is None or round < fundingRound:
                    round = fundingRound
                    roundDesc = roundStr

        if h4 == "团队成员":
            #not accurate member infos
            pass
        if h4 == "媒体报道":
            pass

    artifacts = []

    if desc is None:
        desc = brief

    if brief is not None and len(brief.decode('utf-8')) > 200:
        brief = None

    type, app_market, app_id = url_helper.get_market(website)
    if type == 4010:
        if item["url"] != website:
            flag, domain = url_helper.get_domain(website)
            if flag is not None:
                if flag is False:
                    domain = None
                artifacts.append({
                    "type": 4010,
                    "name": name,
                    "description": desc,
                    "link": website,
                    "domain": domain
                })
    elif type == 4040:
        domain = app_id
        if domain is not None:
            artifacts.append({
                "type": 4040,
                "name": name,
                "description": desc,
                "link": website,
                "domain": domain
            })
    elif type == 4050:
        domain = None
        if app_market == 16010 or app_market == 16020:
            android_app = parser_db_util.find_android_market(app_market, app_id)
            if android_app:
                domain = android_app["apkname"]
        else:
            domain = app_id
        if domain is not None:
            artifacts.append({
                "type": 4050,
                "name": name,
                "description": desc,
                "link": website,
                "domain": domain
            })

    #logger.info("Desc: %s", desc)
    #logger.info("round: %s, roundDesc: %s", round, roundDesc)

    source_company = {
        "name": name,
        "fullName": None,
        "description": desc,
        "productDesc": None,
        "modelDesc": None,
        "operationDesc": None,
        "teamDesc": None,
        "marketDesc": None,
        "compititorDesc": None,
        "advantageDesc": None,
        "planDesc": None,
        "brief": brief,
        "round": round,
        "roundDesc": roundDesc,
        "companyStatus": 2010,
        'fundingType': 0,
        "locationId": None,
        "address": None,
        "phone": None,
        "establishDate": None,
        "logo": logo,
        "source": SOURCE,
        "sourceId": company_key,
        "field": None,
        "subField": None,
        "tags": None,
        "headCountMin": None,
        "headCountMax": None,
        "artifacts": artifacts,
        "fundings": source_fundings,
        "status": 1
    }

    #for i in source_company:
    #    logger.info("%s -> %s", i, source_company[i])
    return source_company

def parseFinance_save(source_company_id, fundings, download_crawler):
    if len(fundings) == 0:
        return True
    flag = True
    for funding in fundings:

        source_funding = {
            "sourceCompanyId": source_company_id,
            "preMoney": None,
            "postMoney": None,
            "investment": funding['investment'],
            "precise": funding['precise'],
            "round": funding['round'],
            "roundDesc": funding['roundDesc'],
            "currency": funding['currency'],
            "fundingDate": funding['fundingDate'],
        }
        logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))

        source_investors = []
        for investor in funding['investors']:
            source_investor_id = parser_db_util.find_source_investor_id(SOURCE, investor['key'])
            if source_investor_id:
                source_investor = {
                    "source_investor_id" : source_investor_id["id"]
                }
                source_investors.append(source_investor)
            else:
                logger.info("No investor %s", investor['name'])
                flag = False
        logger.info(json.dumps(source_investors, ensure_ascii=False, cls=util.CJsonEncoder))
        parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)

    return flag


if __name__ == "__main__":
    # while True:
    #     process()
    #     #break   #test
    #     time.sleep(30*60)
    process()