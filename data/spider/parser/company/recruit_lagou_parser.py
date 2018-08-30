# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html

from bson.objectid import ObjectId
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import requests
import util
import parser_util
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup



source = 13050
def parse_company(company_key):
    company = fromdb.company.find_one({"source": source, "company_key":company_key})
    if company == None:
        return

    content = company["content"]

    d = pq(content)

    logo_url = d('.top_info_wrap > img').attr('src')
    logo_id = None
    if logo_url is not None:
        logo_id = parser_util.get_logo_id(source, company_key, 'company', logo_url)

    name = d('.company_main > h1 > a').text()
    link = d('.company_main > h1 > a').attr('href')
    website = util.norm_url(link)
    fullName = d('.company_main > h1 > a').attr('title')

    # print logo_id
    # print name
    # print website
    # print fullName

    if name is None or fullName is None:
        return

    if len(name) > len(fullName):
        name = fullName

    brief = d('.company_word').text()
    desc_text = d('.company_intro_text').text()

    # print website
    # print brief
    # print desc

    if u"该公司尚未添加公司介绍" in desc_text or len(desc_text) < 10 :
        return

    desc = d('.company_intro_text > .company_content').html()
    desc = desc.replace('<span class="text_over">展开</span>', '')

    soup = BeautifulSoup(desc)
    raw = soup.getText()

    # logger.info(desc)
    logger.info(raw)

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

    if headCount == "少于15":
        min_staff = 1
        max_staff = 15
    else:
        staffarr = headCount.split('-')
        if len(staffarr) > 1:
            min_staff = staffarr[0]
            max_staff = staffarr[1]
        else:
            min_staff = staffarr[0]
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

    location_id = parser_util.get_location_id(location)


    source_company = {"name": name,
                      "fullName": fullName,
                      "description": desc,
                      "brief": brief,
                      "round": stage,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType':funding_type,
                      "locationId": location_id,
                      "address": address,
                      "phone": None,
                      "establishDate": None,
                      "logo": logo_id,
                      "source": source,
                      "sourceId": company_key,
                      "field": field,
                      "subField": None,
                      "tags": None,
                      "headCountMin": min_staff,
                      "headCountMax": max_staff
                      }
    source_company_id = parser_util.insert_source_company(source_company)

    parse_artifact(d, source_company_id)

    parser_member(d, company_key, source_company_id)

    parser_develop(d, company_key, source_company_id)


    parser_job(company_key, source_company_id)

    msg = {"type":"company", "id":source_company_id}
    logger.info(msg)
    kafka_producer.send_messages("parser_v2", json.dumps(msg))


def parse_artifact(d, source_company_id):
    logger.info('*********** parsing artifact **************')
    products = d('.product_details')
    for product in products:
        p = pq(product)
        link = p('.product_url > a').attr('href')
        name = p('.product_url > a').text()
        desc = p('.product_profile').text()

        #type
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

        source_artifact = {"sourceCompanyId": source_company_id,
                           "name": name,
                           "description": desc,
                           "link": link,
                           "type": type}

        for t in type:
            if t != 4010:
                source_artifact["link"] = None

            source_artifact["type"] = t
            parser_util.insert_source_artifact(source_artifact)



def parser_member(d, company_key, source_company_id):
    logger.info('*********** parsing member **************')
    lis = d('.manager_list > li')
    member_rank = 0
    if len(lis) > 0:
        for li in lis:
            mem = pq(li)
            try:
                logo_url = mem('img').attr('src')

                member_rank += 1
                member_key = str(company_key)+'_'+str(member_rank)
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
                                'location':None,
                                'role': member_position,
                                'description': member_desc,
                                'education': None,
                                'work': None,
                                'source': source,
                                'sourceId': member_key,
                                }

                source_company_member_rel = {
                                'sourceCompanyId':source_company_id,
                                'position': member_position,
                                'joinDate': None,
                                'leaveDate': None,
                                'type':0
                                }

                parser_util.insert_source_member(source_member, source_company_member_rel)

            except Exception,ex:
                logger.exception(ex)



