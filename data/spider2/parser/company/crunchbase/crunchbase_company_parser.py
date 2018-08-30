# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))

import name_helper,loghelper,util , url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util2'))
import parser_mongo_util
#logger
loghelper.init_logger("crunchbase_company_parser", stream=True)
logger = loghelper.get_logger("crunchbase_company_parser")

SOURCE = 13130  #crunchbase
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


# todo 聚合拓展 processed = 0 parser_db_util.py save_company
# has_key ==> dict.get()

def process():
    logger.info('crunchbase_company_parser begin ...')
    start = 0
    while True:
        items =  parser_db_util.find_process_limit(SOURCE,TYPE,0,500)
        # mongo = db.connect_mongo()
        # collection = mongo.raw.projectdata
        # items = list(collection.find({"_id" : ObjectId("5b02a14fdeb4717184810e22")}))
        for item in items:
            if item is None:
                continue
            try:
                r = parse_company(item)
                logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder,indent=2))
                # source_company (2010 running)
                source_company_id = parser_db_util.save_company_standard(r, download_crawler)
                logger.info('%s:%s'%(item['name'],source_company_id))
                parser_db_util.delete_source_company_name(source_company_id)
                parser_db_util.delete_source_mainbeianhao(source_company_id)
                # source_company_name (12020 shortname)
                parser_db_util.save_source_company_name(source_company_id, r["name"], 12020)

                artifacts=parse_artifact(source_company_id,item)
                logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder,indent=2))

                if (r["fullName"] is None or r["fullName"].strip() == "") and (r['description'] is None or r['description'].strip() == "") \
                    and len(artifacts) == 0:
                    parser_db_util.update_active(SOURCE, item["key"], 'N')
                    parser_db_util.update_processed(item["_id"])
                    logger.info("missing all stuff, processed %s", item["url"])
                    continue

                # source_artifact (4010 website)
                parser_db_util.save_artifacts_standard(source_company_id, artifacts)

                # source_member and source_company_member_rel(5010 ceo)
                parseMember_save(source_company_id, item, download_crawler)

                parser_db_util.delete_funding(source_company_id)
                # source_funding and source_funding_investor_rel (10020 vc)
                parseFinance_save(source_company_id,item , download_crawler)

            except Exception,E:
                logger.info(E)
                pass

            parser_db_util.update_processed(item["_id"])
            logger.info("processed %s"%item["url"])
        # break
        if len(items) == 0:
            break
        logger.info('parser end.')
        return

def parse_company(item):
    name = item['name']
    logger.info('parse_company:%s'%name)

    c = item['content']['company_base']
    company_key = item['key']

    tags_str = None
    tags = c['tags']
    tagss = []
    if tags:
        for tag in tags:
            tagss.append(tag['value'])
    tags_str = ','.join(tagss)
    # logger.info('tags：%s'%tags_str)

    logo = c['logo']
    if logo:
        logo = "https://crunchbase-production-res.cloudinary.com/image/upload/c_lpad,h_100,w_100,f_auto,b_white,q_auto:eco/%s"%logo
    # logger.info('logo：%s'%logo)

    establish_date = None
    if c['overview_fields'].has_key('founded_on'):
        establish_date = c['overview_fields']['founded_on']['value']
        if establish_date:
            es = establish_date.split('-')
            int_es = map(int,es)
            if int_es[0] > 1980:
                establish_date = datetime.datetime(int_es[0],int_es[1],int_es[2])
            else:
                establish_date = None
    # logger.info('establish_date：%s'%establish_date)

    locaotions_str = None
    locationss = []
    if c['locations'].has_key('location_identifiers'):
        locations = c['locations']['location_identifiers']
        if locations:
            for locat in locations:
                locationss.append(locat['value'])
    locaotions_str = ','.join(locationss)
    # logger.info('locaotions_str：%s'%locaotions_str)

    location_id = 421
    contry = '国外'
    if locaotions_str.lower().find('china') >=0:
        contry = '中国'
    location = parser_db_util.get_location(contry)
    if location != None:
        location_id = location["locationId"]
    # logger.info('location_id：%s'%location_id)

    brief = None
    if c['locations'].has_key('short_description'):
        brief = c['locations']['short_description']
    # logger.info('brief:%s'%brief)

    desc = ""
    descriptions = c['description']
    if descriptions.has_key('description'):
        desc = descriptions['description']

    fullName = None
    productDesc = None
    modelDesc = None
    operationDesc = None
    teamDesc = None
    marketDesc = None
    compititorDesc = None
    advantageDesc = None
    planDesc = None
    otherDesc = None
    headCountMin = None
    headCountMax = None
    return {
        "name": name,
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
        "headCountMin": headCountMin,
        "headCountMax": headCountMax
    }

