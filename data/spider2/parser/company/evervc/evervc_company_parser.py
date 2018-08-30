# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../itjuzi'))
import itjuzi_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../kr36'))
import kr36_company_parser_2

# logger
loghelper.init_logger("evervc_company_parser", stream=True)
logger = loghelper.get_logger("evervc_company_parser")

SOURCE = 13838  # evervc
TYPE = 36001  # 公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


def parseFinance_save(source_company_id, item, sourceId, download_crawler):
    logger.info("parseFinance_save")
    if item is None:
        return None

    d = pq(html.fromstring(item['content'].decode("utf-8")))
    finances = d('.funding-info tbody tr')

    for finance in finances:
        roundStr = d(finance)('td:nth-child(1)').text()
        fundingRound, roundStr = itjuzi_helper.getFundingRound(roundStr)

        fundingInvestment = d(finance)('.amount').text()
        if fundingInvestment.find('￥ ') >= 0:
            fundingInvestment = fundingInvestment.replace('￥ ', '') + '人民币'
        elif fundingInvestment.find('$ ') >= 0:
            fundingInvestment = fundingInvestment.replace('$ ', '') + '美元'
        else:
            logger.info('not RMB:%s %s', sourceId, fundingInvestment)  # todo
            exit()

        fundingCurrency, fundingInvestment, precise = itjuzi_helper.getMoney(fundingInvestment)

        fundingDate = datetime.datetime.strptime(d(finance)('.date').text(), '%Y-%m-%d')

        source_funding = {
            "sourceCompanyId": source_company_id,
            "preMoney": None,
            "postMoney": None,
            "investment": fundingInvestment,
            "precise": precise,
            "round": fundingRound,
            "roundDesc": roundStr,
            "currency": fundingCurrency,
            "fundingDate": fundingDate,
            "newsUrl": None
        }

        # logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))
        if fundingInvestment == 0:
            logger.info("new invest case: %s", sourceId)
            exit()
        logger.info("%s, %s, %s, %s", roundStr, fundingRound, fundingInvestment, fundingCurrency)

        source_investors = []

        investors = d(finance)('.investor a')
        for investor in investors:
            entityName = d(investor).text().strip()
            logger.info(entityName)
            entityId = str(d(investor).attr('href').split('startups/')[-1])

            source_investor = {
                "name": entityName,
                "website": None,
                "description": None,
                "logo_url": None,
                "stage": None,
                "field": None,
                "type": 10020,
                "source": SOURCE,
                "sourceId": entityId
            }
            source_investors.append(source_investor)

        logger.info(json.dumps(source_investors, ensure_ascii=False, cls=util.CJsonEncoder))
        try:
            parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)
        except:
            pass


def parseMember_save(source_company_id, item, download_crawler):
    logger.info("parseMember_save")

    companyKey = item["key"]
    d = pq(html.fromstring(item['content'].decode("utf-8")))
    members = d('.startups-member')
    for m in members:
        name = d(m)('.media-heading').text()
        logger.info(name)

        desc = d(m)('.desc').text()
        position = d(m)('.title').text()

        logo = 'http:' + d(m)(".media-object").attr('src').replace('@!logom', '')
        if logo.find('deafult') >= 0 or logo.find('default') >= 0: logo = None

        if logo:
            logo = logo.replace("https://", "http://")

        sourceId = d(m)('.media-body a').attr('href')
        if sourceId is not None:
            sourceId = str(companyKey) + '_' + sourceId.split('person/')[-1].strip()
        else:
            sourceId = str(companyKey) + '_' + kr36_company_parser_2.get_company_code(name)

        source_member = {
            "source": SOURCE,
            "sourceId": sourceId,
            "name": name,
            "photo_url": logo,
            "weibo": None,
            "location": 0,
            "role": position[:50],
            "description": desc,
            "education": None,
            "work": None
        }
        ptype = name_helper.position_check(position)

        source_company_member_rel = {
            "sourceCompanyId": source_company_id,
            "position": position[:50],
            "joinDate": None,
            "leaveDate": None,
            "type": ptype
        }
        try:
            parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
            # logger.info(source_member)
            # logger.info(source_company_member_rel)
        except Exception, ex:
            logger.info("%s:%s", Exception, ex)
            exit()


