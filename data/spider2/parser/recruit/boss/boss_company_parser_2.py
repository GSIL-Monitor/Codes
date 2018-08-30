# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from bson import json_util
from pyquery import PyQuery as pq
from lxml import html
import time


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, download, name_helper,url_helper, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util2'))
import parser_mongo_util

#logger
loghelper.init_logger("boss_company_parser_2", stream=True)
logger = loghelper.get_logger("boss_company_parser_2")

SOURCE = 13055 #Lgou
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=True)


def process():
    logger.info("boss_company_parser mongo begin...")
    while True:

        items = parser_mongo_util.find_process_limit_lagou(SOURCE, TYPE, 0,1000)
        # items = [parser_mongo_util.find_process_one(SOURCE, TYPE, 80002)]
        for item in items:

            r = parse_company(item)

            if r is None or r["status"] == "No_Name":
                # parser_mongo_util.update_active(SOURCE, item["key"], 'N')
                parser_mongo_util.update_processed_lagou(item["_id"])
                logger.info("processed %s with no data", item["url"])
                continue


            for i in r:
                logger.info("%s-%s", i, r[i])
            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))
            #
            parser_mongo_util.save_mongo_recruit_company(r["source"], r["sourceId"], r)
            parser_mongo_util.update_processed_lagou(item["_id"])

        # break
        if len(items) == 0:
                break

        # break

    logger.info("boss_company_parser end.")


def parse_company(item):
    if item is None:
        logger.info("here")
        return None

    logger.info("*** base ***")
    company_key = item["key"]
    html1 = item["content"]
    logger.info(company_key)
    d = pq((html.fromstring(html1.decode("utf-8"))))

    name = d('h1.name').text().strip()

    fullName = d('div.company-business> h4').text()
    if fullName.find("来源")>=0:
        fullName = fullName.split(" ")[-1]

    fullName = name_helper.company_name_normalize(fullName)

    if (name is None or name == "") or (fullName is None or fullName == ""):
        logger.info("here1: %s", name)
        return {
            "status": "No_Name",
        }
    if len(name) > len(fullName):
        name = fullName
    if name is None or name.strip() == "":
        name = fullName

    chinese, companycheck = name_helper.name_check(fullName)
    if companycheck is not True:
        logger.info("here")
        return {
            "status": "No_Name",
        }
    logo = d('div.company-logo> img').attr('src')

    if logo.startswith("http") or logo.startswith("https") or logo.find("default") >= 0:
        pass
    else:
        logo = None

    # if logo.find("default") >= 0:
    #     logo = None

    brief = None
    desc_text = d('div.job-sec> div.text').text()
    logger.info("desc: %s", desc_text)

    if u"该公司尚未添加公司介绍" in desc_text or desc_text == "" or len(desc_text) < 5:
        desc = None
    else:

        desc = desc_text.replace('公司简介：',"").replace("收起","").replace("展开","").replace("&nbsp;","").strip()

    field = ''
    stage = ''
    headCount = ''
    location = ''
    address = ''
    try:
        lll = d('div.info-primary> p').text().strip()
        if len(lll.split(" ")) == 3:
            field = lll.split(" ")[2]
            stage = lll.split(" ")[0]
            headCount = lll.split(" ")[1]

    except:
        pass

    headCount = headCount.replace("人", "")

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



    links = d('div.company-products> ul> li> div.text> div.name> a')
    artifacts = []
    for linkp in links:
        link = pq(linkp)('a').attr("href")
        website = url_helper.url_normalize(link)
        logger.info("website: %s" % website)

        type, app_market, app_id = url_helper.get_market(website)
        if type == 4010:
            if item["url"] != website and website.find("zhipin") == -1:
                flag, domain = url_helper.get_domain(website)
                if flag is not None:
                    if flag is False:
                        domain = None
                    artifacts.append({
                        "type": 4010,
                        "name": name,
                        "description": None,
                        "link": website,
                        "domain": domain
                    })
        elif type == 4020 or type == 4030:
            domain = None
            if domain is not None:
                artifacts.append({
                    "type": type,
                    "name": name,
                    "description": None,
                    "link": website,
                    "domain": domain
                })
        elif type == 4040:
            domain = app_id
            if domain is not None:
                artifacts.append({
                    "type": 4040,
                    "name": name,
                    "description": None,
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
                    "description": None,
                    "link": website,
                    "domain": domain
                })

    #parser member
    members = []

    lis = d('div.manager-list> div> ul >li> div')
    member_rank = 0
    if len(lis) > 0:
        for li in lis:
            mem = pq(li)
            try:
                logo_url = mem('div.info-user> img').attr('src')
                if logo_url.startswith("http") or logo_url.startswith("https"):
                    pass
                else:
                    logo_url = "http:" + logo_url
                member_rank += 1
                member_key = str(item["key"]) + '_' + str(member_rank)
                member_name = mem('p> span.name').text()
                # member_link = mem('p.item_manager_name > a').attr('href')
                member_position = mem('p> span.job-title').text()

                member_desc = mem('div.item_manager_content').text()

                # weibo = None
                # if member_link is not None:
                #     if 'weibo.com' in member_link:
                #         weibo = member_link

                source_member = {'name': member_name,
                                 'photo_url': logo_url,
                                 'weibo': None,
                                 'location': None,
                                 'role': member_position,
                                 'description': member_desc,
                                 'education': None,
                                 'work': None
                                 }
                members.append(source_member)
            except:
                pass

    sourceId2link =  d('div.company-tab> a').eq(0).attr("href")
    if sourceId2link is not None and sourceId2link.find("gongsi") >=0:
        sourceId2 = sourceId2link.split("/")[-1].replace(".html","")
    else:
        sourceId2 =  None

    source_company = {
                      "name": name,
                      "fullName": fullName  if fullName is not None and fullName.strip() != "" else None,
                      "description": desc,
                      "brief": brief,
                      "round": None,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType': funding_type,
                      "locationId": int(0),
                      "address": address,
                      "phone": None,
                      "establishDate": None,
                      "logo": logo,
                      "source": SOURCE,
                      "sourceId": company_key,
                      "sourceId2": sourceId2,
                      "sourceUrl": "https://www.zhipin.com/gongsi/%s.html?ka=company-intro" % company_key,
                      "field": field,
                      "headCountMin": min_staff,
                      "headCountMax": max_staff,
                      "artifacts": artifacts,
                      "members": members,
                      "status": 1,
                      "stage": 0,
                      }

    return source_company






if __name__ == "__main__":
    while True:
        process()
        time.sleep(60*30)