def parser_develop(d, company_key, source_company_id):
    logger.info('*********** parsing develop **************')
    #news & footprint
    lis = d('.history_ul > li')
    develop_rank = 0
    if len(lis) > 0:
        for li in lis:
            try:
                d_day = d('.date_day').text()
                d_year =  d('.date_year').text()
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
                    d_date = None
                else:
                    d_date = d_year+'-'+d_month+'-'+d_day


                develop_rank += 1
                develop_key = str(company_key)+'_'+str(develop_rank)

                if d_type == u'资本':
                    investors = d('.desc_intro').text()
                    investors = ''.join(investors)
                    try:
                        (investors,) = util.re_get_result(u'融资机构：(.*?) ；', investors)
                    except Exception, e:
                        investors = None

                    investment = None
                    round = None
                    unit = None
                    currency = ''
                    precise = 'Y'

                    funding = d_title.replace('获得','').replace('轮融资', '')
                    logger.info(funding)

                    try:
                        funding = funding.replace('元', '')
                        if u'亿' in funding:
                            f_arr = funding.split(u'亿')

                            if '.' in f_arr[0]:
                                investment = int(f_arr[0].replace('.', '')) * 1000
                            else:
                                investment = int(f_arr[0]) * 10000

                            round = f_arr[1]
                            unit = 0
                        else:
                            try:
                                (investment,) = util.re_get_result('(\d+)', funding)

                            except Exception, e:
                                pass

                            if investment is not None:
                                round = funding.split(investment)[1]


                        if currency == '美':
                            currency = 3010
                        else:
                            currency = 3020

                        if '￥'in str(investment):
                            currency = 3020
                        elif '$' in str(investment):
                            currency = 3020

                        investment = str(investment).replace('$', '').replace('￥', '')\
                            .replace('美金', '').replace('美', '')


                        if u'数' in funding:
                            precise = 'N'

                        if round is None:
                            round = funding.replace('数', '')

                        if u'千' in round:
                            investment = 1000
                            unit = 0
                        elif u'百' in round:
                            investment = 100
                            unit = 0
                        elif u'十' in round:
                            investment = 10
                            unit = 0

                        if unit == 0:
                            investment = int(investment) * 10000

                        if investment is None:
                            investment = 0

                        if investment == 0:
                            precise ='N'
                        elif investment < 1000:
                            investment = int(investment) * 10000

                        roundDesc = round

                        round = round.replace('万', '').replace('千', '').replace('百', '').replace('十', '')
                        round = round.replace('美', '')


                        if u'天使' in round:
                            round = 1010
                        elif 'Pre-A' in round:
                            round = 1020
                        elif 'A' in round:
                            round = 1030
                        elif 'B' in round:
                            round = 1040
                        elif 'C' in round:
                            round = 1050
                        elif 'D' in round:
                            round = 1060
                        elif 'E' in round:
                            round = 1070
                        elif 'F' in round:
                            round = 1080
                        else:
                            round = 0


                        logger.info(investment)
                        logger.info(round)


                        source_funding ={
                                         "sourceCompanyId": source_company_id,
                                         "preMoney": None,
                                         "postMoney": None,
                                         "investment": investment,
                                         "round": round,
                                         "roundDesc": roundDesc,
                                         "currency": currency,
                                         "precise": precise,
                                         "fundingDate": d_date,
                                 }

                        # logger.info(source_funding)

                        logger.info(investors)
                        investor_list = []
                        if investors is not None:
                            investors_arr = investors.split(',')
                            investor_key = 0
                            for investor in investors_arr:
                                if investor != '':
                                    investor_key += 1
                                    sourceId = str(company_key)+'_'+ str(investor_key)

                                    if '个人' in investor:
                                        type = 10010
                                    else:
                                        type = 10020

                                    invstor_content = {'source': source,
                                                       'sourceId': sourceId,
                                                       'logo_url': None,
                                                       'name': investor,
                                                       'website': None,
                                                       'description': None,
                                                       'stage': None,
                                                       'field': None,
                                                       'type': type,
                                                       'source': source,
                                                       'sourceId': sourceId
                                                       }

                                    investor_list.append(invstor_content)

                        parser_util.insert_source_funding(source_funding, investor_list)


                    except Exception,e:
                        logger.exception(e)

                    continue

                if d_type == u'其他':
                    # news
                    if d_url is not None or d_url != '' or len(d_url) > 10:
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

                    #footprint
                    else:
                        source_footprint = {"source": source,
                                            "sourceCompanyId": source_company_id,
                                            "footDate":d_date,
                                            "description": d_title,
                                    }
                        parser_util.insert_source_footprint(source_footprint)

            except Exception,ex:
                logger.exception(ex)


def parser_job(company_key, source_company_id):
    logger.info('*********** parsing job **************')
    jobs = fromdb.job.find({"source": source, "company_key":company_key})
    for job in jobs:
        job_key = job["job_key"]
        job_content = job["content"]

        born_time = job_content["bornTime"]
        position = job_content["positionName"]
        education = job_content["education"]
        city = job_content["city"]
        # keywords = job_content["keyWords"]
        salary = job_content["salary"]
        work_year = job_content["workYear"]
        position_type = job_content["positionFirstType"]
        update_time = job_content["createTime"]


        location_id = parser_util.get_location_id(city)

        education_type = 0
        if education == '大专':
            education_type = 6020
        elif education == '本科':
            education_type = 6030
        elif education == '硕士':
            education_type = 6040
        elif education == '博士':
            education_type = 6050

        workYear_type = 7000
        if work_year == '应届毕业生':
            workYear_type = 7010
        elif work_year == '1年以下':
            workYear_type = 7020
        elif work_year == '1-3年':
            workYear_type = 7030
        elif work_year == '3-5年':
            workYear_type = 7040
        elif work_year == '5-10年':
            workYear_type = 7050
        elif work_year == '10年以上':
            workYear_type = 7060


        domain = 0
        if position_type == '技术':
            domain = 15010
        elif position_type == '产品':
            domain = 15020
        elif position_type == '设计':
            domain = 15030
        elif position_type == '运营':
            domain = 15040
        elif position_type == '市场与销售':
            domain = 15050
        elif position_type == '职能':
            domain = 15060
        elif position_type == '金融':
            domain = 15070

        date = "%s" % time.strftime("%Y-%m-%d", time.localtime())
        if '-' not in born_time:
            born_time = date+ ' '+ born_time.strip()
        if '-' not in update_time and update_time != None:
            update_time = date+ ' '+ update_time.strip()

        source_job = {
                    "sourceId": job_key,
                    "sourceCompanyId": source_company_id,
                    "position": position,
                    "salary": salary,
                    "description": None,
                    "domain": domain,
                    "locationId": location_id,
                    "educationType": education_type,
                    "workYearType": workYear_type,
                    "startDate": born_time,
                    "updateDate": update_time,
                    }

        parser_util.insert_source_job(source_job)


if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("recruit_lagou", "crawler_recruit_lagou")

    i = 0
    threads = []
    msgs = []
    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    company_key = msg["company_key"]

                    if type == "company":
                        parse_company(company_key)

                    kafka_consumer.task_done(message)
                    kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("recruit_lagou", "crawler_recruit_lagou")
