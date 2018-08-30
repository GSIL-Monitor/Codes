# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import traceback
from kafka import (KafkaClient, KafkaConsumer, SimpleProducer)
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, db, config, util, url_helper, name_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

#logger
loghelper.init_logger("corporate_track", stream=True)
logger = loghelper.get_logger("corporate_track")

itunesDomainEx = ["baidu.com","hao123.com","appzg.org"]



# kafka
kafkaConsumer = None
kafkaProducer = None

def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("validator_company", group_id="bamy2",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')

def update_domain(domain, row_id):
    conn = db.connect_torndb()
    sql = "update artifact set domain=%s where id=%s"
    conn.update(sql, domain, row_id)
    conn.close()


def set_active(table, active_value, row_id):
    conn = db.connect_torndb()
    sql = "update " + table + " set active=%s where id=%s"
    conn.update(sql, active_value, row_id)
    conn.close()

def save_beian_artifacts(items, companyId):
    conn = db.connect_torndb()
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        homepage = "http://www." + item["domain"]
        ###############################? only check domain? if there is no domain
        artifact = conn.get("select * from artifact where type=4010 and companyId=%s and link=%s limit 1",
                                       companyId, homepage)
        if artifact is None:
            artifact = conn.get("select * from source_artifact where type=4010 and companyId=%s and domain=%s limit 1",
                                companyId, item["domain"])

        type = 4010

        if artifact is None:
            sql = "insert artifact(companyId, name, link, type, domain, createTime,modifyTime) \
                              values(%s,%s,%s,%s,%s,now(),now())"
            conn.insert(sql, companyId, item["websiteName"], homepage, type, item["domain"])

    conn.close()



def save_itunes_artifact(app, companyId):
    conn = db.connect_torndb()
    type = 4040
    try:
        sql = "insert artifact(companyId, name, description, link, domain, type, createTime,modifyTime) \
                          values(%s,%s,%s,%s,%s,%s,now(),now())"
        artifact_id = conn.insert(sql, companyId, app["trackName"], app["description"],app["trackViewUrl"], app["trackId"], type)
    except:
        artifact_id=None
    conn.close()
    return artifact_id


#here should be all artifacts under companyId
def find_itunesId(itunesId, companyId):

    conn = db.connect_torndb()
    artifacts = conn.query("select * from artifact where companyId=%s and type=4040", companyId)
    conn.close()
    #Check if itunesId is already existed in artifacts
    for artifact in artifacts:

        trackid = None
        if artifact["domain"] is None:
            (apptype, appmarket, trackid) = url_helper.get_market(artifact["link"])
            if apptype != 4040:
                continue

        else:
            try:
                trackid = int(artifact["domain"])
            except:
                pass

        if trackid == itunesId:
            return True
    return False



def save_android_artifact(app, companyId):
    conn = db.connect_torndb()
    type = 4050
    sql = "insert artifact(companyId, name, description, link, domain, type, createTime,modifyTime) \
                          values(%s,%s,%s,%s,%s,%s,now(),now())"
    try:
        artifact_id = conn.insert(sql, companyId, app["name"], app["description"], app["link"], app["apkname"], type)
    except Exception,e:
        logger.info("here")
        logger.info(e)
        artifact_id = None
    conn.close()
    return artifact_id

#here should be all artifacts under companyId
def find_androidAppname(androidApk, companyId):
    # mongo
    mongo = db.connect_mongo()
    collection_android_market = mongo.market.android_market

    if androidApk is None or androidApk.strip() == "":
        mongo.close()
        return True

    conn = db.connect_torndb()
    artifacts = conn.query("select * from artifact where companyId=%s and type=4050", companyId)
    conn.close()

    #Check if apkname is already existed in artifacts
    for artifact in artifacts:

        apkname = None
        if artifact["domain"] is None:
            (apptype, appmarket, appid) = url_helper.get_market(artifact["link"])
            if apptype != 4050:
                continue
            # Get apkname of baidu and 360 from android market
            if appmarket == 16010 or appmarket == 16020:
                android_app = collection_android_market.find_one({"appmarket": appmarket, "key_int": appid})
                if android_app:
                    apkname = android_app["apkname"]
            else:
                apkname = appid
        else:
            apkname = artifact["domain"]
        #logger.info(apkname)
        if apkname == androidApk:
            mongo.close()
            return True
    mongo.close()
    return False


def count_company_names(apps, item_of_name):
    names = {}
    for app in apps:
        company_name = app.get(item_of_name)
        if company_name is not None:
            ischinese, iscompany = name_helper.name_check(company_name)
            if iscompany == True:
                names[company_name] = 1
    return len(names)

def count_domains(apps, item_of_url):
    domains = {}
    for app in apps:
        url = app.get(item_of_url)
        flag, domain = url_helper.get_domain(url)
        if flag is not None and domain is not None:
            domains[domain] = 1
    return len(domains)


def expand(company_id):
        # mongo
        mongo = db.connect_mongo()
        # create index?
        # collection = mongo.crawler_v3.projectdata

        collection_itunes = mongo.market.itunes
        collection_beian = mongo.info.beian
        collection_android = mongo.market.android
        collection_android_market = mongo.market.android_market

        logger.info("Company id: %s Start app check!!!", company_id)

        conn = db.connect_torndb()
        company_names = conn.query("select * from corporate_alias where corporateId in (select corporateId from "
                                   "company where id=%s) and (active is null or active='Y')", company_id)
        artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')", company_id)
        logger.info(json.dumps(company_names, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))
        conn.close()

        # Step A/1:按公司名,备案查询
        logger.info("%s 按公司名备案查询", company_id)
        for company_name in company_names:
            # Only check chinese company name
            if company_name["name"] is None or company_name["name"].strip() == "":
                continue
            (chinese, companyName) = name_helper.name_check(company_name["name"])

            if chinese != "Y":
                continue

            check_names = list(collection_beian.find({"organizer": company_name["name"]}))

            if len(check_names) > 0:

                save_beian_artifacts(check_names,  company_id)  # insert website/homepage into Mysql.artifact

        #itunes扩展
        #Step B/2根据公司名查询更多的itunes artifact
        logger.info("%s 根据公司名查询更多的itunes artifact", company_id)
        for company_name in company_names:

            if company_name["name"] is None or company_name["name"].strip() == "":
                continue

            check_itunes_sellers = list(collection_itunes.find({"sellerName": company_name["name"]}))
            logger.info("**********%s find %s", company_name["name"], len(check_itunes_sellers))
            if len(check_itunes_sellers) > 0:
                #lens_domain = count_domains(check_itunes_sellers, "sellerUrl")

                for app in check_itunes_sellers:
                    logger.info("**********%s find %s,%s", company_name["name"], app["trackName"], app["trackId"])
                    # Check if itunesId is already existed in all artifacts in 1 CompanyId
                    if find_itunesId(app["trackId"], company_id):
                        pass
                    else:
                        save_itunes_artifact(app, company_id)

        #Step B/3根据域名查询更多的itunes artifact
        logger.info("%s 根据域名查询更多的itunes artifact", company_id)
        for artifact in artifacts:
            if artifact["type"] != 4010:
                continue

            if artifact["domain"] is None:
                (flag, domain) = url_helper.get_domain(artifact["link"])
                if flag is None:
                    continue
                if flag is False:
                    continue
                update_domain(domain, artifact["id"])
            else:
                domain =artifact["domain"]

            if domain is None or domain.strip() == "":
                continue

            if domain in itunesDomainEx:
                continue

            check_itunes_sellerDomains = list(collection_itunes.find({"sellerDomain": domain}))
            logger.info("**********%s find %s", domain, len(check_itunes_sellerDomains))
            if len(check_itunes_sellerDomains) > 0:

                #lens_company_names = count_company_names(check_itunes_sellerDomains, "sellerName")

                for app in check_itunes_sellerDomains:
                    logger.info("**********%s find %s, %s", domain, app["trackName"], app["trackId"])
                    # Check if itunesId is already existed in all artifacts in 1 CompanyId
                    if find_itunesId(app["trackId"], company_id):
                        pass
                    else:
                        save_itunes_artifact(app, company_id)

            check_itunes_supportDomains = list(collection_itunes.find({"supportDomain": domain}))
            logger.info("**********%s find %s", domain, len(check_itunes_supportDomains))
            if len(check_itunes_supportDomains) > 0 and len(check_itunes_supportDomains) < 100:

                #lens_company_names = count_company_names(check_itunes_supportDomains, "sellerName")

                for app in check_itunes_supportDomains:
                    logger.info("**********%s find %s, %s", domain, app["trackName"], app["trackId"])
                    # Check if itunesId is already existed in all artifacts in 1 CompanyId
                    if find_itunesId(app["trackId"], company_id):
                        pass
                    else:
                        save_itunes_artifact(app, company_id)


        #android扩展

        #Step C/2根据公司名查询更多的android artifact
        logger.info("%s 根据公司名查询更多的android artifact", company_id)
        for company_name in company_names:
            # producer name
            if company_name["name"] is None or company_name["name"].strip() == "":
                continue

            check_android_authors = list(collection_android.find({"author": company_name["name"]}))
            logger.info("**********%s find %s", company_name["name"], len(check_android_authors))
            if len(check_android_authors) > 0 and len(check_android_authors) < 100:

                #lens_domain = count_domains(check_android_authors, "website")

                #check if author is consistent
                for app in check_android_authors:
                    logger.info("**********%s find %s, %s", company_name["name"], app["name"], app["apkname"])
                    # Check if AnId existed
                    if find_androidAppname(app["apkname"], company_id):
                        pass
                    else:
                        save_android_artifact(app, company_id)

        #Step C/3根据域名查询更多的android artifact
        logger.info("%s 根据域名查询更多的android artifact", company_id)
        for artifact in artifacts:
            if artifact["type"] != 4010:
                continue

            if artifact["domain"] is None:
                (flag, domain) = url_helper.get_domain(artifact["link"])
                if flag is None:
                    continue
                if flag is False:
                    continue
                update_domain(domain, artifact["id"])
            else:
                domain = artifact["domain"]

            if domain is None or domain.strip() == "":
                continue

            check_android_websiteDomains = list(collection_android.find({"website_domain": domain}))
            logger.info("**********%s find %s", domain, len(check_android_websiteDomains))
            if len(check_android_websiteDomains) > 0:

                #lens_company_names = count_company_names(check_android_websiteDomains, "author")

                for app in check_android_websiteDomains:
                    logger.info("**********%s find %s, %s", domain, app["name"], app["apkname"])
                    # Check if AndroidId is already existed in artifacts
                    if find_androidAppname(app["apkname"], company_id):
                        pass
                    else:
                        save_android_artifact(app, company_id)

            check_android_apknameDomains= list(collection_android.find({"apkname_domain": domain}))
            logger.info("**********%s find %s", domain, len(check_android_apknameDomains))
            #add threshold to avoid case: domain: com.wowotuan
            if len(check_android_apknameDomains) > 0 and len(check_android_apknameDomains) < 100:

                #lens_company_names = count_company_names(check_android_apknameDomains, "author")

                for app in check_android_apknameDomains:
                    logger.info("**********%s find %s, %s", domain, app["name"], app["apkname"])
                    # Check if AndroidId is already existed in artifacts
                    if find_androidAppname(app["apkname"], company_id):
                        pass
                    else:
                        save_android_artifact(app, company_id)

        mongo.close()


def update(cid,name):
    mongo = db.connect_mongo()
    collection_name = mongo.info.gongshang_name
    gname = collection_name.find_one({"name": name})
    if gname is None:
        collection_name.insert({"name": name, "type": 3, "lastCheckTime": None,
                                        "corporateIds": [int(cid)]})
    else:
        collection_name.update_one({"name": name}, {'$set': {"lastCheckTime": None}})
    mongo.close()

def expand_corp(corporate_id,name):
    update(corporate_id,name)
    conn = db.connect_torndb()
    companies = conn.query("select * from company where (active is null or active !='N') and corporateId=%s",corporate_id)
    for company in companies:
        expand(company["id"])
    conn.close()

# return companyid list
if __name__ == "__main__":

    init_kafka()
    while True:
        try:
            logger.info("start")
            # logger.info(kafkaConsumer)
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    # msg: type:XXXX, name :xxxx
                    logger.info(json.dumps(msg, ensure_ascii=False, cls=util.CJsonEncoder))
                    if msg["action"] == "create":
                        logger.info("handle -> %s", msg["id"])
                        expand_corp(msg["id"],msg["name"])
                        kafkaConsumer.commit()
                        # exit(0)
                    else:
                        # pass
                        kafkaConsumer.commit()
                except Exception, e:

                    traceback.print_exc()
                # break
        except KeyboardInterrupt:
            logger.info("break1")
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()
        break
