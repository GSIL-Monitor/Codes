# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
from kr36_location import kr36_cities


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("36kr_company_parser_2", stream=True)
logger = loghelper.get_logger("36kr_company_parser_2")

SOURCE = 13022  #36kr
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
        # items = [parser_db_util.find_process_one(SOURCE,TYPE,83700389)]
        for item in items:
            try:
                r = parse_company(item)
                logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

                source_company_id = parser_db_util.save_company_standard(r, download_crawler)
                parser_db_util.delete_source_company_name(source_company_id)
                parser_db_util.delete_source_mainbeianhao(source_company_id)
                parser_db_util.save_source_company_name(source_company_id, r["name"],12020)
                if r["fullName"] is not None:
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

                parseMember_save(source_company_id, item, download_crawler)
                #
                parser_db_util.delete_funding(source_company_id)
                flag=parseFinance_save(source_company_id,item, download_crawler)
                flag = True
            except Exception, E:
                logger.info(E)
                pass
            # if flag:
            parser_db_util.update_processed(item["_id"])
            logger.info("processed %s" ,item["url"])
            # else:
            #     logger.info("lack something:  %s", item["url"])

            #break
        #break
        if len(items) == 0:
            break

    logger.info("36kr_company_parser end.")


def parse_company(item):
    logger.info("parse_company")
    company_key = item["key"]

    #company basic info
    c = item["content"]["company_base"]["data"]
    #check if page is under development or is completed(CREATED)
    # if c["status"] == "INIT":
    #     return {
    #         "status":c["status"],
    #     }

    tags = item["content"]["company_base"]["data"]["industryTag"]
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

    if c.has_key("companyIntroduce"):
        if c["companyIntroduce"]["productService"] is not None and c["companyIntroduce"]["productService"].strip() != "": # productService
            productDesc = c["companyIntroduce"]["productService"]
        if c["companyIntroduce"]["userMarket"] is not None and c["companyIntroduce"]["userMarket"].strip() != "":
            marketDesc =  c["companyIntroduce"]["userMarket"]
    # if c.has_key("dataLights"): # 我们的用户
    #     operationDesc = c["dataLights"].strip()
    # if c.has_key("projectPlan"): # 未来的我们
    #     modelDesc = c["projectPlan"].strip()
    # if c.has_key("competitor"): # 与我们相似的产品
    #     compititorDesc = c["competitor"].strip()
    if c.has_key("intro"):  # 其他
        # otherDesc = c["intro"].strip()
        desc = c["intro"].strip()
    # if c.has_key("story"): # 团队介绍
    #     teamDesc = c["story"].strip()

    headCount = c["scale"].replace("人", "")
    min_staff = None
    max_staff = None
    if headCount.strip() != "":
        if headCount == "少于15":
            min_staff = 1
            max_staff = 15
        else:
            staffarr = headCount.split('-')
            if len(staffarr) > 1:
                try:
                    min_staff = int(staffarr[0])
                    max_staff = int(staffarr[1])
                except: pass
            else:
                try:
                    min_staff = int(staffarr[0].strip())
                    max_staff = None
                except: pass

    return {
        "name": c["name"],
        "fullName": fullName if fullName is not None and fullName.strip() != "" else None,
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
        "round": None,
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
        "headCountMin": min_staff,
        "headCountMax": max_staff
    }

    #source_company_id = parser_util.insert_source_company(source_company)


def parse_artifact(source_company_id,item):
    logger.info("parse_artifact")
    company_key = item["key"]
    cc = item["content"]["company_base"]["data"]
    cp = item["content"]["product"]["data"]["companyProduct"]
    artifacts = []
    links = []
    # artifact
    for c in [cc, cp]:
        website = c.get("website","").strip()
        website = url_helper.url_normalize(website)
        if website is not None and website != "" and website not in links:
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
                    links.append(website)
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
                    links.append(website)

        weibo = c.get("weibo","").strip()
        if weibo is not None and weibo != "" and weibo.find("weibo")>=0 and weibo not in links:
            artifact = {
                "sourceCompanyId": source_company_id,
                "name": c["name"],
                "description": None,
                "link": weibo,
                "domain": None,
                "type": 4030
                 }
            artifacts.append(artifact)
            links.append(weibo)

        weixin = c.get("weixin","").strip()
        if weixin is not None and weixin != "" and weixin not in links:
            artifact = {
                "sourceCompanyId": source_company_id,
                "name": c["name"],
                "description": None,
                "link": weixin,
                "domain": weixin,
                "type": 4020
            }
            artifacts.append(artifact)
            links.append(weixin)

        iphoneAppstoreLink = c.get("ios","").strip()
        if iphoneAppstoreLink is not None and iphoneAppstoreLink != ""  and iphoneAppstoreLink not in links:
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
                links.append(iphoneAppstoreLink)

        # ipadAppstoreLink = c.get("ipadAppstoreLink","").strip()
        # if ipadAppstoreLink is not None and ipadAppstoreLink != "":
        #     type, market, app_id = url_helper.get_market(ipadAppstoreLink)
        #     domain = get_android_domain(market, app_id)
        #     if (type==4040 or type==4050) and domain is not None:
        #         artifact = {
        #             "sourceCompanyId": source_company_id,
        #             "name": c["name"],
        #             "description": None,
        #             "link": ipadAppstoreLink,
        #             "domain": domain,
        #             "type": type
        #         }
        #         artifacts.append(artifact)

        androidLink = c.get("android","").strip()
        if androidLink is not None and androidLink != ""  and androidLink not in links:
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
                links.append(androidLink)

    return artifacts