def parse_artifact(source_company_id,item):
    name = item['name']
    logger.info('parse_artifact:%s'%name)

    artifacts = []
    desc = ''
    descs = item['content']['company_base']['properties']
    if descs.has_key('short_description'):
        desc = descs['short_description']

    of = item['content']['company_base']['overview_fields2']
    if of.has_key('website'):
        website = of['website']['value']
        website = url_helper.url_normalize(website)
        # logger.info('website：%s'%website)
        if website is not None and website.find('twitter')==-1 and website.find('linkedin')==-1 and website.find('facebook')==-1:
            type, app_market, app_id = url_helper.get_market(website)
            # logger.info('type:%s---market:%s---app_id:%s'%(type,market,app_id))
            if type == 4010:
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
            elif type == 4020 or type == 4030:
                domain = None
                if domain is not None:
                    artifacts.append({
                        "type": type,
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
                    android_app = parser_mongo_util.find_android_market(app_market, app_id)
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

def parseMember_save(source_company_id, item, download_crawler):
    name = item['name']
    logger.info('parseMember_save:%s'%name)
    members = item['content']['member']['current_employees']

    for m in members:
        # logger.info('*******%s'%m)
        person = m.get('person_identifier','')
        name = person.get('value','')
        # logger.info('name:%s', name)
        uuid = person.get('uuid','')
        desc = None
        position = m.get('title','')
        # logger.info('position:%s', position)
        logo = person.get('image_id','')
        if logo:
            logo = 'https://crunchbase-production-res.cloudinary.com/image/upload/c_thumb,h_200,w_200,f_auto,g_faces,z_0.7,b_white,q_auto:eco/%s'%logo
        # logger.info('logo:%s', logo)
        source_member = {
            "source": SOURCE,
            "sourceId": uuid,
            "name": name,
            "photo_url":logo,
            "weibo": None,
            "location": 0,
            "role": position,
            "description":desc,
            "education": None,
            "work": None
        }
        ptype = name_helper.crunchbase_position_check(position)
        # logger.info('ptype:%s',ptype)

        source_company_member_rel = {
            "sourceCompanyId": source_company_id,
            "position": position,
            "joinDate": None,
            "leaveDate": None,
            "type": ptype
        }
        logger.info(json.dumps(source_member,ensure_ascii=False,indent=2))
        logger.info(json.dumps(source_company_member_rel,ensure_ascii=False,indent=2))


        try:
            parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
        except:
            pass

def parseFinance_save(source_company_id,item,download_crawler):
    name = item['name']
    logger.info("parseFinance_save:%s"%name)

    def funding_round(roundStr):
        fundingRound = 0
        # if isinstance(roundStr,bool):
        #     roundStr = 'IPO'
        roundStr = roundStr.lower()
        if roundStr.find('seed round') != -1:
            fundingRound = 1010
            roundStr = "SEED"
        elif roundStr.find('angel round') != -1:
            fundingRound = 1011
            roundStr = "天使"
        elif roundStr.find('series a') != -1:
            fundingRound = 1030
            roundStr = 'A'
        elif roundStr.find('series b') != -1:
            fundingRound = 1040
            roundStr = 'B'
        elif roundStr.find('series c') != -1:
            fundingRound = 1050
            roundStr = 'C'
        elif roundStr.find('series d') != -1:
            fundingRound = 1060
            roundStr = 'D'
        elif roundStr.find('series e') != -1:
            fundingRound = 1070
            roundStr = 'E'
        elif roundStr.find('series f') != -1:
            fundingRound = 1080
            roundStr = 'F'
        elif roundStr.find('series g') != -1 or roundStr.find('series h') != -1:
            fundingRound = 1090
            roundStr = 'Late Stage'
        elif roundStr.find('initial coin offering') != -1:
            fundingRound = 1109
            roundStr = 'ICO'
        elif roundStr.find('post-ipo equity') != -1 or roundStr.find('post-ipo debt')!= -1 or roundStr.find('post-ipo')!= -1:
            fundingRound = 1111
            roundStr = 'Post-IPO'
        elif roundStr.find('corporate round') != -1 or roundStr.find('private equity round') != -1:
            fundingRound = 1130
            roundStr = '战略投资'
        elif roundStr.find('debt financing') != -1 or roundStr.find('convertible note') != -1:
            fundingRound = 1150
            roundStr = '债权融资'
        elif roundStr.find('grant') != -1:
            fundingRound = 1170
            roundStr = 'Grant Funding'
        elif roundStr.find('venture round') != -1 or roundStr.find('funding round') != -1:
            fundingRound = 0
            roundStr = 'UNKNOWN'
        elif roundStr.find('equity crowdfunding') != -1 or roundStr.find('product crowdfunding') != -1 :
            fundingRound = 1009
            roundStr = '众筹'
        elif roundStr.find('acquired by') != -1:
            fundingRound = 1120
            roundStr = 'Acquired'
        elif roundStr == 'ipo':
            fundingRound = 1110
            roundStr = 'IPO'
        else:
            fundingRound = 0
            roundStr = 'UNKNOWN'
        return fundingRound, roundStr

    def get_fundingDate(financeDate):
        if financeDate:
            lis = financeDate.strip().split('-')
            datelis = map(int, lis)
            if len(datelis) == 3:
                fundingDate = datetime.datetime(datelis[0], datelis[1], datelis[2])
                return fundingDate

    def get_fundingCurrency(financeAmountUnit):
        fundingCurrency = 3010
        if financeAmountUnit == 'CNY':
            fundingCurrency = 3020
        elif financeAmountUnit == 'SGD':
            fundingCurrency = 3030
        elif financeAmountUnit == 'EUR':
            fundingCurrency = 3040
        elif financeAmountUnit == 'GBP':
            fundingCurrency = 3050
        elif financeAmountUnit == 'JPY':
            fundingCurrency = 3060
        elif financeAmountUnit == 'HKD':
            fundingCurrency = 3070
        elif financeAmountUnit == 'AUD':
            fundingCurrency = 3080
        elif financeAmountUnit == 'INR':
            fundingCurrency = 3090
        elif financeAmountUnit == 'BRL':
            fundingCurrency = 3100
        return fundingCurrency


    def get_source_investors(uuid,flag):
        source_investors = []
        if flag == 'finance':
            investors = item['content']['past_finance']['investors']
            if investors is not None:
                for investor in investors:
                    if investor['funding_round_identifier']['uuid'] == uuid:
                        iname = investor['investor_identifier']['value']
                        sourceId = investor['investor_identifier']['uuid']
                        source_investor = {
                            "name": iname,
                            "website": None,
                            "description": None,
                            "logo_url": None,
                            "stage": None,
                            "field": None,
                            "type": 10020,
                            "source": SOURCE,
                            "sourceId": sourceId
                        }
                        source_investors.append(source_investor)
        elif flag == 'acquired':
            investorss = item['content']['past_finance']['acquired_by_fields']
            if investorss.has_key('acquirer_identifier'):
                if uuid == 1:
                    iname = investorss['acquirer_identifier']['value']
                    sourceId = investorss['acquirer_identifier']['uuid']
                    source_investor = {
                        "name": iname,
                        "website": None,
                        "description": None,
                        "logo_url": None,
                        "stage": None,
                        "field": None,
                        "type": 10020,
                        "source": SOURCE,
                        "sourceId": sourceId
                    }
                    source_investors.append(source_investor)
        return source_investors

    def save(fundingRound,roundStr,fundingCurrency,fundingDate,financeAmount,precise,newsUrl,source_investors=None):
        source_funding = {
            "sourceCompanyId": source_company_id,
            "preMoney": None,
            "postMoney": None,
            "investment": financeAmount,
            "precise": precise,
            "round": fundingRound,
            "roundDesc": roundStr,
            "currency": fundingCurrency,
            "fundingDate": fundingDate,
            "newsUrl": newsUrl
        }
        logger.info("%s, %s, %s, %s", roundStr,fundingRound,financeAmount , fundingCurrency)
        logger.info(json.dumps(source_investors, ensure_ascii=False, cls=util.CJsonEncoder,indent=2))

        try:
            parser_db_util.save_funding_standard_crunchbase(source_funding, download_crawler, source_investors)
        except:
            pass
    if item["content"]["past_finance"].has_key("acquired_by_fields") is True:
        acquired = item['content']['past_finance']['acquired_by_fields']
    else:
        acquired = item['content']["company_base"]['acquired_by_fields']
    if acquired.has_key('acquisition_identifier'):
        acquiredStr = acquired['acquisition_identifier']['value']
        fundingRound = None; roundStr = None; fundingCurrency = None
        fundingDate = None; financeAmount = None; newsUrl = None; precise = 'Y'
        if acquiredStr:
            fundingRound, roundStr = funding_round(acquiredStr)
            # logger.info('roundStr:%s',roundStr)

        if acquired.has_key('acquisition_announced_on'):
            acquiredDate = acquired['acquisition_announced_on']['value']
            fundingDate = get_fundingDate(acquiredDate) #date type
            # logger.info('fundingDate:%s',fundingDate)

        if acquired.has_key('acquisition_price'):
            financeAmountUnit = acquired['acquisition_price']['currency']
            fundingCurrency = get_fundingCurrency(financeAmountUnit)
            financeAmount = acquired['acquisition_price']['value_usd']
            if fundingCurrency != 3010:
                financeAmount = acquired['acquisition_price']['value']
            precise = 'Y'
            # logger.info('fundingCurrency:%s---financeAmount:%s' % (fundingCurrency, financeAmount))
        acquireduuid = 1
        source_investors = get_source_investors(acquireduuid,'acquired')
        save(fundingRound,roundStr,fundingCurrency,fundingDate,financeAmount,precise,newsUrl,source_investors=source_investors)

    ipo_fields = item['content']['past_finance']['ipo_fields']
    if ipo_fields.has_key('went_public_on') or ipo_fields.has_key('stock_link') :
        ipo_raise = ipo_fields.get('ipo_amount_raised','')
        fundingRound = 1110; roundStr = 'IPO'; fundingCurrency = None
        fundingDate = None; financeAmount = None; newsUrl = None; precise = 'Y'
        # logger.info('roundStr:%s' ,roundStr)
        if ipo_raise:
            financeAmountUnit = ipo_raise['currency']
            fundingCurrency = get_fundingCurrency(financeAmountUnit)
            financeAmount = ipo_raise['value_usd']
            if fundingCurrency != 3010:
                financeAmount = ipo_raise['value']
            precise = 'Y'
            # logger.info('fundingCurrency:%s---financeAmount:%s'%(fundingCurrency,financeAmount))

        if ipo_fields.has_key('went_public_on'):
            ipoDate = ipo_fields['went_public_on']
            fundingDate = get_fundingDate(ipoDate)
            # logger.info(fundingDate)

        save(fundingRound, roundStr, fundingCurrency, fundingDate, financeAmount, precise, newsUrl)

    finances = item['content']['past_finance']['funding_rounds']
    if len(finances) == 0:
        return
    for finance in finances:
        if finance.has_key("identifier") is False :
            continue
        fundingRound = None; roundStr = None; fundingCurrency = None
        fundingDate = None; financeAmount = None; newsUrl = None; precise = 'Y'
        financeStr = finance['identifier']['value']
        financeuuid = finance['identifier']['uuid']
        if finance['identifier'].has_key('value'):
            fundingRound, roundStr = funding_round(financeStr)
            # logger.info('roundStr:%s',roundStr)
        if finance.has_key('announced_on'):
            financeDate = finance['announced_on']
            fundingDate = get_fundingDate(financeDate)
            # logger.info('fundingDate:%s', fundingDate)
        if finance.has_key("money_raised"):
            financeAmountUnit = finance['money_raised']['currency']
            fundingCurrency = get_fundingCurrency(financeAmountUnit)
            financeAmount = finance['money_raised']['value_usd']
            if fundingCurrency != 3010:
                financeAmount = finance['money_raised']['value']
            precise = 'Y'
            # logger.info('fundingCurrency:%s---financeAmount:%s'%(fundingCurrency,financeAmount))
        source_investors = get_source_investors(financeuuid,'finance')
        save(fundingRound,roundStr,fundingCurrency,fundingDate,financeAmount,precise,newsUrl,source_investors=source_investors)

if __name__ == '__main__':
    while True:
        process()
        logger.info('sleep 30 mins')
        time.sleep(30*60)