def parse_artifact(source_company_id, r):
    type, market, app_id = url_helper.get_market(r['website'])
    artifacts = []

    if type == 4010 and r['website'].strip() != '' and r['website'] is not None:
        artifact = {
            "sourceCompanyId": source_company_id,
            "name": r["name"],
            "description": None,
            "link": r['website'],
            "domain": app_id,
            "type": type
        }
        artifacts.append(artifact)

    return artifacts


def parse_company(item):
    # logger.info("parse_company")

    d = pq(html.fromstring(item['content'].decode("utf-8")))
    company_key = item["key"]

    # company basic info
    tags = []

    for tag in d('.portfolio-user-tag .label').text().split():
        if tag.strip() not in tags: tags.append(tag.strip())

    tags_str = ",".join(tags)

    logo = 'http:' + d('.portfolio-user-photo img').attr('src')
    if logo:
        logo = logo.replace("https://", "http://")
        logo = logo.replace("@!msgs", "")

    establish_date = None

    companyName = d('.corp-name').text()

    location_id = 0
    city = d('.portfolio-user-tag').text().split(' ')[0]
    if city != None: location = parser_db_util.get_location(city)
    if location is None: city = name_helper.get_location_from_company_name(companyName)[0]

    if city != None:
        location = parser_db_util.get_location(city)
        if location != None:
            location_id = location["locationId"]

    # logger.info("locationid =%s",location_id)

    fullName = companyName.replace("_", "")
    fullName = name_helper.company_name_normalize(fullName)

    # desc = d('.portfolio-corp p').text()
    desc = d('.portfolio-user-bio .text').text()
    productDesc = d('.portfolio-text').text()

    website = d('.user-contact a').text()

    if desc == '' or desc is None: desc = productDesc

    shortName = d('.portfolio-user-info h1').text()

    companyResult = {}

    companyResult.update({
        "name": shortName,
        "fullName": fullName,
        "description": desc,
        "productDesc": productDesc,
        "round": 0,
        "roundDesc": None,
        "companyStatus": 2010,
        'fundingType': 0,
        "locationId": location_id,
        "address": None,
        "phone": None,
        "establishDate": None,
        "logo": logo,
        "source": SOURCE,
        "sourceId": company_key,
        "field": None,
        "subField": None,
        "tags": tags_str,
        "headCountMin": None,
        "headCountMax": None,
        "brief": None,
        "website": website,

    })

    return companyResult


def process(sourceId=0):
    logger.info("evervc_company_parser begin...")

    start = 0
    while True:
        if sourceId > 0:
            items = [parser_db_util.find_process_one(SOURCE, TYPE, sourceId)]
        else:
            items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)

        for item in items:
            r = parse_company(item)
            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

            source_company_id = parser_db_util.save_company_standard(r, download_crawler)
            parser_db_util.delete_source_company_name(source_company_id)
            parser_db_util.delete_source_mainbeianhao(source_company_id)
            parser_db_util.save_source_company_name(source_company_id, r["fullName"], 12010)
            if len(r["name"])<len(r["fullName"]) or r['fullName'] is None or r["fullName"]=='':
                parser_db_util.save_source_company_name(source_company_id, r["name"], 12020)
            main_company_name = name_helper.get_main_company_name(r["fullName"])
            if main_company_name != r["fullName"]:
                parser_db_util.save_source_company_name(source_company_id, main_company_name, 12010)
            logger.info("source_company_id=%s", source_company_id)

            artifacts = parse_artifact(source_company_id, r)
            logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))

            parser_db_util.save_artifacts_standard(source_company_id, artifacts)

            parseMember_save(source_company_id, item, download_crawler)

            parser_db_util.delete_funding(source_company_id)  ##??
            flag = parseFinance_save(source_company_id, item, r['sourceId'], download_crawler)
            flag = True

            if flag:
                parser_db_util.update_processed(item["_id"])
                logger.info("processed %s", item["url"])
            else:
                logger.info("lack something:  %s", item["url"])

                # break

        # start += 1000  # todo
        if len(items) == 0 or sourceId > 0:
            break

    logger.info("evervc_company_parser end.")


def tes():
    item = parser_db_util.find_process_one(13838, 36001, 85131)
    parseMember_save(1, item, download_crawler)
    exit()
    parse_company(item)

    # parseMember_save(1, 1, item, download_crawler)
    parseFinance_save(1, item, 71554, download_crawler)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = int(sys.argv[1])
        process(param)
    else:
        while True:
            process()
            time.sleep(30 * 60)


