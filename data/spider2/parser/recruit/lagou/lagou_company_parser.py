# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from bson import json_util
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import lxml.html
import time

import lagou_job_parser

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, download, name_helper,url_helper, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("lagou_company_parser", stream=True)
logger = loghelper.get_logger("lagou_company_parser")

SOURCE = 13050 #Lgou
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=True)


def get_blacklist():
    mongo = db.connect_mongo()
    collection = mongo.blacklist.blacklist
    blacks = list(collection.find({"type":3}))
    blacknames = [black["name"] for black in blacks]
    mongo.close()
    return blacknames

def process():
    logger.info("lagou_company_parser begin...")
    bnames = get_blacklist()
    while True:

        items = parser_db_util.find_process_limit(SOURCE, TYPE, 0,1000)
        # items = [parser_db_util.find_process_one(SOURCE, TYPE, 109625)]

        for item in items:

            r = parse_company(item)
            #if r is None:
            #    continue
            if r.has_key("name") and r["name"].strip()!= "":
                for bname in bnames:
                    if r["name"].find(bname) >= 0:
                        logger.info("黑名单")
                        r["status"] = "No_Name"
                        break

            if r["status"] == "No_Name":
                parser_db_util.update_active(SOURCE, item["key"], 'N')
                parser_db_util.update_processed(item["_id"])
                logger.info("processed %s with no data", item["url"])
                continue

            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))
            source_company_id = parser_db_util.save_company_standard(r, download_crawler)
            logger.info("sourceCompanyId : %s", source_company_id)
            parser_db_util.delete_source_company_name(source_company_id)
            parser_db_util.delete_source_mainbeianhao(source_company_id)
            if len(r["name"])< len(r["fullName"]):
                parser_db_util.save_source_company_name(source_company_id, r["name"], 12020)
            parser_db_util.save_source_company_name(source_company_id, r["fullName"], 12010)

            artifacts = []
            artifacts.extend(r["artifacts"])
            logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))
            #artifact provided in lagou do not have any links, ignore that
            #artifacts = parse_artifact(source_company_id, item)
            parser_db_util.save_artifacts_standard(source_company_id, artifacts)
            parseMember_save(source_company_id, item)

            parserDevelop_save(source_company_id, item)

            # job = parser_db_util.find_process_one(SOURCE,36010, item["key_int"])
            # if job:
            #     source_jobs = lagou_job_parser.parse_companyjobs_save(source_company_id, job)
            #     if len(source_jobs) > 0:
            #         parser_db_util.save_jobs_standard(source_jobs)
            #     parser_db_util.update_processed(job["_id"])
            parser_db_util.update_processed(item["_id"])

            #exit()

        if len(items) == 0:
                break

        #break

    logger.info("lagou_company_parser end.")


