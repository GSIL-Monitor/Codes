# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from kr36_location import kr36_cities


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("36kr_company_parser", stream=True)
logger = loghelper.get_logger("36kr_company_parser")

SOURCE = 13020  #36kr
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)

def formCityName(name):
    if name.endswith("市"):
        return name.split("市")[0]
    if name.endswith("县"):
        return name.split("县")[0]
    return name


def process():
    logger.info("36kr_company_parser begin...")

    start = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)

        for item in items:
            r = parse_company(item)
            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))
            if r["status"] == "INIT" :
                parser_db_util.update_active(SOURCE, item["key"], 'N')
                parser_db_util.update_processed(item["_id"])
                logger.info("processed %s" ,item["url"])
                continue

            source_company_id = parser_db_util.save_company_standard(r, download_crawler)
            parser_db_util.delete_source_company_name(source_company_id)
            parser_db_util.delete_source_mainbeianhao(source_company_id)
            parser_db_util.save_source_company_name(source_company_id, r["name"],12020)
            parser_db_util.save_source_company_name(source_company_id, r["fullName"],12010)
            main_company_name = name_helper.get_main_company_name(r["fullName"])
            if main_company_name != r["fullName"]:
                parser_db_util.save_source_company_name(source_company_id, main_company_name,12010)
            logger.info("source_company_id=%s", source_company_id)

            artifacts=parse_artifact(source_company_id,item)
            logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))

            if (r["fullName"] is None or r["fullName"].strip() == "") and (r['description'] is None or r['description'].strip() == "") \
                and len(artifacts) == 0:
                parser_db_util.update_active(SOURCE, item["key"], 'N')
                parser_db_util.update_processed(item["_id"])
                logger.info("missing all stuff, processed %s", item["url"])
                continue

            parser_db_util.save_artifacts_standard(source_company_id, artifacts)

            # parser_db_util.delete_funding(source_company_id)
            # flag=parseFinance_save(source_company_id,item, download_crawler)
            flag = True

            if item["content"].has_key("founders") and item["content"]["founders"]["data"].has_key("data"):
                parseMember_save(source_company_id,5010,item["content"]["founders"]["data"]["data"], download_crawler)
            if item["content"].has_key("employees") and item["content"]["employees"]["data"].has_key("data"):
                parseMember_save(source_company_id,5030,item["content"]["employees"]["data"]["data"], download_crawler)
            if item["content"].has_key("former_members") and item["content"]["former_members"]["data"].has_key("data"):
                parseMember_save(source_company_id,5040,item["content"]["former_members"]["data"]["data"],download_crawler)

            if flag:
                parser_db_util.update_processed(item["_id"])
                logger.info("processed %s" ,item["url"])
            else:
                logger.info("lack something:  %s", item["url"])

            #break
        start += 1000
        if len(items) == 0:
            break

    logger.info("36kr_company_parser end.")


