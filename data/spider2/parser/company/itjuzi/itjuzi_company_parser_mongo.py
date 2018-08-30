# -*- coding: utf-8 -*-
import os, sys
import datetime
from pyquery import PyQuery as pq
import json
import itjuzi_helper

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, download, name_helper, url_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util2'))
import parser_mongo_util

#logger
loghelper.init_logger("itjuzi_company_parser", stream=True)
logger = loghelper.get_logger("itjuzi_company_parser")

SOURCE = 13030  #ITJUZI
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(max_crawl=200, timeout=10)

def process():
    logger.info("itjuzi_company_parser begin...")

    start = 0
    while True:
        items = parser_mongo_util.find_process_limit(SOURCE, TYPE, start, 1000)
        for item in items:
            logger.info(item["url"])

            r = parse_base(item)
            if r is None:
                continue
            #source_company_id = parser_db_util.save_company(r, SOURCE, download_crawler)
            parser_mongo_util.save_mongo_company(r["source"], r["sourceId"], r)
            # parser_db_util.delete_source_company_name(source_company_id)
            # parser_db_util.delete_source_mainbeianhao(source_company_id)
            # parser_db_util.save_source_company_name(source_company_id, r["shortName"],12020)
            # parser_db_util.save_source_company_name(source_company_id, r["productName"],12020)
            # parser_db_util.save_source_company_name(source_company_id, r["fullName"],12010)
            parser_mongo_util.save_mongo_source_company_name(r["source"], r["sourceId"], {"name": r["shortName"], "type": 12020})
            parser_mongo_util.save_mongo_source_company_name(r["source"], r["sourceId"], {"name": r["productName"], "type": 12020})
            parser_mongo_util.save_mongo_source_company_name(r["source"], r["sourceId"], {"name": r["fullName"], "type": 12020})
            main_company_name = name_helper.get_main_company_name(r["fullName"])
            if main_company_name != r["fullName"]:
                parser_mongo_util.save_mongo_source_company_name(r["source"], r["sourceId"], {"name": main_company_name, "type": 12020})

            # logger.info("source_company_id=%s", source_company_id)

            artifacts = parse_artifact(item)
            artifacts.extend(r["artifacts"])
            logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))
            # parser_db_util.save_artifacts(source_company_id, artifacts)
            for artifact in artifacts:
                parser_mongo_util.save_mongo_source_artifact(r["source"], r["sourceId"], artifact)

            #TODO FOOTPRINTS
            # footprints = parse_footprint(item)
            # parser_db_util.save_footprints(source_company_id, footprints)

            members = parse_member(item)
            # parser_db_util.save_member_rels(source_company_id, members, SOURCE)
            for member in members:
                parser_mongo_util.save_mongo_source_company_member(r["source"], r["sourceId"], member)

            parser_mongo_util.update_processed(item["_id"])
            parser_mongo_util.update_processStatus(r["source"], r["sourceId"])

            #if flag:
            #break
        start += 1000
        if len(items) == 0:
            break

    logger.info("itjuzi_company_parser end.")


