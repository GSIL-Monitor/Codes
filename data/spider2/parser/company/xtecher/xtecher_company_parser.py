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

# logger
loghelper.init_logger("xtecher_company_parser", stream=True)
logger = loghelper.get_logger("xtecher_company_parser")

SOURCE = 13821  # xtecher
TYPE = 36001  # 公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


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
    for tag in d('.word_list').text().split():
        if tag.strip() not in tags: tags.append(tag)

    tags_str = ",".join(tags)

    logo = d('.peoimg img').attr('src')
    if logo:
        logo = logo.replace("https://", "http://")

    establish_date = None
    time_content = d('.time_content li:last-child')
    if d(time_content)('.upword').text().find('成立') > 0:
        establish_date = d(time_content)('.time_up').text()
        establish_date = datetime.datetime.strptime(establish_date, '%Y-%m-%d')

    companyName = d('.company_div h5').text()
    city = name_helper.get_location_from_company_name(companyName)[0]
    location_id = 0
    if city != None:
        location = parser_db_util.get_location(city)
        if location != None:
            location_id = location["locationId"]

    # logger.info("locationid =%s",location_id)

    fullName = companyName.replace("_", "")
    fullName = name_helper.company_name_normalize(fullName)

    desc = d('#intro_srocll p').text()
    productDesc = ''
    website = ''
    for p in d('.procont_lis p'):
        if d(p).text().find('官网') > 0 and d(p)('a').attr('href') is not None:
            website = d(p)('a').attr('href')
            continue
        productDesc += d(p).text() + '\n'

    if desc == '' or desc is None: desc = productDesc

    shortName = d('.peo_center h4').text().split('：')[0].split(':')[0].split('——')[0].split('，')[0].split('｜')[0]

    companyResult={}
    # isCompany
    # print companyName,company_key, ',', name_helper.name_check(companyName)[1], ',', len(website)>0
    if name_helper.name_check(companyName)[1] == True:
        # English name
        if name_helper.name_check(shortName)[0] == False:
            pass
        else:
            cnt = 0
            for s in shortName:
                if s in companyName: cnt += 1

            if not cnt > 2:
                shortName = companyName
    else:
        if not len(website) > 0:
            return 0
        else:
            companyResult['fakeName']=fullName
            fullName = None

    companyResult.update({
        "name": shortName,
        "fullName": fullName,
        "description": desc,
        "round": 0,
        "roundDesc": None,
        "companyStatus": 2010,
        'fundingType': 0,
        "locationId": location_id,
        "address": None,
        "phone": None,
        "establishDate": establish_date,
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


def process():
    logger.info("xtecher_company_parser begin...")

    start = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)

        for item in items:
            r = parse_company(item)
            if r == 0:
                parser_db_util.update_processed(item["_id"])
                logger.info("missing website and companyName, processed %s", item["url"])
                continue

            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

            source_company_id = parser_db_util.save_company_standard(r, download_crawler)
            parser_db_util.delete_source_company_name(source_company_id)
            parser_db_util.delete_source_mainbeianhao(source_company_id)
            parser_db_util.save_source_company_name(source_company_id, r["name"], 12020)
            if r.has_key('fakeName'):
                parser_db_util.save_source_company_name(source_company_id, r["fakeName"], 12020)
            else:
                parser_db_util.save_source_company_name(source_company_id, r["fullName"], 12010)
                main_company_name = name_helper.get_main_company_name(r["fullName"])
                if main_company_name != r["fullName"]:
                    parser_db_util.save_source_company_name(source_company_id, main_company_name, 12010)
            logger.info("source_company_id=%s", source_company_id)

            artifacts = parse_artifact(source_company_id, r)
            logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))

            parser_db_util.save_artifacts_standard(source_company_id, artifacts)

            # parser_db_util.delete_funding(source_company_id)
            # flag=parseFinance_save(source_company_id,item, download_crawler)
            flag = True

            if flag:
                parser_db_util.update_processed(item["_id"])
                logger.info("processed %s", item["url"])
            else:
                logger.info("lack something:  %s", item["url"])

                # break
        # start += 1000  # todo
        if len(items) == 0:
            break

    logger.info("xtecher_company_parser end.")


if __name__ == "__main__":
    while True:
        process()
        # break   #test
        time.sleep(30 * 60)