def parse_company(item):
    logger.info("parse_company")
    company_key = item["key"]

    #company basic info
    c = item["content"]["company_base"]["data"]["company"]
    #check if page is under development or is completed(CREATED)
    if c["status"] == "INIT":
        return {
            "status":c["status"],
        }

    tags = item["content"]["company_base"]["data"]["tags"]
    tags2 = []
    for tag in tags:
        tags2.append(tag["name"])
    tags_str = ",".join(tags2)

    logo=c["logo"]
    if logo:
        logo = logo.replace("https://","http://")
    establish_date = None
    if c.has_key("startDate"):
        d = time.localtime(c["startDate"]/1000)
        if d.tm_year > 1980:
            establish_date = datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)

    address1 = None
    address2 = None
    if c.has_key("address1"):
        address1 = c["address1"]
    if c.has_key("address2"):
        address2 = c["address2"]

    location_id = 0
    if address2!=None:
        city = kr36_cities.get(str(address2),None)
        if city != None:
            location = parser_db_util.get_location(formCityName(city))
            if location != None:
                location_id= location["locationId"]

    if location_id==0 and address1 != None:
        city = kr36_cities.get(str(address1),None)
        if city != None:
            location = parser_db_util.get_location(formCityName(city))
            if location != None:
                location_id = location["locationId"]

    #logger.info("locationid =%s",location_id)

    fullName = c["fullName"]
    fullName = fullName.replace("_","")
    idx = fullName.rfind(u"公司")
    if idx != -1:
        fullName = fullName[:(idx+len(u"公司"))]
    fullName = name_helper.company_name_normalize(fullName)

    desc = ""
    productDesc = None
    modelDesc = None
    operationDesc = None
    teamDesc = None
    marketDesc = None
    compititorDesc = None
    advantageDesc = None
    planDesc = None
    otherDesc = None

    if c.has_key("projectAdvantage"): # 我们的产品与优势
        productDesc = c["projectAdvantage"].strip()
    if c.has_key("dataLights"): # 我们的用户
        operationDesc = c["dataLights"].strip()
    if c.has_key("projectPlan"): # 未来的我们
        modelDesc = c["projectPlan"].strip()
    if c.has_key("competitor"): # 与我们相似的产品
        compititorDesc = c["competitor"].strip()
    if c.has_key("intro"):  # 其他
        # otherDesc = c["intro"].strip()
        desc = c["intro"].strip()
    if c.has_key("story"): # 团队介绍
        teamDesc = c["story"].strip()

    '''
    if productDesc or operationDesc or modelDesc or compititorDesc or teamDesc:
        desc = ""
        if productDesc:
            desc += u"<p>我们的产品与优势</p>\n" + "<pre>" + productDesc + "</pre>\n"
        if operationDesc:
            desc += u"<p>我们的用户</p>\n" + "<pre>" + operationDesc + "</pre>\n"
        if modelDesc:
            desc += u"<p>未来的我们</p>\n" + "<pre>" + modelDesc + "</pre>\n"
        if compititorDesc:
            desc += u"<p>与我们相似的产品</p>\n" + "<pre>" + compititorDesc + "</pre>\n"
        if otherDesc:
            desc += u"<p>其他</p>\n" + "<pre>" + otherDesc + "</pre>\n"
        if teamDesc:
            desc += u"<p>团队介绍</p>\n" + "<pre>" + teamDesc + "</pre>\n"
    else:
        desc = otherDesc
    '''

    return {
        "status":c["status"],
        "name": c["name"],
        "fullName": fullName,
        "description": desc,
        "productDesc": productDesc,
        "modelDesc": modelDesc,
        "operationDesc": operationDesc,
        "teamDesc": teamDesc,
        "marketDesc": marketDesc,
        "compititorDesc": compititorDesc,
        "advantageDesc": advantageDesc,
        "planDesc": planDesc,
        "otherDesc": otherDesc,
        "brief": c["brief"],
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
        "field": c.get("industry"),
        "subField": None,
        "tags": tags_str,
        "headCountMin": None,
        "headCountMax": None
    }

    #source_company_id = parser_util.insert_source_company(source_company)