def parse_base(item):
    if item is None:
        return None

    logger.info("*** base ***")
    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    company_short_name = ""
    product_name = d('div.line-title> span> b').clone().children().remove().end().text().strip()
    temps = product_name.split("/",1)
    if len(temps) == 2:
        product_name = temps[0].strip()
        company_short_name = temps[1].strip()
    if company_short_name == "":
        company_short_name = product_name
    logger.info("product name: %s" % product_name)
    logger.info("company short name: %s" % company_short_name)

    company_name = d('div.des-more> div').eq(0).text().strip().replace("公司全称：","")
    if company_name == "暂无" or company_name == "暂未收录":
        company_name = ""
    company_name = name_helper.company_name_normalize(company_name)
    logger.info("company name: %s" % company_name)

    if company_short_name == "" and company_name == "":
        return

    establish_date = None
    str = d('div.des-more> div').eq(1).text().strip().replace("成立时间：","")
    result = util.re_get_result('(\d*)\.(\d*)',str)
    if result != None:
        (year, month) = result
        try:
            if int(month) > 12:
                month = "1"
        except:
            month = "1"
        establish_date = datetime.datetime.strptime("%s-%s-1" % (year,month), '%Y-%m-%d')
    logger.info("establish date: %s" % establish_date)

    locationId=0
    str = d('span.loca').text().strip()
    #logger.info(str)
    result = util.re_get_result(u'(.*?)·(.*?)$',str)
    if result != None:
        (province, city) = result
        province = province.strip()
        city = city.strip()
        logger.info("location: %s-%s" % (province, city))

        locationId = 0
        result = parser_mongo_util.get_location(city)
        if result != None:
            locationId = result["locationId"]
        else:
            result = parser_mongo_util.get_location(province)
            if result != None:
                locationId = result["locationId"]

    if locationId == 0:
        loc1,loc2 = name_helper.get_location_from_company_name(company_name)
        if loc1 is not None:
            result = parser_mongo_util.get_location(loc1)
            if result != None:
                locationId = result["locationId"]
    logger.info("locationId: %d" % locationId)

    company_status = 2010
    str = d('div.des-more> div').eq(2).text().strip()
    if str == "已关闭":
        company_status = 2020
    logger.info("company_status: %d" % company_status)

    funding_type = 0
    str = d("span.tag.bg-c").text().strip()
    logger.info("融资需求: %s" % str)
    if str == "融资需求 · 需要融资":
        funding_type = 8020
    elif str == "融资需求 · 寻求收购":
        funding_type = 8020
    logger.info("funding_type=%d" % funding_type)

    field = d("span.scope.c-gray-aset> a").eq(0).text().strip()
    logger.info("field: %s" % field)

    sub_field = d("span.scope.c-gray-aset> a").eq(1).text().strip()
    logger.info("sub field: %s" % sub_field)

    tags = d("div.tagset.dbi.c-gray-aset> a >span").text().strip().replace(" ",",")
    logger.info("tags: %s" % tags)

    desc = d("div.des").text().strip()
    logger.info("desc: %s" % desc)

    #logo
    logo = d("div.pic >img").attr("src")
    #if logo:
    #    logo = logo.replace("http://", "https://")
    logger.info("logo: %s", logo)

    website = d('div.link-line> a.weblink').attr("href").strip()
    if website=="http://%e6%9a%82%e6%97%a0":
        website = ""
    website = url_helper.url_normalize(website)
    logger.info("website: %s" % website)

    artifacts = []
    type, app_market, app_id = url_helper.get_market(website)
    if type == 4010:
        flag, domain = url_helper.get_domain(website)
        if flag is not None:
            if flag is False:
                domain = None
            artifacts.append({
                "type":4010,
                "name":product_name,
                "desc":desc,
                "link":website,
                "domain": domain
            })
    elif type == 4040:
        domain = app_id
        if domain is not None:
            artifacts.append({
                    "type":4040,
                    "name":product_name,
                    "desc":desc,
                    "link":website,
                    "domain": domain
            })
    elif type == 4050:
        domain = None
        if app_market == 16010 or app_market == 16020:
            android_app = parser_mongo_util.find_android_market(app_market, app_id)
            if android_app:
                domain = android_app["apkname"]
        else:
            domain = app_id
        if domain is not None:
            artifacts.append({
                "type":4050,
                "name":product_name,
                "desc":desc,
                "link":website,
                "domain": domain
            })

    #获投状态
    roundStr = d('span.t-small.c-green').text().replace("(","").replace(")","").replace("获投状态：","").strip()
    fundingRound,roundStr = itjuzi_helper.getFundingRound(roundStr)
    logger.info("获投状态: %d, %s", fundingRound, roundStr)

    logger.info("")


    return {
        "name": product_name,
        "shortName": company_short_name,
        "fullName": company_name,
        "productName": product_name,
        "description": desc,
        "brief": "",
        "round": fundingRound,
        "roundDesc": roundStr,
        "companyStatus": company_status,
        "fundingType": funding_type,
        "locationId": locationId,
        "establishDate": establish_date,
        "logo": logo,
        "source": SOURCE,
        "sourceId": company_key,
        "field": field,
        "subField": sub_field,
        "tags": tags,
        "type":41010,
        "artifacts":artifacts
    }

