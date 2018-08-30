# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json
import pymongo
from pymongo import MongoClient
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper
import name_helper
import util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/goshang'))
import qixinbao

#logger
loghelper.init_logger("company_goshang_expand", stream=True)
logger = loghelper.get_logger("company_goshang_expand")

#mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang

COMPANIES = []

def save_collection_goshang(collection_name, item1, item2=None):
    if item2 is None:
        item = item1
    else:
        item = item2

    #in case that related companies have been saved before
    record = collection_name.find_one({"name": item["name"]})
    if record is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        id = collection_name.insert(item)
    else:
        id = record["_id"]
        item["modifyTime"] = datetime.datetime.now()
        collection_name.update_one({"_id": id}, {'$set': item})
    return id

def update_time(row_id):
    conn = db.connect_torndb()
    # sql = "update source_company_name set gongshangCheckTime=now() where id=%s"
    sql = "update company_alias set gongshangCheckTime=now() where id=%s"
    #logger.info(sql, row_id)
    conn.update(sql, row_id)
    conn.close()


def query_goshang():
    qinxinbao_search_crawler = qixinbao.QixinbaoSearchCrawler()
    qinxinbao_company_crawler = qixinbao.QixinbaoCompanyCrawler()

    while True:
        if len(COMPANIES) == 0:
            return
        alias = COMPANIES.pop(0)
        logger.info("Company: %s Start gongshang check!!!", alias["name"])

        # if source_company_name["type"] != 12010 or source_company_name["chinese"] == 'N':
        #     continue

        check_goshang_name = collection_goshang.find_one({"name": alias["name"]})

        if check_goshang_name is None:
            company_urls = qinxinbao_search_crawler.query_by_company(alias["name"])
            #logger.info(company_urls)
            # Get several urls for related companies, save all data into mongo
            for company_url in company_urls:
                if company_url["company_name"] is None or company_url["link"] is None:
                    continue
                check_gongshang_name_f = collection_goshang.find_one({"name": company_url["company_name"]})


                if check_gongshang_name_f is not None:
                    continue

                items_qixinbao = qinxinbao_company_crawler.query_by_company_url(company_url["link"])
                if len(items_qixinbao) != 1:
                    logger.info("Wrong goshang data")
                    continue
                item_qixinbao = items_qixinbao[0]

                logger.info(item_qixinbao)
                goshangBaseId = save_collection_goshang(collection_goshang, item_qixinbao)

                # but only save exact 1 company into source_company_goshang_re
                #if item_qixinbao["name"] == source_company_name["name"]:
                    # save_company_goshang_rel(goshangBaseId, source_company_id)
                #    pass
        else:
            logger.info("%s already existed", alias["name"])

        update_time(alias["id"])



def start_run(concurrent_num):
    # while True:
    #     logger.info("Company gongshang start...")
    #
    #     conn = db.connect_torndb()
    #     #source_company_names = conn.query("select * from source_company_name where type=12010 and chines='Y' and gongshangCheckTime is null order by id desc")
    #     source_company_names = conn.query("select * from source_company_name where sourceCompanyId=31098")
    #     conn.close()
    #     for source_company_name in source_company_names:
    #         company_name = source_company_name["name"]
    #         #NAME CHECK
    #         chinese, is_company = name_helper.name_check(company_name)
    #         if chinese and is_company:
    #             COMPANIES.append(source_company_name)
    #
    #     logger.info(json.dumps(COMPANIES, ensure_ascii=False, cls=util.CJsonEncoder))
    #
    #     threads = [gevent.spawn(query_goshang()) for i in xrange(concurrent_num)]
    #     gevent.joinall(threads)
    #
    #
    #     logger.info("Company gongshang end.")
    #
    #     if len(COMPANIES) == 0:
    #         gevent.sleep(10*60)

    logger.info("Company gongshang start...")
    while True:
        conn = db.connect_torndb()
        company_aliases = conn.query("select * from company_alias where type=12010 and gongshangCheckTime is null order by id desc limit 1000")
        conn.close()
        for alias in company_aliases:
            company_name = alias["name"]
            #NAME CHECK
            chinese, is_company = name_helper.name_check(company_name)
            if chinese and is_company:
                COMPANIES.append(alias)

        #logger.info(json.dumps(COMPANIES, ensure_ascii=False, cls=util.CJsonEncoder))

        if len(COMPANIES) > 0:
            threads = [gevent.spawn(query_goshang) for i in xrange(concurrent_num)]
            gevent.joinall(threads)
        else:
            logger.info("Company gongshang end.")
            gevent.sleep(10*60)
            logger.info("Company gongshang start...")

if __name__ == "__main__":
    start_run(10)