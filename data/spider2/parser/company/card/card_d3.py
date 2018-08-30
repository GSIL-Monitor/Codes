# -*- coding: utf-8 -*-
import os, sys, re
import time
import datetime
from bson.objectid import ObjectId
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import random
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("card_d3", stream=True)
logger = loghelper.get_logger("card_d3")

download_crawler = download.DownloadCrawler(use_proxy=True)
SOURCE = 13121
#parse data from qimingpian directly, bamy called it step 1 to checkout company



def parse_company(item):
    logger.info("parse_company")
    company_key = item["postdata"]["id"]

    #company basic info
    c = item["data"]["basic"]

    tags = c["tags"]

    tags_str = tags.replace("|",",")

    logo=c["icon"]
    if logo.find("product_default.png") >= 0:
        logo = None

    establish_date = None
    if c.has_key("open_time"):
        try:
            establish_date = datetime.datetime.strptime(c["open_time"], "%Y-%m-%d")
        except:
            pass

    address1 = None
    address2 = None
    if c.has_key("city"):
        address2 = c["city"]
    if c.has_key("province"):
        address1 = c["province"]

    location_id = 0
    if address2!=None and address2.strip()!="":
        location = parser_db_util.get_location(address2)
        if location != None:
            location_id= location["locationId"]

    if location_id==0 and address1 != None and address1.strip()!="":
        location = parser_db_util.get_location(address1)
        if location != None:
            location_id = location["locationId"]

    fullName = c["company"]
    if fullName is None or fullName.strip() == "":
        fullName = None
    else:
        fullName = fullName.replace("_","")
        idx = fullName.rfind(u"公司")
        if idx != -1:
            fullName = fullName[:(idx+len(u"公司"))]
        fullName = name_helper.company_name_normalize(fullName)

    name = c["product"]
    desc = ""
    brief = ""
    productDesc = None
    modelDesc = None
    operationDesc = None
    teamDesc = None
    marketDesc = None
    compititorDesc = None
    advantageDesc = None
    planDesc = None
    otherDesc = None


    if c.has_key("desc"):  # 其他
        # otherDesc = c["intro"].strip()
        desc = c["desc"].strip()

    if c.has_key("yewu"):  # 其他
        # otherDesc = c["intro"].strip()
        brief = c["yewu"].strip()

    if name is None or fullName is None:
        return {
            "status": "No_Name",
        }

    artifacts = []
    websites = []
    if c.has_key("gw_link") is True and c["gw_link"].strip() !="" and c["gw_link"] not in websites:
        websites.append(c["gw_link"])
    if c.has_key("source_gw_link") is True and c["source_gw_link"].strip() != "" and c["source_gw_link"] not in websites:
        websites.append(c["source_gw_link"])
    if item["data"].has_key("productinfos") is True:
        for pi in item["data"]["productinfos"]:
            if pi.has_key("link") is True and pi["link"].strip() !="" and pi["link"] not in websites:
                websites.append(pi["link"])

    for website in websites:
        type, app_market, app_id = url_helper.get_market(website)
        if type == 4010:
            if item["url"] != website and website.find("qimingpian.com") == -1:
                flag, domain = url_helper.get_domain(website)
                if flag is not None:
                    if flag is False:
                        domain = None
                    artifacts.append({
                        "type": 4010,
                        "name": name,
                        "description": brief,
                        "link": website,
                        "domain": domain
                    })
        elif type == 4020 or type == 4030:
            domain = None
            if domain is not None:
                artifacts.append({
                    "type": type,
                    "name": name,
                    "description": brief,
                    "link": website,
                    "domain": domain
                })
        elif type == 4040:
            domain = app_id
            if domain is not None:
                artifacts.append({
                    "type": 4040,
                    "name": name,
                    "description": brief,
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
                    "description": brief,
                    "link": website,
                    "domain": domain
                })

    return {
        "name": name,
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
        "brief": brief,
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
        "artifacts": artifacts,

    }

