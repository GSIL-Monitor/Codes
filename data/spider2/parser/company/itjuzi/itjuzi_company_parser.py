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
import util, download, name_helper, url_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

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
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)
        # items = [parser_db_util.find_process_one(SOURCE, TYPE, 33045986)]
        for item in items:
            logger.info(item["url"])

            r = parse_base(item)
            if r is None:
                continue
            source_company_id = parser_db_util.save_company(r, SOURCE, download_crawler)
            parser_db_util.delete_source_company_name(source_company_id)
            parser_db_util.delete_source_mainbeianhao(source_company_id)
            parser_db_util.save_source_company_name(source_company_id, r["shortName"],12020)
            parser_db_util.save_source_company_name(source_company_id, r["productName"],12020)
            if r["fullName"] is not None:
                parser_db_util.save_source_company_name(source_company_id, r["fullName"],12010)
                main_company_name = name_helper.get_main_company_name(r["fullName"])
                if main_company_name != r["fullName"]:
                    parser_db_util.save_source_company_name(source_company_id, main_company_name,12010)

            logger.info("source_company_id=%s", source_company_id)

            artifacts = parse_artifact(item)
            flag = False
            if len(artifacts) > 0:
                flag = True

            artifacts.extend(r["artifacts"])
            logger.info(artifacts)
            parser_db_util.save_artifacts(source_company_id, artifacts)

            footprints = parse_footprint(item)
            parser_db_util.save_footprints(source_company_id, footprints)

            # members = parse_member(item)
            # parser_db_util.save_member_rels(source_company_id, members, SOURCE)
            parseMember_save(source_company_id, item, download_crawler)

            parser_db_util.update_processed(item["_id"])

            #if flag:
        # break
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
    product_name = d('div.line-title> span> h1').clone().children().remove().end().text().strip()
    if product_name is None or product_name.strip() == "":
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

    if company_name is None or company_name.strip() == "":
        try:
            company_name = d('div.des-more> h2').text().strip()
        except:
            pass
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
        result = parser_db_util.get_location(city)
        if result != None:
            locationId = result["locationId"]
        else:
            result = parser_db_util.get_location(province)
            if result != None:
                locationId = result["locationId"]

    if locationId == 0:
        loc1,loc2 = name_helper.get_location_from_company_name(company_name)
        if loc1 is not None:
            result = parser_db_util.get_location(loc1)
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
    try:
        brief = d("h2.seo-slogan").text().strip()
    except:
        brief = ""
    logger.info("brief: %s" % brief)

    if brief.find("暂未收录"):
        brief = ""
    field = d("span.scope.c-gray-aset> a").eq(0).text().strip()
    logger.info("field: %s" % field)

    sub_field = d("span.scope.c-gray-aset> a").eq(1).text().strip()
    logger.info("sub field: %s" % sub_field)

    tags = d("div.tagset.dbi.c-gray-aset> a >span").text().strip().replace(" ",",")
    logger.info("tags: %s" % tags)

    desc = d("div.des,div.desc,div.introduction,div.abstract,div.summary").text().\
        replace("购买数据请联系","").replace('hello@itjuzi.com',"").replace("itjuzi是一家数据服务公司","").strip()
    logger.info("********desc: %s" % desc)

    #logo
    logo = d("div.pic >img").attr("src")
    #if logo:
    #    logo = logo.replace("http://", "https://")
    logger.info("logo: %s", logo)


    # website = d('div.link-line> a').text().strip()
    # if website is None or website == "":
    #     website = d('div.link-line> a.webTink').text().strip()
    # if website is None or website == "":
    #     try:
    #         logger.info("here")
    #         website = d('div.link-line> span.weblink> a').eq(1).text().strip()
    #         logger.info(website)
    #     except:
    #         pass
    artifacts = []
    for ty in [1,2,3]:
        if ty == 1:
            was = d('div.link-line> a')
        else:
            was = d('div.link-line> span.weblink,span.webTink> a')

        for wa in was:
            webs =[]

            try:
                website = pq(wa).attr("href").strip()
                if website=="http://%e6%9a%82%e6%97%a0" or website == "http://tt":
                    website = ""
                website = url_helper.url_normalize(website)
                logger.info("website: %s" % website)
                webs.append(website)
            # else:

            #     website = pq(wa).text().strip()
            except:
                pass
            try:
                website = pq(wa).text().strip()
                if website == "http://%e6%9a%82%e6%97%a0" or website == "http://tt":
                    website = ""
                website = url_helper.url_normalize(website)
                logger.info("website: %s" % website)
                webs.append(website)
            # else:
            #     website = pq(wa).text().strip()
            except:
                pass

            #
            # if website=="http://%e6%9a%82%e6%97%a0":
            #     website = ""
            # website = url_helper.url_normalize(website)
            # logger.info("website: %s" % website)

            # artifacts = []
            for website in webs:
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

                elif type == 4020:
                    domain = app_id
                    if domain is not None:
                        artifacts.append({
                            "type": 4020,
                            "name": product_name,
                            "desc": None,
                            "link": website,
                            "domain": website
                        })

                elif type == 4030:
                    domain = app_id
                    if domain is not None:
                        artifacts.append({
                            "type": 4030,
                            "name": product_name,
                            "desc": None,
                            "link": website,
                            "domain": None
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
                        android_app = parser_db_util.find_android_market(app_market, app_id)
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
        "shortName": company_short_name,
        "fullName": company_name if company_name is not None and company_name.strip() != "" else None,
        "productName": product_name,
        "description": desc,
        "brief": brief,
        "round": fundingRound,
        "roundDesc": roundStr,
        "companyStatus": company_status,
        "fundingType": funding_type,
        "locationId": locationId,
        "establishDate": establish_date,
        "logo": logo,
        "sourceId": company_key,
        "field": field,
        "subField": sub_field,
        "tags": tags,
        "type":41010,
        "artifacts":artifacts
    }

def parse_artifact(item):
    if item is None:
        return None

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
                    android_app = parser_db_util.find_android_market(app_market, app_id)
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
        return None

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


def parseMember_save(source_company_id, item, download_crawler):
    if item is None:
        return None

    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)

    members = []
    # members
    logger.info("*** member ****")
    lis = d('ul.team-list> li')
    for li in lis:
        try:
            l = pq(li)
            member_name = l('div.per-name> a').text().strip()
            member_key = l('div.per-name> a').attr("href").split("/")[-1]
            position = l('div.per-position').text().strip()
            logo = l('a.avatar> img').attr("src")
            desc = l('div.per-des').text().strip()

            logger.info(
                "member_key: %s, member_name: %s, position: %s, desc: %s" % (member_key, member_name, position, desc))
            source_member = {
                "source": SOURCE,
                "sourceId": str(member_key),
                "name": member_name,
                "photo_url": logo,
                "weibo": None,
                "location": 0,
                "role": position,
                "description": desc,
                "education": None,
                "work": None
            }
            # member = {
            #     "key":member_key,
            #     "name":member_name,
            #     "position":position
            # }

            ptype = name_helper.position_check(position)

            source_company_member_rel = {
                "sourceCompanyId": source_company_id,
                "position": position,
                "joinDate": None,
                "leaveDate": None,
                "type": ptype
            }

            parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
            # members.append(member)
        except Exception,ex:
            logger.exception(ex)

    logger.info("")
    return members

if __name__ == "__main__":
    process()