def parse_artifact(item):
    if item is None:
        return []

    artifacts = []
    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    #artifact
    logger.info("*** artifact ***")
    lis = d('ul.list-prod> li> div.on-edit-hide')
    for li in lis:
        l = pq(li)
        strtype = l('h4> span.tag').text().strip()
        #logger.info(strtype)
        if strtype != u"网站" and strtype != "app":
            continue

        link = l('h4> b> a').attr("href").strip()
        if link == "":
            continue

        domain = None
        type = None
        if strtype == u"网站":
            type, app_market, app_id = url_helper.get_market(link)
            if type == 4010:
                link = url_helper.url_normalize(link)
                flag, domain = url_helper.get_domain(link)
                if flag is None:
                    continue
                if flag is False:
                    domain = None

        if type != 4010:
            type, app_market, app_id = url_helper.get_market(link)
            if type == 4040:
                domain = app_id
            elif type == 4050:
                if app_market == 16010 or app_market == 16020:
                    android_app = parser_mongo_util.find_android_market(app_market, app_id)
                    if android_app:
                        domain = android_app["apkname"]
                else:
                    domain = app_id
            if domain is None and type !=4030 and type != 4020:
                continue

        name = l('h4> b').text().strip()
        desc = l('p').text().strip()
        logger.info("type: %s, name: %s, link: %s, desc: %s" % (type, name,link,desc))
        artifact = {
            "type":type,
            "name":name,
            "desc":desc,
            "link":link,
            "domain": domain
        }
        artifacts.append(artifact)

    logger.info("")
    return artifacts


def parse_footprint(item):
    if item is None:
        return []

    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    footprints = []
    #footprint
    logger.info("*** footprint ***")
    lis = d('ul.list-milestone> li')
    for li in lis:
        l = pq(li)
        footDesc = l('div> p').eq(0).text().strip()
        logger.info(footDesc)
        if footDesc is None or footDesc == "":
            continue
        footDateText = l('div> p> span.t-small').text().strip()
        logger.info(footDateText)
        if footDateText is None or footDateText == "":
            continue
        result = util.re_get_result('(\d*?)\.(\d*?)$',footDateText)
        if result == None:
            continue
        (year, month) = result
        year = int(year)
        try:
            month = int(month)
        except:
            month = 1

        if month<=0 or month>12:
            month = 1
        if year < 1970 or year > 3000:
            year = 1970
        footDate = datetime.datetime.strptime("%s-%s-1" % (year,month), '%Y-%m-%d')
        logger.info("%s: %s", footDate, footDesc)
        footprint = {"footDate":footDate, "footDesc":footDesc}
        footprints.append(footprint)
    logger.info("")
    return footprints


def parse_member(item):
    if item is None:
        return []

    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    members = []
    # members
    logger.info("*** member ****")
    lis = d('ul.list-prodcase> li')
    for li in lis:
        try:
            l = pq(li)
            member_name = l('h4> a> b> span.c').text().strip()
            position = l('h4> a> b> span.c-gray').text().strip()
            str = l('h4> a').attr("href").strip()
            (member_key,) = util.re_get_result(r'person/(\d*?)$',str)
            logger.info("member_key: %s, member_name: %s, position: %s" % (member_key, member_name, position))
            memberId = parser_mongo_util.find_mongo_memberId(SOURCE, member_key)
            if memberId is None:
                continue
            type = name_helper.position_check(position)
            member = {
                "_memberId":memberId,
                "name":member_name,
                "position":position,
                "type": type
            }
            members.append(member)
        except Exception,ex:
            logger.exception(ex)

    logger.info("")
    return members

if __name__ == "__main__":
    process()