def parse_artifact(source_company_id,item):
    logger.info("parse_artifact")
    company_key = item["key"]
    c = item["content"]["company_base"]["data"]["company"]
    artifacts = []
    # artifact
    website = c.get("website","").strip()
    website = url_helper.url_normalize(website)
    if website is not None and website != "":
        type, market, app_id = url_helper.get_market(website)
        if type == 4010:
            if website.find('36kr.com') > 0 and c["name"].find('36') == -1:
                pass
            else:
                artifact = {
                    "sourceCompanyId": source_company_id,
                    "name": c["name"],
                    "description": None,
                    "link": website,
                    "domain": app_id,
                    "type": type
                }
                artifacts.append(artifact)
        elif (type==4040 or type==4050) and app_id is not None:
            domain = get_android_domain(market, app_id)
            if (type==4040 or type==4050) and domain is not None:
                artifact = {
                    "sourceCompanyId": source_company_id,
                    "name": c["name"],
                    "description": None,
                    "link": website,
                    "domain": domain,
                    "type": type
                }
                artifacts.append(artifact)

    weibo = c.get("weibo","").strip()
    if weibo is not None and weibo != "":
        artifact = {
            "sourceCompanyId": source_company_id,
            "name": c["name"],
            "description": None,
            "link": weibo,
            "domain": None,
            "type": 4030
             }
        artifacts.append(artifact)

    weixin = c.get("weixin","").strip()
    if weixin is not None and weixin != "":
        artifact = {
            "sourceCompanyId": source_company_id,
            "name": c["name"],
            "description": None,
            "link": weixin,
            "domain": weixin,
            "type": 4020
        }
        artifacts.append(artifact)

    iphoneAppstoreLink = c.get("iphoneAppstoreLink","").strip()
    if iphoneAppstoreLink is not None and iphoneAppstoreLink != "":
        type, market, app_id = url_helper.get_market(iphoneAppstoreLink)
        domain = get_android_domain(market, app_id)
        if (type==4040 or type==4050) and domain is not None:
            artifact = {
                "sourceCompanyId": source_company_id,
                "name": c["name"],
                "description": None,
                "link": iphoneAppstoreLink,
                "domain": domain,
                "type": type
            }
            artifacts.append(artifact)

    ipadAppstoreLink = c.get("ipadAppstoreLink","").strip()
    if ipadAppstoreLink is not None and ipadAppstoreLink != "":
        type, market, app_id = url_helper.get_market(ipadAppstoreLink)
        domain = get_android_domain(market, app_id)
        if (type==4040 or type==4050) and domain is not None:
            artifact = {
                "sourceCompanyId": source_company_id,
                "name": c["name"],
                "description": None,
                "link": ipadAppstoreLink,
                "domain": domain,
                "type": type
            }
            artifacts.append(artifact)

    androidLink = c.get("androidLink","").strip()
    if androidLink is not None and androidLink != "":
        type, market, app_id = url_helper.get_market(androidLink)
        domain = get_android_domain(market, app_id)
        if (type==4040 or type==4050) and domain is not None:
            artifact = {
                "sourceCompanyId": source_company_id,
                "name": c["name"],
                "description": None,
                "link": androidLink,
                "domain": domain,
                "type": type
            }
            artifacts.append(artifact)

    return artifacts

def get_android_domain(app_market, app_id):
    domain = None
    if app_market == 16010 or app_market == 16020:
        android_app = parser_db_util.find_android_market(app_market, app_id)
        if android_app:
            domain = android_app["apkname"]
    else:
        domain = app_id
    return domain

