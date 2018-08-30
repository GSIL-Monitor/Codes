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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util2'))
import parser_mongo_util

#logger
loghelper.init_logger("lagou_company_parser_2", stream=True)
logger = loghelper.get_logger("lagou_company_parser_2")

SOURCE = 13050 #Lgou
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=True)


def process():
    logger.info("lagou_company_parser mongo begin...")
    while True:

        items = parser_mongo_util.find_process_limit_lagou(SOURCE, TYPE, 0,1000)
        #items = [parser_mongo_util.find_process_one(SOURCE, TYPE, 147)]
        for item in items:

            r = parse_company(item)

            if r["status"] == "No_Name":
                # parser_mongo_util.update_active(SOURCE, item["key"], 'N')
                parser_mongo_util.update_processed_lagou(item["_id"])
                logger.info("processed %s with no data", item["url"])
                continue

            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

            parser_mongo_util.save_mongo_recruit_company(r["source"], r["sourceId"], r)
            parser_mongo_util.update_processed_lagou(item["_id"])

        if len(items) == 0:
                break

        # break

    logger.info("lagou_company_parser end.")


def parse_company(item):
    if item is None:
        return None

    logger.info("*** base ***")
    company_key = item["key"]
    html = item["content"]
    logger.info(company_key)
    d = pq(html)



    if html.decode("utf-8").find("这个公司的主页还在建设") >= 0:
        return {
            "status": "No_Name",
        }
    name = d('.company_main > h1 > a').text()
    link = d('.company_main > h1 > a').attr('href')
    fullName = d('.company_main > h1 > a').attr('title')
    fullName = name_helper.company_name_normalize(fullName)
    if name is None or fullName is None or (name.find("拉勾")>=0 and company_key != "147"):
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
        desc = raw

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
    location_new = parser_mongo_util.get_location(location)
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

    #parser member
    members = []

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
                                 'work': None
                                 }
                members.append(source_member)
            except:
                pass

    source_company = {
                      "name": name,
                      "fullName": fullName if fullName is not None and fullName.strip() != "" else None,
                      "description": desc,
                      "brief": brief,
                      "round": None,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType': funding_type,
                      "locationId": int(location_id),
                      "address": address,
                      "phone": None,
                      "establishDate": None,
                      "logo": logo,
                      "source": SOURCE,
                      "sourceId": company_key,
                      "sourceUrl": "https://www.lagou.com/gongsi/%s.html" % company_key,
                      "field": field,
                      "headCountMin": min_staff,
                      "headCountMax": max_staff,
                      "artifacts": artifacts,
                      "members": members,
                      "status": 1
                      }

    return source_company



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

                if d_type == u'其他':
                    logger.info("********其他")
                    # news
                    if d_url is not None and d_url.strip() != '' and len(d_url) > 10:
                        logger.info(d_url)
                        pass

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
                        # logger.info(json.dumps(source_footprint, ensure_ascii=False, cls=util.CJsonEncoder))
                        # parser_db_util.save_footprints(source_company_id, source_footprint)


            except Exception,ex:
                logger.exception(ex)




if __name__ == "__main__":
    while True:
        process()
        time.sleep(60*30)