def parse_company(item):
    if item is None:
        return None

    logger.info("*** base ***")
    company_key = item["key"]
    html = item["content"]
    logger.info(company_key)
    d = pq(html)

    # logo_id processed in parser_db_util
    '''
    logo_id = None
    if logo_url is not None:
        logo_id = parser_util.get_logo_id(source, company_key, 'company', logo_url)
    '''

    if html.decode("utf-8").find("这个公司的主页还在建设") >= 0:
        return {
            "status": "No_Name",
        }
    name = d('.company_main > h1 > a').text()
    link = d('.company_main > h1 > a').attr('href')
    fullName = d('.company_main > h1 > a').attr('title')
    fullName = name_helper.company_name_normalize(fullName)
    if name is None or fullName is None or name.find("拉勾")>=0:
        return {
            "status": "No_Name",
        }
    if len(name) > len(fullName):
        name = fullName
    if name is None or name.strip() == "":
        name = fullName

    chinese, companycheck = name_helper.name_check(fullName)
    if companycheck is not True:
        return {
            "status": "No_Name",
        }
    logo = d('.top_info_wrap > img').attr('src')

    if logo.startswith("http") or logo.startswith("https"):
        pass
    else:
        logo = "http:" + logo

    if logo.find("logo_default") >= 0:
        logo = None

    brief = d('.company_word').text()
    desc_text = d('.company_intro_text').text()

    if u"该公司尚未添加公司介绍" in desc_text or len(desc_text) < 10:
        desc = None
    else:
        desc = d('.company_intro_text > .company_content').html()
        desc = desc.replace('<span class="text_over">展开</span>', '')

        soup = BeautifulSoup(desc,"lxml")
        raw = soup.getText()

        # logger.info(desc)
        #logger.info(raw)

        desc = raw

    # if desc is None or desc.strip() == "":
    #     return {
    #         "status": "No_Name",
    #     }
    field = ''
    stage = ''
    headCount = ''
    location = ''
    address = ''
    try:
        field = d('#basic_container > .item_content >ul > li:eq(0) > span').text()
        stage = d('#basic_container > .item_content >ul > li:eq(1) > span').text()
        headCount = d('#basic_container > .item_content >ul > li:eq(2) > span').text()
        headCount = headCount[0:headCount.index(u'人')]
        location = d('#basic_container > .item_content >ul > li:eq(3) > span').text()
        address = d('.con_mlist_ul > li:eq(0) > p:eq(1)').text()
    except:
        pass

    headCount = headCount.replace("people", "")

    if headCount == "少于15":
        min_staff = 1
        max_staff = 15
    else:
        staffarr = headCount.split('-')
        if len(staffarr) > 1:
            min_staff = staffarr[0]
            max_staff = staffarr[1]
        else:
            try:
                min_staff = int(staffarr[0].strip())
                max_staff = None
            except:
                min_staff = None
                max_staff = None



    funding_type = 0
    if stage == '不需要融资':
        stage = 0
        funding_type = 8010
    elif stage == '未融资':
        stage = 0
    elif stage == '天使轮':
        stage = 1010
    elif stage == 'A轮':
        stage = 1030
    elif stage == 'B轮':
        stage = 1040
    elif stage == 'C轮':
        stage = 1050
    elif stage == 'D轮及以上':
        stage = 1060
    elif stage == '上市公司':
        stage = 1110
    else:
        stage = 0

    location_id=0
    location_new = parser_db_util.get_location(location)
    if location_new != None:
        location_id = location_new["locationId"]

    #website = util.norm_url(link)
    website = url_helper.url_normalize(link)
    logger.info("website: %s" % website)

    artifacts = []
    type, app_market, app_id = url_helper.get_market(website)
    if type == 4010:
        if item["url"] != website and website.find("lagou.com") == -1:
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

    source_company = {
                      "name": name,
                      "fullName": fullName  if fullName is not None and fullName.strip() != "" else None,
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
                      "round": None,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType': funding_type,
                      "locationId": location_id,
                      "address": address,
                      "phone": None,
                      "establishDate": None,
                      "logo": logo,
                      "source": SOURCE,
                      "sourceId": company_key,
                      "field": field,
                      "subField": None,
                      "tags": None,
                      "headCountMin": min_staff,
                      "headCountMax": max_staff,
                      "artifacts": artifacts,
                      "status": 1
                      }

    return source_company
'''
def parse_artifact(source_company_id,item):
    if item is None:
        return None
    logger.info("*** artifacts ***")
    html = item["content"]
    d = pq(html)
    artifacts = []
    # artifact
    products = d('.product_details')
    for product in products:
        p = pq(product)
        link = p('.product_url > a').attr('href')
        name = p('.product_url > a').text()
        desc = p('.product_profile').text()

        # type
        lis = p('.product_details > ul > li')
        type = []
        if len(lis) > 0:
            for li in lis:
                if '网站' in pq(li).text():
                    if link is not None:
                        type.append(4010)
                if '移动app' in pq(li).text():
                    type.append(4040)
                    type.append(4050)

        artifact = {"sourceCompanyId": source_company_id,
                           "name": name,
                           "description": desc,
                           "link": link,
                           "type": type}

        for t in type:
            if t != 4010:
                artifact["link"] = None
            artifact["type"] = t

            artifacts.append(artifact)
            #for i in artifact:
            #    logger.info("%s -> %s",i, artifact[i])


    return artifacts
'''
def parseMember_save(source_company_id,item):
    if item is None:
        return
    logger.info("*** member ***")
    html = item["content"]
    d = pq(html)

    lis = d('.manager_list > li')
    member_rank = 0
    if len(lis) > 0:
        for li in lis:
            mem = pq(li)
            try:
                logo_url = mem('img').attr('src')
                if logo_url.startswith("http") or logo_url.startswith("https"):
                    pass
                else:
                    logo_url = "http:" + logo_url
                member_rank += 1
                member_key = str(item["key"]) + '_' + str(member_rank)
                member_name = mem('p.item_manager_name > span').text()
                member_link = mem('p.item_manager_name > a').attr('href')
                member_position = mem('p.item_manager_title').text()

                member_desc = mem('div.item_manager_content').text()

                # print member_position
                # print member_name
                # print member_desc

                weibo = None
                if member_link is not None:
                    if 'weibo.com' in member_link:
                        weibo = member_link

                source_member = {'name': member_name,
                                 'photo_url': logo_url,
                                 'weibo': weibo,
                                 'location': None,
                                 'role': member_position,
                                 'description': member_desc,
                                 'education': None,
                                 'work': None,
                                 'source': SOURCE,
                                 'sourceId': member_key,
                                 }
                ptype = name_helper.position_check(member_position)
                source_company_member_rel = {
                    'sourceCompanyId': source_company_id,
                    'position': member_position,
                    'joinDate': None,
                    'leaveDate': None,
                    'type': ptype
                }
                logger.info(json.dumps(source_member, ensure_ascii=False, cls=util.CJsonEncoder))

                parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)

            except Exception,ex:
                logger.exception(ex)



