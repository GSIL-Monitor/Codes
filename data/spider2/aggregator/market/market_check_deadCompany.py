# -*- coding: utf-8 -*-
import os, sys
import time,datetime
import json
from kafka import (KafkaClient, SimpleProducer)
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper,url_helper
import db,config
import name_helper, hz, desc_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/website'))
import website


#logger
loghelper.init_logger("Company_data_clean", stream=True)
logger = loghelper.get_logger("Company_data_clean")

# kafka
kafkaProducer = None
mongo = db.connect_mongo()
collection_website = mongo.info.website

def save_collection_website(collection_name, item):
    #in case that related websites have been saved before
    record = collection_name.find_one({"url": item["url"]})
    if record is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        try:
            id = collection_name.insert(item)
        except:
            return None
    else:
        id = record["_id"]
        item["modifyTime"] = datetime.datetime.now()
        collection_name.update_one({"_id": id}, {'$set': item})
    return id


def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def send_message(company_id, action):
    #action: create, delete
    msg = {"type":"company", "id":company_id , "action":action}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


if __name__ == "__main__":
    init_kafka()
    conn = db.connect_torndb()

    num1=0;num2=0;num3=0;num4=0;num5=0;num6=0;num7=0;num8=0
    companies = list(conn.query("select * from company where (active is null or active='Y') order by id desc"))
    cids = []
    for company in companies:
        num1+=1
        company_id = company["id"]
        if len(conn.query("select * from funding where (active is null or active='Y') and companyId=%s", company_id)) ==0:continue
        num2+=1
        # if company["website"] is None or company["website"].strip()=="": num3+=1;continue
        # num4+=1
        # if company["locationId"] is not None and company["locationId"] > 370: continue
        #
        # meta = collection_website.find_one({"url": company["website"]})
        #
        # if meta is None:
        #     num5+=1;continue
        #     # meta = website.get_meta_info(company["website"])
        #     # if meta:
        #     #     websiteId = save_collection_website(collection_website, meta)
        #     # else:
        #     #     meta = {
        #     #         "url": company["website"],
        #     #         "httpcode": 404
        #     #     }
        #     #     websiteId = save_collection_website(collection_website, meta)
        #     # if meta:
        #     #     # 发生转跳
        #     #     # logger.info(meta)
        #     #     if meta["httpcode"] == 200:
        #     #         redirect_url = meta.get("redirect_url")
        #     #         if company["website"] != redirect_url:
        #     #             url = url_helper.url_normalize(meta["redirect_url"])
        #     #             (flag_new, domain_new) = url_helper.get_domain(url)
        #     #
        #     #             meta_new = {
        #     #                 "url": url,
        #     #                 "domain": domain_new if flag_new is True else None,
        #     #                 "redirect_url": url,
        #     #                 "title": meta["title"],
        #     #                 "tags": meta["tags"],
        #     #                 "description": meta["description"],
        #     #                 "httpcode": 200
        #     #
        #     #             }
        #     #
        #     #             websiteId_new = save_collection_website(collection_website, meta_new)
        #
        #
        #
        # if meta["httpcode"]==404:
        #     flag, domain = url_helper.get_domain(company["website"])
        #     meta_domain = collection_website.find_one({"domain": domain})
        #     if meta_domain is None or meta["httpcode"]==404:
        #         # if company["locationId"] is not None and company["locationId"]>370:
        #         #     num7+=1;continue
        #         logger.info("checking company: %s|%s website: %s", company["code"], company_id, company["website"])
        #         logger.info("*****************website is not available");num6+=1;cids.append(int(company_id))
        #         # collection_website.update_one({"_id":meta["_id"]},{'$set': {"websiteCheckTime": None}})
        #     else: num8+=1
        # else:num8+=1
        #


    logger.info("num:%s/%s/%s/%s/%s/%s/%s/%s",num1,num2, num3,num4, num5, num6,num7, num8)

    logger.info(cids)