def get_company_code(name):
    conn = db.connect_torndb()
    if len(name) <8 :
        pinyin = lazy_pinyin(name.decode('utf-8'))
        company_code = ''.join(pinyin)
    else:
        pinyin = lazy_pinyin(name.decode('utf-8'), style=pypinyin.INITIALS)
        company_code = ''.join(pinyin)

    bs = bytes(company_code)
    st = ''
    for b in bs:
        if re.match('-|[0-9a-zA-Z]', b):
            st +=b
    company_code = st

    if len(company_code) >31:
        company_code = company_code[0:30]

    if len(company_code) < 3:
        company_code = company_code+str(random.randint(1, 100))


    conn.close()
    return company_code

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
    if not item["content"]["past_finance"].has_key("data"):
        return True

    finances = item["content"]["past_finance"]["data"]
    for finance in finances:
        if finance.has_key("financeDate") is False:
            continue
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
        financeAmount = finance.get("financeAmount").replace(",","")
        if financeAmount != None:
            try:
                logger.info("here, %s, %s", financeAmount, type(financeAmount))
                # if financeAmount.find("亿")>=0:
                #     logger.info("find")

                if re.match(u"(\d+)(\.0)?(亿|万)", financeAmount):
                    logger.info("hhhhhhhhhhhh %s", financeAmount)
                    fundingInvestment = int(financeAmount.replace("亿","").replace("万","").replace(".0","").replace(",","")) * 10000

                    if financeAmount.find("亿") >= 0:
                        logger.info("here")
                        fundingInvestment = fundingInvestment * 10000
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
                elif financeAmount.find("千万级")>=0:
                    fundingInvestment = 100*10000
                    precise = 'N'
                elif financeAmount.find("亿元级以上")>=0:
                    fundingInvestment = 10000 * 10000
                    precise = 'N'
                elif financeAmount.find("亿元级")>=0:
                    fundingInvestment = 1000* 10000
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
            "fundingDate": fundingDate,
            "newsUrl": finance.get("newsUrl",None)
        }

        # logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info("%s, %s, %s, %s", roundStr,financeAmount, fundingRound, fundingInvestment)

        source_investors = []

        investors = finance.get("participantVos")
        if investors is not None:
            for investor in investors:
                logger.info(investor.get("entityName"))
                entityId = investor.get("entityId")
                entityType = investor.get("entityType")
                if entityType is not None:
                # if entityType == "ORGANIZATION":
                #     item = parser_db_util.find_36kr(SOURCE,36003,str(entityId))
                #     if item:
                #         v = item["content"]["investor_base"]["data"]
                #         if v["name"] == "":
                #             v["name"] = v["nameAbbr"]
                #         logo = v.get("logo")
                #         if logo:
                #             logo = logo.replace("https://","http://")
                #         source_investor = {
                #             "name": v["name"],
                #             "website": v.get("website"),
                #             "description": v["intro"],
                #             "logo_url":logo,
                #             "stage": None,
                #             "field": None,
                #             "type":10020,
                #             "source":SOURCE,
                #             "sourceId":str(entityId)
                #         }
                #         source_investors.append(source_investor)
                #     else:
                #         logger.info("No investor %s",str(entityId))
                #         flag=False
                # elif entityType == "COMPANY":
                #     item = parser_db_util.find_36kr(SOURCE, 36001, str(entityId))
                #     if item:
                #         v = item["content"]["company_base"]["data"]["company"]
                    if entityType == 2:
                        sourceId = str(entityId)
                        if entityId == 0:
                            sourceId = str(entityId)+'_'+get_company_code(investor["entityName"])
                    else:
                        sourceId = str(entityType)+'_'+str(entityId)
                        if entityId == 0:
                            sourceId = str(entityType) + '_' + str(entityId)+'_'+get_company_code(investor["entityName"])
                    source_investor = {
                        "name": investor["entityName"],
                        "website": None,
                        "description": None,
                        "logo_url":None,
                        "stage": None,
                        "field": None,
                        "type":10020,
                        "source":SOURCE,
                        "sourceId":sourceId
                    }
                    source_investors.append(source_investor)
                #     else:
                #         logger.info("No company %s", str(entityId))
                #         flag=False
                # else:
                #     logger.info("**********" + entityType + ", entityId=" + str(entityId))
        logger.info(json.dumps(source_investors, ensure_ascii=False, cls=util.CJsonEncoder))
        try:
            parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)
        except:
            pass

    return flag


def parseMember_save(source_company_id, item, download_crawler):
    logger.info("parseMember_save")
    members = item["content"]["member"]["data"]["members"]
    for m in members:
        if not m.has_key("name"):
            continue

        logger.info(m["name"])

        desc = m.get("intro")
        position = m.get("position","")


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
            "role": position,
            "description": desc,
            "education": None,
            "work": None
        }
        ptype = name_helper.position_check(position)

        source_company_member_rel = {
            "sourceCompanyId": source_company_id,
            "position": position,
            "joinDate": None,
            "leaveDate": None,
            "type": ptype
        }
        try:
            parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
            # logger.info(source_member)
            # logger.info(source_company_member_rel)
        except:
            pass




if __name__ == "__main__":
    while True:
        process()
        #break   #test
        time.sleep(60)