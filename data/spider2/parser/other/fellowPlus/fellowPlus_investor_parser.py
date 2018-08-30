# -*- coding: utf-8 -*-
import os, sys
from pyquery import PyQuery as pq
import json, datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("fellowPlus_investor_parser", stream=True)
logger = loghelper.get_logger("fellowPlus_investor_parser")


SOURCE = 13042
TYPE = 36004


from pymongo import MongoClient
import gridfs
import pymongo
mongo = db.connect_mongo()
collection_investor = mongo.fellowplus.investor
collection_org = mongo.fellowPlus.org
imgfs = gridfs.GridFS(mongo.gridfs)


def process():
    logger.info("fellowPlus_investor_parser begin...")
    items = parser_db_util.find_process(SOURCE, TYPE)
    # items = [parser_db_util.find_process_one_key(SOURCE, TYPE, "126_9")]
    for item in items:
        key = item["key"]
        info = parser(item)
        # break
        # collection_content = {
        #     "date":datetime.datetime.now(),
        #     "source":SOURCE,
        #     "type":TYPE,
        #     "url":item['url'],
        #     "key":key,
        #     "info":investor_info
        # }
        info["createTime"] = datetime.datetime.now()
        info["source"] = SOURCE
        info["type"] = TYPE
        info["url"] = item["url"]
        info["key"] = item["key"]

        parser_item = collection_investor.find_one({"source":SOURCE, "type":TYPE, "key":key})
        if parser_item is not None:
            collection_investor.delete_one({"source":SOURCE, "type":TYPE, "key":key})
        collection_investor.insert_one(info)


        # user_focus_field = investor_info['user_focus_field']
        # fields = user_focus_field.split('、')
        # for field in fields:
        #     tag_item =collection_field.find_one({'name': field})
        #     if tag_item is None:
        #         field_content = {'name': field, 'count': 1}
        #         collection_field.insert_one(field_content)
        #     else:
        #         tag_item['count'] = tag_item['count']+1
        #         _id = tag_item["_id"]
        #         collection_field.update_one({'_id':_id}, {"$set": tag_item})

        # org_name = info['org_name']
        # org_item = collection_org.find_one({'org_name': org_name})
        # users = []
        # user = {'name': info['name'], 'position': info['org_position']}
        # if org_item is None:
        #     users.append(user)
        #     org_content = {'org_name': org_name, 'users': users}
        #     collection_org.insert_one(org_content)
        # else:
        #     users = org_item['users']
        #     e_flag = False
        #     for u in users:
        #         if u["name"] == user["name"]: e_flag = True; break
        #     if e_flag is False:
        #         users.append(user)
        #         _id = org_item["_id"]
        #         collection_org.update_one({'_id':_id}, {"$set": org_item})

        # parser_db_util.update_processed(item["_id"])
        #break
    logger.info("fellowPlus_investor_parser end.")

def get_companyIds(website,name):
    cids = []
    conn = db.connect_torndb()
    if website is not None and website.strip() != "":
        artifacts = conn.query("select * from artifact where link=%s and (active='Y' or active is null)", website)
        for artifact in artifacts:
            if artifact["companyId"] is not None:
                company = conn.get("select * from company where id=%s and (active='Y' or active is null)", artifact["companyId"])
                if company is not None:
                    logger.info("*******website %s matched company: %s|%s|%s",
                                website, company["name"], company["id"], company["code"])
                    if int(company["id"]) not in cids:
                        cids.append(int(company["id"]))
    if len(cids) == 0 and name is not None and name.strip() != "":
        companies = conn.query("select * from company where name=%s and (active='Y' or active is null)", name)
        cid = None
        company_scores = None
        for cp in companies:
            logger.info("*******name %s matched company: %s|%s|%s", name, cp["name"], cp["id"], cp["code"])
            cs = conn.get("select * from company_scores where companyId=%s and type=37010", cp["id"])
            if cs is None: cs = {"score": None}
            if cid is None:
                cid = int(cp["id"])
                company_scores = cs["score"]
            else:
                if company_scores is None or (company_scores is not None and cs["score"] is not None and company_scores<cs["score"]):
                    cid = int(cp["id"])
                    company_scores = cs["score"]
        if cid not in cids:
            cids.append(cid)
    # logger.info(cids)
    conn.close()
    return cids

def parser(item):
    if item is None:
        return None

    html = item["content"]
    d = pq(html)

    photo = d('.photo').attr('src')
    name = d('span.fn:eq(0)').text()
    org_name = d('span.org:eq(0)').text()
    org_position = d('span.category:eq(0)').text()
    user_invest_desc = d('.foudation:eq(0)').text()

    user_focus_field = d('.investment-style > li:eq(0) > p').text()
    user_invest_stage = d('.investment-style > li:eq(1) > p').text()
    user_location = d('.investment-style > li:eq(2) > p').text()
    invest_num_each_year = d('.investment-style > li:eq(3) > p').text()
    invest_amount = d('.investment-style > li:eq(4) > p').text()

    products = []
    works = []
    educations = []
    companyIds = []
    product_list = d('.production-list > li')
    for product in product_list:
        pd = pq(product)
        user_invest_product = {}
        user_invest_product['website'] = pd('li > a').attr('href')
        user_invest_product['logo'] = pd('img').attr('src')
        user_invest_product['name'] = pd('.info-main > h4').text()
        user_invest_product['stage'] = pd('.info-main > p').text()
        user_invest_product['desc'] = pd('.intro').text()
        products.append(user_invest_product)

        related_cids = get_companyIds(user_invest_product['website'], user_invest_product['name'])
        for cid in related_cids:
            if cid not in companyIds and cid is not None: companyIds.append(cid)

    user_activeness = d('.activeness:eq(0) > span.text').text()
    sub_blocks = d('.sub-block')
    for sub_block in sub_blocks:
        bd = pq(sub_block)
        if bd('h6').text() == '工作经历':
            lis = bd('ul.experience >li')
            for li in lis:
                work = {}
                work['experience'] = pq(li)('h6').text()
                work['year'] = pq(li)('p').text()
                works.append(work)
        if bd('h6').text() == '教育经历':
            lis = bd('ul.experience >li')

            for li in lis:
                education = {}
                education['experience'] = pq(li)('h6').text()
                education['year'] = pq(li)('p').text()
                educations.append(education)

    investor_info = {
        'photo' : photo,
        'name' : name,
        'org_name' : org_name,
        'org_position' : org_position,
        'user_invest_desc' : user_invest_desc,
        'user_focus_field' : user_focus_field,
        'user_invest_stage' : user_invest_stage,
        'user_location' : user_location,
        'invest_num_each_year' : invest_num_each_year,
        'invest_amount' : invest_amount,
        'products' : products,
        'works' : works,
        'educations' : educations,
        'user_activeness': user_activeness,
        'companyIds': companyIds
    }

    logger.info(json.dumps(investor_info, ensure_ascii=False))
    return investor_info


if __name__ == "__main__":
    process()