def getMoney(moneyStr):
    investment = 0
    currency = 3020
    precise = 'Y'

    investmentStr = ""

    if investment == 0:
        result = util.re_get_result(u'(数.*?)万人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000
            elif investmentStr == u"数十":
                investment = 10*10000
            elif investmentStr == u"数百":
                investment = 100*10000
            elif investmentStr == u"数千":
                investment = 1000*10000

    if investment == 0:
        result = util.re_get_result(u'(数.*?)亿人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000*10000
            elif investmentStr == u"数十":
                investment = 10*10000*10000
            elif investmentStr == u"数百":
                investment = 100*10000*10000
            elif investmentStr == u"数千":
                investment = 1000*10000*10000

    if investment == 0:
        result = util.re_get_result(u'(\d*\.?\d*?)万人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(float(investmentStr) * 10000)
        else:
            result = util.re_get_result(u'(\d*\.?\d*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(float(investmentStr) * 10000)

    if investment == 0:
        result = util.re_get_result(u'(\d*\.?\d*?)亿人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(float(investmentStr) * 100000000)
        else:
            result = util.re_get_result(u'(\d*\.?\d*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(float(investmentStr) * 100000000)

    if investment == 0:
        result = util.re_get_result(u'亿元及以上美元',moneyStr)
        if result != None:
            currency = 3020
            investment = 100000000
            precise = 'N'
        else:
            result = util.re_get_result(u'亿元及以上人民币',moneyStr)
            if result != None:
                currency = 3010
                investment = 100000000
                precise = 'N'

    return currency, investment, precise


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

def parseFinance_save(source_company_id,item, download_crawler):
    logger.info("parseFinance_save")
    if item is None:
        return None
    # company_key = item["key"]

    # Check Investor if saved in investor databases (36003)
    flag = True
    if not item["data"].has_key("basic"):
        return True
    if not item["data"]["basic"].has_key("rongzi"):
        return True

    finances = item["data"]["basic"]["rongzi"]
    for finance in finances:
        if finance.has_key("pl_time") is False:
            continue
        logger.info("%s,%s,%s,%s" % (finance.get("lunci"),finance.get("money"),finance["pl_time"],finance.get("tzr_all")))

        roundStr = finance.get("lunci")
        fundingRound = 0
        if roundStr.startswith("尚未获投"):
            fundingRound = 1000
            roundStr = "尚未获投"
        elif roundStr.startswith("种子"):
            fundingRound = 1010
            roundStr = "天使轮"
        elif roundStr.startswith("天使"):
            fundingRound = 1011
            roundStr = "天使轮"
        elif roundStr.startswith("Pre-A"):
            fundingRound = 1020
            roundStr = "Pre-A轮"
        elif roundStr.startswith("A+"):
            fundingRound = 1031
            roundStr = "A+轮"
        elif roundStr.startswith("A"):
            fundingRound = 1030
            roundStr = "A轮"
        elif roundStr.startswith("Pre-B"):
            fundingRound = 1039
            roundStr = "Pre-B轮"
        elif roundStr.startswith("B+"):
            fundingRound = 1041
            roundStr = "B+轮"
        elif roundStr.startswith("B"):
            fundingRound = 1040
            roundStr = "B轮"
        elif roundStr.startswith("C+"):
            fundingRound = 1051
            roundStr = "C轮"
        elif roundStr.startswith("C"):
            fundingRound = 1050
            roundStr = "C轮"
        elif roundStr.startswith("D"):
            fundingRound = 1060
            roundStr = "D轮"
        elif roundStr.startswith("E"):
            fundingRound = 1070
            roundStr = "E轮"
        elif roundStr.startswith("F"):
            fundingRound = 1080
            roundStr = "F轮"
        elif roundStr.startswith("Pre-IPO"):
            fundingRound = 1080
            roundStr = "Pre-IPO"
        elif roundStr.startswith("新三板"):
            fundingRound = 1105
            roundStr = "新三板"
        elif roundStr.startswith("定向增发"):
            fundingRound = 1106
            roundStr = "新三板定增"
        elif (roundStr.startswith("IPO") or roundStr.startswith("已上市")) and roundStr.find("IPO上市后") == -1:
            fundingRound = 1110
            roundStr = "上市"
        elif roundStr.startswith("已被收购") or roundStr.startswith("并购"):
            fundingRound = 1120
            roundStr = "并购"
        elif roundStr.startswith("战略投资") or roundStr.startswith("战略融资") or roundStr.startswith("IPO上市后"):
            fundingRound = 1130
            roundStr = "战略投资"
        elif roundStr.startswith("私有化"):
            fundingRound = 1140
            roundStr = "私有化"
        elif roundStr.startswith("债权融资"):
            fundingRound = 1150
            roundStr = "债权融资"
        elif roundStr.startswith("股权转让"):
            fundingRound = 1160
            roundStr = "股权转让"


        # d = time.localtime(finance["financeDate"]/1000)
        # fundingDate = datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)

        try:
            fundingDate = datetime.datetime.strptime(finance["pl_time"], "%Y.%m.%d")
        except:
            fundingDate = None
        (currency, investment, precise) = getMoney(finance.get("money"))


        source_funding = {
            "sourceCompanyId": source_company_id,
            "preMoney": None,
            "postMoney": None,
            "investment": investment,
            "precise": precise,
            "round": fundingRound,
            "roundDesc": roundStr,
            "currency": currency,
            "fundingDate": fundingDate,
            "newsUrl": finance.get("newsUrl",None)
        }

        # logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info("%s, %s, %s, %s", roundStr,finance.get("money"), fundingRound, investment)

        source_investors = []

        if finance.get("tzr_all") is not None and finance["tzr_all"].strip() != "":
            if finance["tzr_all"].find("公开发行")>=0: pass
            else:
                for investor in finance["tzr_all"].split("|"):
                    logger.info(investor)

                    source_investor = {
                        "name": investor,
                        "website": None,
                        "description": None,
                        "logo_url":None,
                        "stage": None,
                        "field": None,
                        "type":10020,
                        "source":SOURCE,
                        "sourceId":get_company_code(investor)
                    }
                    source_investors.append(source_investor)
        logger.info("here")
        logger.info(json.dumps(source_investors, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info("hereover")
        # try:
        #     parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)
        # except Exception, E:
        #     logger.info(E)
        #     pass
        parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)

    return flag

if __name__ == '__main__':
    logger.info("card d3 Begin...")
    # noo = 0
    while True:
        (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection = mongo.raw.qmp

        while True:
            # items = list(collection.find({"_id" : ObjectId("5ad7ef121045403178ed4135")}).limit(100))
            items = list(collection.find({"url":"http://vip.api.qimingpian.com/d/c3", "processed":None},
                                         {"data.basic":1,"postdata":1,"productinfos":1,"url":1}))
            logger.info("items : %s", len(items))
            for item in items:
                # if item.has_key("processed") and item["processed"] is True:
                #     continue
                try:
                    logger.info(item)
                    r = parse_company(item)
                    # logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))
                    for i in r:
                        logger.info("%s - %s",i,r[i])
                    source_company_id = parser_db_util.save_company_standard(r, download_crawler)
                    parser_db_util.delete_source_company_name(source_company_id)
                    parser_db_util.delete_source_mainbeianhao(source_company_id)
                    parser_db_util.save_source_company_name(source_company_id, r["name"], 12020)
                    parser_db_util.save_source_company_name(source_company_id, r["fullName"], 12010)
                    main_company_name = name_helper.get_main_company_name(r["fullName"])
                    if main_company_name != r["fullName"]:
                        parser_db_util.save_source_company_name(source_company_id, main_company_name, 12010)
                    logger.info("source_company_id=%s", source_company_id)

                    artifacts = []
                    artifacts.extend(r["artifacts"])
                    logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))


                    parser_db_util.save_artifacts_standard(source_company_id, artifacts)
                    #
                    # #
                    parser_db_util.delete_funding(source_company_id)
                    flag = parseFinance_save(source_company_id, item, download_crawler)
                    # flag = True
                except Exception,E:
                    logger.info(E)
                    pass
                # if flag:
                # parser_db_util.update_processed(item["_id"])
                collection.update({"_id": item["_id"]}, {"$set": {"processed": True}})
                logger.info("processed %s", item["url"])

            break

        # break
        # logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
        mongo.close()
        conn.close()
        # time.sleep(10*60)
        break