def parserDevelop_save(source_company_id,item):
    if item is None:
        return
    logger.info("*** Development ***")
    html = item["content"]
    d = pq(html)
    #news & footprint
    lis = d('.history_ul > li')
    develop_rank = 0
    if len(lis) > 0:
        d_date = None
        for li in lis:
            try:
                d = pq(li)
                d_day = d('.date_day').text()
                d_year =  d('.date_year').text()
                d_month=None
                if d_year is not None:
                    d_month = d_year[5:].strip()
                    if d_month == 'Jan':
                        d_month = '01'
                    elif d_month == 'Feb':
                        d_month = '02'
                    elif d_month == 'Mar':
                        d_month = '03'
                    elif d_month == 'Apr':
                        d_month = '04'
                    elif d_month == 'May':
                        d_month = '05'
                    elif d_month == 'Jun' or d_month == 'June':
                        d_month = '06'
                    elif d_month == 'Jul' or d_month == 'July':
                        d_month = '07'
                    elif d_month == 'Aug':
                        d_month = '08'
                    elif d_month == 'Sep' or d_month == 'Sept':
                        d_month = '09'
                    elif d_month == 'Oct':
                        d_month = '10'
                    elif d_month == 'Nov':
                        d_month = '11'
                    elif d_month == 'Dec':
                        d_month = '12'

                    d_year = d_year[0:4]

                d_type = d('div.li_type_icon').attr('title')
                d_title = d('div.li_desc > p').text()
                d_url =  d('div.li_desc > p').attr('data-href')
                d_key = util.md5str(d_url)

                if d_year is None or d_year == '':
                    d_date = d_date
                else:
                    d_date = d_year+'-'+d_month+'-'+d_day
                logger.info("date: %s", d_date)

                develop_rank += 1
                develop_key = str(item["key"])+'_'+str(develop_rank)

                if d_type == u'资本':
                    pass
                    # comment Investment
                    # investors = d('.desc_intro').text()
                    # investors = ''.join(investors)
                    # #logger.info("investors_initial: %s", investors)
                    # try:
                    #     if investors.find("融资金额") >= 0:
                    #         (investors,) = util.re_get_result(u'融资机构：(.*?) ；', investors)
                    #     else:
                    #         #logger.info("find here %s",investors)
                    #         (investors,) = util.re_get_result(u'融资机构：(.*?)$', investors)
                    # except Exception, e:
                    #     investors = None
                    #
                    # investment = None
                    # round = None
                    # unit = None
                    # currency = ''
                    # precise = 'Y'
                    #
                    # funding = d_title.replace('获得','').replace('轮融资', '')
                    # logger.info(funding)
                    #
                    # try:
                    #     funding = funding.replace('元', '')
                    #     if u'亿' in funding:
                    #         f_arr = funding.split(u'亿')
                    #
                    #         if '.' in f_arr[0]:
                    #             investment = int(f_arr[0].replace('.', '')) * 1000
                    #         else:
                    #             investment = int(f_arr[0]) * 10000
                    #
                    #         round = f_arr[1]
                    #         unit = 0
                    #     else:
                    #         try:
                    #             (investment,) = util.re_get_result('(\d+)', funding)
                    #
                    #         except:
                    #             pass
                    #
                    #         if investment is not None:
                    #             round = funding.split(investment)[1]
                    #
                    #
                    #     if funding.find('美') > 0:
                    #         currency = 3010
                    #     else:
                    #         currency = 3020
                    #
                    #     if funding.find('￥') > 0:
                    #         currency = 3020
                    #     elif funding.find('$') > 0:
                    #         currency = 3010
                    #
                    #     if investment is not None:
                    #         investment = str(investment).replace('$', '').replace('￥', '')\
                    #         .replace('美金', '').replace('美', '')
                    #
                    #
                    #     if u'数' in funding:
                    #         precise = 'N'
                    #
                    #     if round is None:
                    #         round = funding.replace('数', '')
                    #
                    #     if u'千' in round:
                    #         investment = 1000
                    #         unit = 0
                    #     elif u'百' in round:
                    #         investment = 100
                    #         unit = 0
                    #     elif u'十' in round:
                    #         investment = 10
                    #         unit = 0
                    #
                    #     if unit == 0:
                    #         investment = int(investment) * 10000
                    #
                    #     if investment is None:
                    #         investment = 0
                    #
                    #     if investment == 0:
                    #         precise ='N'
                    #     else:
                    #         try:
                    #             if int(investment)< 10000:
                    #                 investment = int(investment) * 10000
                    #         except:
                    #             pass
                    #     logger.info("investment %s", investment)
                    #
                    #     round = round.replace('万', '').replace('千', '').replace('百', '').replace('十', '')
                    #     round = round.replace('美', '')
                    #
                    #     roundDesc=None
                    #     if u'天使' in round:
                    #         round = 1010
                    #         roundDesc="天使"
                    #     elif 'Pre-A' in round:
                    #         round = 1020
                    #         roundDesc = "Pre-A"
                    #     elif 'A' in round:
                    #         round = 1030
                    #         roundDesc = "A"
                    #     elif 'B' in round:
                    #         round = 1040
                    #         roundDesc = "B"
                    #     elif 'C' in round:
                    #         round = 1050
                    #         roundDesc = "C"
                    #     elif 'D' in round:
                    #         round = 1060
                    #         roundDesc = "D"
                    #     elif 'E' in round:
                    #         round = 1070
                    #         roundDesc = "E"
                    #     elif 'F' in round:
                    #         round = 1080
                    #         roundDesc = "F"
                    #     else:
                    #         round = 0
                    #
                    #
                    #     logger.info("round %s", round)
                    #     logger.info("roundDesc %s",roundDesc)
                    #
                    #
                    #     source_funding ={
                    #                      "sourceCompanyId": source_company_id,
                    #                      "preMoney": None,
                    #                      "postMoney": None,
                    #                      "investment": investment,
                    #                      "round": round,
                    #                      "roundDesc": roundDesc,
                    #                      "currency": currency,
                    #                      "precise": precise,
                    #                      "fundingDate": d_date,
                    #              }
                    #
                    #
                    #     # logger.info(source_funding)
                    #
                    #     logger.info(investors)
                    #     investor_list = []
                    #     if investors is not None:
                    #         investors = investors.replace(" " , "").replace("，" , ",").replace("、" , ",")\
                    #             .replace("跟投","").replace("领投","")
                    #         investors_arr = investors.split(",")
                    #         investor_key = 0
                    #         for investor in investors_arr:
                    #             #logger.info("investor:%s", investor)
                    #             if investor.find("、") >= 0:
                    #                 continue
                    #             if investor != '':
                    #                 logger.info("investor:%s",investor)
                    #                 investor_key += 1
                    #                 sourceId = develop_key+'_'+ str(investor_key)
                    #
                    #                 if '个人' in investor:
                    #                     type = 10010
                    #                 else:
                    #                     type = 10020
                    #
                    #                 invstor_content = {
                    #                                    'logo_url': None,
                    #                                    'name': investor,
                    #                                    'website': None,
                    #                                    'description': None,
                    #                                    'stage': None,
                    #                                    'field': None,
                    #                                    'type': type,
                    #                                    'source': SOURCE,
                    #                                    'sourceId': sourceId
                    #                                    }
                    #
                    #                 investor_list.append(invstor_content)
                    #
                    #     parser_db_util.save_funding_standard(source_funding, download_crawler, investor_list)
                    #
                    #
                    #
                    # except Exception,e:
                    #     logger.exception(e)


                if d_type == u'其他':
                    logger.info("********其他")
                    # news
                    if d_url is not None and d_url.strip() != '' and len(d_url) > 10:
                        logger.info(d_url)
                        pass
                        '''
                        try:
                            r = requests.get(d_url, timeout= 10)
                            r.encoding = r.apparent_encoding
                            content = r.text

                            # print content[0:500]

                            source_news = {"source": source,
                                           "news_key": d_key,
                                           "company_key": company_key,
                                           "url": d_url,
                                           "title": d_title,
                                           "date": d_date,
                                           "domain": 'lagou',
                                           "content": content
                                            }

                            parser_util.insert_source_news(source_news)
                        except Exception,e :
                            pass
                        '''
                    #footprint
                    else:
                        logger.info("FOOTPRINT")
                        if d_date is None:
                            continue
                        source_footprint = [{"source": SOURCE,
                                            "sourceCompanyId": source_company_id,
                                            "footDate": d_date,
                                            "footDesc":  d_title,
                                    }]
                        logger.info(json.dumps(source_footprint, ensure_ascii=False, cls=util.CJsonEncoder))
                        parser_db_util.save_footprints(source_company_id, source_footprint)


            except Exception,ex:
                logger.exception(ex)




if __name__ == "__main__":
    while True:
        process()
        time.sleep(60*30)