def parseFinance_save(source_company_id,item, download_crawler):
    logger.info("parseFinance_save")
    if item is None:
        return None
    company_key = item["key"]

    # Check Investor if saved in investor databases (36003)
    flag = True
    if not item["content"].has_key("past_finance"):
        return True
    if not item["content"]["past_finance"]["data"].has_key("data"):
        return True

    finances = item["content"]["past_finance"]["data"]["data"]
    for finance in finances:
        logger.info("%s,%s,%s,%s" % (finance.get("phase"),finance.get("financeAmountUnit"),finance["financeDate"],finance.get("financeAmount")))

        roundStr = finance.get("phase")
        fundingRound = 0
        if roundStr == "INFORMAL" or roundStr=="ANGEL":
            fundingRound = 1011
            roundStr = "天使"
        elif roundStr == "PRE_A":
            fundingRound = 1020
            roundStr = "Pre-A"
        elif roundStr == "A":
            fundingRound = 1030
        elif roundStr == "A_PLUS":
            fundingRound = 1031
            roundStr = "A+"
        elif roundStr == "B":
            fundingRound = 1040
        elif roundStr == "B_PLUS":
            fundingRound = 1041
            roundStr = "B+"
        elif roundStr == "C":
            fundingRound = 1050
        elif roundStr == "D":
            fundingRound = 1060
        elif roundStr == "E":
            fundingRound = 1070
        elif roundStr == "ACQUIRED":
            fundingRound = 1120
        elif roundStr == "IPO":
            fundingRound = 1110
        elif roundStr == "NEEQ":
            fundingRound = 1105
        elif roundStr == "SEED":
            fundingRound = 1010



        d = time.localtime(finance["financeDate"]/1000)
        fundingDate = datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)
        fundingCurrency = 3010
        if finance.get("financeAmountUnit") == "USD":
            fundingCurrency = 3010
        elif finance.get("financeAmountUnit") == "CNY":
            fundingCurrency = 3020

        fundingInvestment = 0
        precise = 'Y'
        financeAmount = finance.get("financeAmount")
        if financeAmount != None:
            try:
                fundingInvestment = int(financeAmount) * 10000
            except:
                pass

            if fundingInvestment == 0:
                if financeAmount == u"数万":
                    fundingInvestment = 1*10000
                    precise = 'N'
                elif financeAmount == u"数十万":
                    fundingInvestment = 10*10000
                    precise = 'N'
                elif financeAmount == u"数百万":
                    fundingInvestment = 100*10000
                    precise = 'N'
                elif financeAmount == u"数千万":
                    fundingInvestment = 1000*10000
                    precise = 'N'
                elif financeAmount == u"数万万":
                    fundingInvestment = 10000*10000
                    precise = 'N'
                elif financeAmount == u"数亿":
                    fundingInvestment = 10000*10000
                    precise = 'N'
                elif financeAmount == u"数十亿":
                    fundingInvestment = 10000*10000*10
                    precise = 'N'

        source_funding = {
            "sourceCompanyId": source_company_id,
            "preMoney": None,
            "postMoney": None,
            "investment": fundingInvestment,
            "precise": precise,
            "round": fundingRound,
            "roundDesc": roundStr,
            "currency": fundingCurrency,
            "fundingDate": fundingDate
        }

        logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))

        source_investors = []

        investors = finance.get("participants")
        if investors is not None:
            for investor in investors:
                logger.info(investor.get("name"))
                entityId = investor.get("entityId")
                entityType = investor.get("entityType")
                if entityType == "ORGANIZATION":
                    item = parser_db_util.find_36kr(SOURCE,36003,str(entityId))
                    if item:
                        v = item["content"]["investor_base"]["data"]
                        if v["name"] == "":
                            v["name"] = v["nameAbbr"]
                        logo = v.get("logo")
                        if logo:
                            logo = logo.replace("https://","http://")
                        source_investor = {
                            "name": v["name"],
                            "website": v.get("website"),
                            "description": v["intro"],
                            "logo_url":logo,
                            "stage": None,
                            "field": None,
                            "type":10020,
                            "source":SOURCE,
                            "sourceId":str(entityId)
                        }
                        source_investors.append(source_investor)
                    else:
                        logger.info("No investor %s",str(entityId))
                        flag=False
                elif entityType == "COMPANY":
                    item = parser_db_util.find_36kr(SOURCE, 36001, str(entityId))
                    if item:
                        v = item["content"]["company_base"]["data"]["company"]
                        source_investor = {
                            "name": v["name"],
                            "website": v.get("website"),
                            "description": v["intro"],
                            "logo_url":v.get("logo"),
                            "stage": None,
                            "field": None,
                            "type":10020,
                            "source":SOURCE,
                            "sourceId":str(entityId)
                        }
                        source_investors.append(source_investor)
                    else:
                        logger.info("No company %s", str(entityId))
                        flag=False
                else:
                    logger.info("**********" + entityType + ", entityId=" + str(entityId))
        logger.info(json.dumps(source_investors, ensure_ascii=False, cls=util.CJsonEncoder))

        parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)

    return flag

type_map = {
    "FOUNDER":"创始人",
    "CO_FOUNDER":"联合创始人",
    "TECH":"技术",
    "DESIGN":"设计",
    "PRODUCT":"产品",
    "OPERATOR":"运营",
    "SALE":"市场与销售",
    "HR":"行政、人事及财务",
    "INVEST":"投资和并购",
}

def parseMember_save(source_company_id, type, members, download_crawler):
    logger.info("parseMember_save")
    for m in members:
        if not m.has_key("name"):
            continue

        logger.info(m["name"])

        desc = m.get("intro")
        member_type = type_map.get(m.get("type"),"")
        position = m.get("position","")
        if len(position) > 20:
            if desc is None:
                desc = position
            else:
                desc += '\n' + position
            position = member_type
        else:
            position = member_type + position

        logo = m.get("avatar")
        if logo:
            logo = logo.replace("https://","http://")
        source_member = {
            "source": SOURCE,
            "sourceId": str(m["id"]),
            "name": m["name"],
            "photo_url": logo,
            "weibo": None,
            "location": 0,
            "role": None,
            "description": desc,
            "education": None,
            "work": None
        }

        source_company_member_rel = {
            "sourceCompanyId": source_company_id,
            "position": position,
            "joinDate": None,
            "leaveDate": None,
            "type": type
        }
        try:
            parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
        except:
            pass




if __name__ == "__main__":
    while True:
        process()
        #break   #test
        time.sleep(30*60)