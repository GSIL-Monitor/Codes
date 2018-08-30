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
import config
import db
import loghelper
import url_helper
import name_helper
import util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian'))
import icp_chinaz
import beian_links

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/goshang'))
import qixinbao

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/website'))
import website

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/screenshot'))
import screenshot_website


#logger
loghelper.init_logger("company_expand", stream=True)
logger = loghelper.get_logger("company_expand")

#mongo
mongo = db.connect_mongo()
#create index?
#collection = mongo.crawler_v3.projectdata
collection_beian = mongo.info.beian

collection_main_beianhao = mongo.info.main_beianhao

collection_itunes = mongo.market.itunes

collection_android = mongo.market.android
collection_android_market = mongo.market.android_market

collection_goshang = mongo.info.gongshang

collection_website = mongo.info.website

COMPANIES=[]

#exception
itunesDomainEx = ["baidu.com","hao123.com","appzg.org"]

def save_collection_beian(collection_name, items):
    for item in items:
        #logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))
        if collection_name.find_one({"domain": item["domain"]}) is not None:
            collection_name.delete_one({"domain": item["domain"]})
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        collection_name.insert_one(item)

def save_collection_mainBeianhao(collection_name, items):
    for item in items:
        if collection_name.find_one({"mainBeianhao": item["mainBeianhao"]}) is None:
            item["createTime"] = datetime.datetime.now()
            item["modifyTime"] = item["createTime"]
            collection_name.insert_one(item)

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

def screenshot_wesbite(collection_name, websiteId, screenshot_crawler):
    dest = "jpeg/"
    website = collection_name.find_one({"_id": websiteId})
    if website is not None and not website.has_key("screenshotTime") and website.has_key("httpcode") and website["httpcode"] ==200:
        logger.info("%s need to do screenshot", website["redirect_url"])
        url = website["redirect_url"]
        id = str(website["_id"])
        screenshot_crawler.run(url, id, dest, timeout=30)
        screenshotId = None

        jpgfile = dest + id + '.jpg'
        if os.path.isfile(jpgfile):
            size = os.path.getsize(jpgfile)
            if size > 0:
                screenshotId = screenshot_crawler.save(jpgfile, id)
            os.remove(jpgfile)

        screenshotTime = datetime.datetime.now()
        collection_name.update_one({"_id": website["_id"]},{"$set": {"screenshotTime": screenshotTime, "screenshotId": screenshotId}})
        logger.info("%s screenshot finished", website["redirect_url"])



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


def merge_beian(items1, items2):
    items = []
    for item1 in items1:
        items.append(item1)

    for item2 in items2:
        new = True
        domain = item2["domain"]
        #Check if domain listed items1ç
        for item in items:
            if item["domain"] == domain:
                new = False
        if new:
            items.append(item2)
    return items

def set_active(table, active_value, row_id):
    conn = db.connect_torndb()
    sql = "update " + table + " set active=%s where id=%s"
    conn.update(sql, active_value, row_id)
    conn.close()

def set_expanded(table, verify_value, row_id):
    conn = db.connect_torndb()
    sql = "update " + table + " set expanded=%s where id=%s"
    conn.update(sql, verify_value, row_id)
    conn.close()

def save_beian_artifacts(items, sourceCompanyId):
    conn = db.connect_torndb()
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        homepage = "http://www." + item["domain"]
        ###############################? only check domain? if there is no domain
        source_artifact = conn.get("select * from source_artifact where type=4010 and sourceCompanyId=%s and link=%s limit 1",
                                       sourceCompanyId, homepage)
        if source_artifact is None:
            source_artifact = conn.get("select * from source_artifact where type=4010 and sourceCompanyId=%s and domain=%s limit 1",
                sourceCompanyId, item["domain"])

        type = 4010
        extended = "Y"
        if source_artifact is None:
            sql = "insert source_artifact(sourceCompanyId, name, link, type, domain, extended, createTime,modifyTime) \
                              values(%s,%s,%s,%s,%s,%s,now(),now())"
            conn.insert(sql, sourceCompanyId, item["websiteName"], homepage, type, item["domain"], extended)
        #Not update data existed
        #else:
            #sql = "update source_artifact set link=%s where id=%s"
            #conn.update(sql, item["homepage"], source_artifact["id"])
    conn.close()


def save_website_artifact(website, sourceCompanyId):
    conn = db.connect_torndb()
    if not find_link(website["url"], sourceCompanyId):
        try:
            sql = "insert source_artifact(sourceCompanyId, name, link, type, domain, extended, createTime,modifyTime) \
                              values(%s,%s,%s,%s,%s,%s,now(),now())"
            conn.insert(sql, sourceCompanyId, website["title"], website["url"], 4010, website["domain"], 'Y')
        except:
            pass
    conn.close()


def save_beian_mainbeianhaos(items, sourceCompanyId):
    conn = db.connect_torndb()
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        source_mainbeianhao = conn.get("select * from source_mainbeianhao where sourceCompanyId=%s and mainBeianhao=%s",
                                       sourceCompanyId, item["mainBeianhao"])
        if source_mainbeianhao is None:
            sql = "insert source_mainbeianhao(sourceCompanyId, mainBeianhao, createTime,modifyTime) \
                              values(%s,%s,now(),now())"
            conn.insert(sql, sourceCompanyId, item["mainBeianhao"])

    conn.close()


def save_beian_company_names(items, sourceCompanyId):
    conn = db.connect_torndb()
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        if item["organizerType"] != "企业":
            continue

        company_name = name_helper.company_name_normalize(item["organizer"])
        source_company_name = conn.get("select * from source_company_name where sourceCompanyId=%s and name=%s limit 1",
                                       sourceCompanyId, company_name)
        if source_company_name is None:
            sql = "insert source_company_name(sourceCompanyId, name, chinese, type, extended, createTime,modifyTime) \
                              values(%s,%s,%s,12010, %s,now(),now())"
            conn.insert(sql, sourceCompanyId, company_name, 'Y','Y')
    conn.close()


def copy_from_itunes(app, sourceArtifactId):
    conn = db.connect_torndb()
    if app.has_key("description"):
        sql = "update source_artifact set name=%s, description=%s, link=%s, domain=%s, modifyTime=now() where id=%s"
        conn.update(sql, app["trackName"], app["description"], app["trackViewUrl"], app["trackId"], sourceArtifactId)
    else:
        sql = "update source_artifact set name=%s, link=%s, domain=%s, modifyTime=now() where id=%s"
        conn.update(sql, app["trackName"], app["trackViewUrl"], app["trackId"], sourceArtifactId)
    conn.close()


def save_itunes_artifact(app, sourceCompanyId):
    conn = db.connect_torndb()
    type = 4040
    try:
        sql = "insert source_artifact(sourceCompanyId, name, description, link, domain, type, createTime,modifyTime,extended) \
                          values(%s,%s,%s,%s,%s,%s,now(),now(),'Y')"
        source_artifact_id = conn.insert(sql, sourceCompanyId, app["trackName"], app["description"],app["trackViewUrl"], app["trackId"], type)
    except:
        source_artifact_id=None
    conn.close()
    return source_artifact_id


#here should be all artifacts under sourceCompanyId
def find_itunesId(itunesId, sourceCompanyId):

    conn = db.connect_torndb()
    artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s and type=4040",sourceCompanyId)
    conn.close()
    #Check if itunesId is already existed in artifacts
    for artifact in artifacts:
        #if artifact["type"] != 4040:
        #    continue

        #Get trackid
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

def copy_from_android(app, sourceArtifactId):
    conn = db.connect_torndb()
    sql = "update source_artifact set name=%s, description=%s, domain=%s, link=%s, modifyTime=now() where id=%s"
    conn.update(sql, app["name"], app["description"], app["apkname"], app["link"], sourceArtifactId)
    conn.close()


def save_android_artifact(app, sourceCompanyId):
    conn = db.connect_torndb()
    type = 4050
    sql = "insert source_artifact(sourceCompanyId, name, description, link, domain, type, createTime,modifyTime,extended) \
                          values(%s,%s,%s,%s,%s,%s,now(),now(),'Y')"
    source_artifact_id = conn.insert(sql, sourceCompanyId, app["name"], app["description"], app["link"], app["apkname"], type)
    conn.close()
    return source_artifact_id

def save_company_name(app, item_of_name, sourceCompanyId):
    conn = db.connect_torndb()
    company_name = app[item_of_name]
    if company_name is None or company_name.strip() == "":
        conn.close()
        return

    company_name = name_helper.company_name_normalize(company_name)
    source_company_name = conn.get("select * from source_company_name where sourceCompanyId=%s and name=%s limit 1",
                                       sourceCompanyId, company_name)
    if source_company_name is None:
        (chinese, company) = name_helper.name_check(app[item_of_name])
        if chinese is True:
            chinese_type = "Y"
        else:
            chinese_type = "N"

        sql = "insert source_company_name(sourceCompanyId, name, chinese, type, extended, createTime,modifyTime) \
                              values(%s,%s,%s, 12010, %s,now(),now())"
        conn.insert(sql, sourceCompanyId, company_name, chinese_type, 'Y')
    conn.close()

#here should be all artifacts under sourceCompanyId
def find_androidAppname(androidApk, sourceCompanyId):
    if androidApk is None or androidApk.strip() == "":
        return True

    conn = db.connect_torndb()
    artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s and type=4050", sourceCompanyId)
    conn.close()

    #Check if apkname is already existed in artifacts
    for artifact in artifacts:
        #if artifact["type"] != 4050:
        #    continue

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
            return True
    return False

def find_link(link, sourceCompanyId):
    if link is None:
        return True
    if link.strip() == "":
        return True

    conn = db.connect_torndb()
    artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=4010 and link=%s limit 1",sourceCompanyId, link)
    if artifact is None:
        flag, domain = url_helper.get_domain(link)
        if domain is not None:
            artifact = conn.get("select * from source_artifact where type=4010 and sourceCompanyId=%s and domain=%s limit 1", sourceCompanyId, domain)
    conn.close()
    if artifact is None:
        return False
    else:
        return True



def save_itunesSupportUrl_artifact(app, sourceCompanyId):
    url = app["supportUrl"]
    flag, domain = url_helper.get_domain(url)
    if flag is not True:
        return None

    if find_link(app["supportUrl"], sourceCompanyId):
        return None

    conn = db.connect_torndb()
    type = 4010
    try:
        sql = "insert source_artifact(sourceCompanyId, name, description, link, domain, type, createTime,modifyTime,extended) \
                          values(%s,%s,%s,%s,%s,%s,now(),now(),'Y')"
        source_artifact_id=conn.insert(sql, sourceCompanyId, app["sellerName"], app["description"], app["supportUrl"], app["supportDomain"], type)
    except:
        source_artifact_id=None
    conn.close()
    return source_artifact_id

def save_itunesSellerUrl_artifact(app, sourceCompanyId):
    url = app["sellerUrl"]
    flag, domain = url_helper.get_domain(url)
    if flag is not True:
        return None

    if find_link(app["sellerUrl"], sourceCompanyId):
        return None

    conn = db.connect_torndb()
    type = 4010
    try:
        sql = "insert source_artifact(sourceCompanyId, name, description, link, domain, type, createTime,modifyTime,extended) \
                          values(%s,%s,%s,%s,%s,%s,now(),now(),'Y')"
        source_artifact_id=conn.insert(sql, sourceCompanyId, app["sellerName"], app["description"], app["sellerUrl"], app["sellerDomain"], type)
    except:
        source_artifact_id = None
    conn.close()
    return source_artifact_id

def save_androidWebsite_artifact(app, sourceCompanyId):
    url = app["website"]
    flag, domain = url_helper.get_domain(url)
    if flag is not True:
        return None
    if find_link(url, sourceCompanyId):
        return None

    conn = db.connect_torndb()
    type = 4010
    try:
        sql = "insert source_artifact(sourceCompanyId, name, description, link, domain, type, createTime,modifyTime,extended) \
                          values(%s,%s,%s,%s,%s,%s,now(),now(),'Y')"
        source_artifact_id=conn.insert(sql, sourceCompanyId, app["name"], app["description"], app["website"], app["website_domain"], type)
    except:
        source_artifact_id = None
    conn.close()
    return source_artifact_id

def filter_domain(items, domain):
    items_new = []
    for item in items:
        if item["domain"] == domain:
            items_new.append(item)

    return items_new

def check_source_artifact(sourceCompanyId):
    conn = db.connect_torndb()
    artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=4010 and (verify='Y' or verify is null) limit 1",sourceCompanyId)
    conn.close()
    if artifact is None:
        return False
    else:
        return True

def check_source_company_name(sourceCompanyId):
    conn = db.connect_torndb()
    company_name = conn.get("select * from source_company_name where sourceCompanyId=%s and type=12010 and (verify='Y' or verify is null) limit 1",sourceCompanyId)
    conn.close()
    if company_name is None:
        return False
    else:
        return True


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

'''
def save_artifact_itunes_rel(itunesId, sourceArtifactId):
    source_artifact_itunes_rel = conn.get("select * from source_artifact_itunes_rel where \
                itunesId=%s and sourceArtifactId=%s", itunesId, sourceArtifactId)

    if source_artifact_itunes_rel is None:
        conn.insert("insert source_artifact_itunes_rel(itunesId, sourceArtifactId, createTime,modifyTime) \
                values(%s,%s, now(),now())",itunesId, sourceArtifactId)

def save_artifact_android_rel(androidId, sourceArtifactId):
    source_artifact_android_rel = conn.get("select * from source_artifact_android_rel where \
                androidId=%s and sourceArtifactId=%s", androidId, sourceArtifactId)

    if source_artifact_android_rel is None:
        conn.insert("insert source_artifact_android_rel(androidId, sourceArtifactId, createTime,modifyTime) \
                values(%s,%s, now(),now())",androidId, sourceArtifactId)

def save_company_goshang_rel(goshangBaseId, sourceComanyId):
    source_company_goshang_rel = conn.get("select * from source_company_goshang_rel where \
                goshangBaseId=%s and sourceComanyId=%s", goshangBaseId, sourceComanyId)

    if source_company_goshang_rel is None:
        conn.insert("insert source_company_goshang_rel(goshangBaseId, sourceComanyId, createTime,modifyTime) \
                values(%s,%s, now(),now())",goshangBaseId, sourceComanyId)

def save_artifact_website_rel(websiteId, sourceArtifactId):
    source_artifact_website_rel = conn.get("select * from source_artifact_website where \
                websiteId=%s and sourceArtifactId=%s", websiteId, sourceArtifactId)

    if source_artifact_website_rel is None:
        conn.insert("insert source_artifact_website_rel(websiteId, sourceArifactId, createTime,modifyTime) \
                values(%s,%s, now(),now())",goshangBaseId, sourceArtifactId)
'''

def expand_source_company(source_company_id, beian_links_crawler, icp_chinaz_crawler, screenshot_crawler, test=False):
    logger.info("Company id: %s Start expand!!!", source_company_id)
    logger.info("clean old expanded data")
    conn = db.connect_torndb()
    conn.execute("delete from source_company_name where sourceCompanyId=%s and extended is not null and (verify='Y' or verify is null)", source_company_id)
    conn.execute("delete from source_mainbeianhao where sourceCompanyId=%s and (verify='Y' or verify is null)", source_company_id)
    conn.execute("delete from source_artifact where sourceCompanyId=%s and extended is not null and (verify='Y' or verify is null)", source_company_id)
    conn.update("update source_artifact set expanded=null where sourceCompanyId=%s and (verify='Y' or verify is null)",
                source_company_id)
    conn.update("update source_company_name set expanded=null where sourceCompanyId=%s and (verify='Y' or verify is null)",
                source_company_id)

    # add fullname into source_company_name
    sourcecompany = conn.get("select * from source_company where id=%s", source_company_id)

    company_fullname = sourcecompany["fullName"]
    if company_fullname is not None and company_fullname.strip() != "":
        company_fullname = name_helper.company_name_normalize(company_fullname)

        check_fullname = conn.get("select * from source_company_name where sourceCompanyId=%s and name=%s limit 1",source_company_id, company_fullname)
        if check_fullname is None:
            (chinese, company) = name_helper.name_check(company_fullname)
            if chinese is True:
                chinese_type = "Y"
            else:
                chinese_type = "N"
            sql = "insert source_company_name(sourceCompanyId, name, chinese, type, createTime,modifyTime) \
                                  values(%s,%s,%s, 12010, now(),now())"
            conn.insert(sql, source_company_id, company_fullname, chinese_type)


    conn.close()

    round = 1
    # logger.info("Company Id: %s", source_company_id)
    while True:
        if round >= 6:
            conn = db.connect_torndb()
            conn.update("update source_company set processStatus=1 where id=%s", source_company_id)
            conn.close()
            break

        # Get main_beianhaos, source_company_names and artifacts for 1 company_id from Mysql.source_mainbeianhao, Mysql.source_artifacts and Mysql.source_company_name
        conn = db.connect_torndb()
        source_company_names = conn.query("select * from source_company_name where sourceCompanyId=%s and type=12010 and expanded is null and (verify='Y' or verify is null)", source_company_id)
        artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s and expanded is null and (verify='Y' or verify is null)", source_company_id)
        main_beianhaos = conn.query("select * from source_mainbeianhao where sourceCompanyId=%s and expanded is null and (verify='Y' or verify is null)", source_company_id)
        logger.info(json.dumps(source_company_names, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(main_beianhaos, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))
        conn.close()

        # Check if there are new stuff which need to do expansion
        if len(source_company_names) == 0 and len(artifacts) == 0 and len(main_beianhaos) == 0:
            conn = db.connect_torndb()
            conn.update("update source_company set processStatus=1 where id=%s", source_company_id)
            conn.close()
            break

        logger.info("Company id: %s expand for round %d", source_company_id, round)

        # Step A/1:按公司名,备案查询
        logger.info("%s 按公司名备案查询", source_company_id)
        for source_company_name in source_company_names:
            # Only check chinese company name
            if source_company_name["name"] is None or source_company_name["name"].strip() == "":
                continue

            if source_company_name["chinese"] is None:
                (chinese, companyName) = name_helper.name_check(source_company_name["name"])
            else:
                chinese = source_company_name["chinese"]

            if chinese != "Y":
                continue

            check_name = collection_beian.find_one({"organizer": source_company_name["name"]})
            # Case that one company_name has multiple beian# : 上海汇翼->(today.ai/teambition.com)#If only one found in Mongo.beian(organizer) it is fine
            if check_name is None:
                if test:
                    items_beianlinks = []
                else:
                    items_beianlinks = beian_links_crawler.query_by_company_name(source_company_name["name"])
                    save_collection_beian(collection_beian, items_beianlinks)  # insert infos into Mongo.beian
            else:
                items_beianlinks = [check_name]
            save_beian_artifacts(items_beianlinks,
                                 source_company_id)  # insert website/homepage into Mysql.source_artifact
            save_beian_company_names(items_beianlinks,
                                     source_company_id)  # insert organizer into Mysql.source_company_names
            save_beian_mainbeianhaos(items_beianlinks,
                                     source_company_id)  # insert mainBeianhao into Mysql.source_mainbeiahao

            # beian
            # 发现更多的artifact(website)和公司名,主备案号

        # Step A/2:按domian,备案查询
        logger.info("%s 按domian备案查询", source_company_id)
        for artifact in artifacts:
            # Only check is artifact is a website
            if artifact["type"] != 4010:
                continue
            if artifact["domain"] is None:
                link = url_helper.url_normalize(artifact["link"])
                (flag, domain) = url_helper.get_domain(link)
                if flag is None:
                    continue
                if flag is False:
                    continue
            else:
                domain = artifact["domain"]

            if domain is None or domain.strip() == "":
                continue

            check_domain = collection_beian.find_one({"domain": domain})

            if check_domain is None:
                if test:
                    items_merge =[]
                else:
                    items_beianlinks = beian_links_crawler.query_by_domain(domain)
                    items_icpchinaz = icp_chinaz_crawler.query_by_domain(domain)
                    items_merge = merge_beian(items_beianlinks, items_icpchinaz)

                    save_collection_beian(collection_beian, items_merge)  # insert infos into Mongo.beian
            else:
                items_merge = [check_domain]

            # filer by check domain to avoid sinaapp.cn case
            items_merge = filter_domain(items_merge, domain)

            save_beian_artifacts(items_merge, source_company_id)  # insert website/homepage into Mysql.source_artifact
            save_beian_company_names(items_merge, source_company_id)  # insert organizer into Mysql.source_company_names
            save_beian_mainbeianhaos(items_merge,
                                     source_company_id)  # insert mainBeianhao into Mysql.source_mainbeiahao

            # beian
            # 发现更多的artifact(website)和公司名,主备案号

        # Step A/3 #按主备案号查询
        logger.info("%s 按主备案号查询", source_company_id)
        for main_beianhao in main_beianhaos:
            mainBeianhao = main_beianhao["mainBeianhao"]
            check_mainBeianhao = collection_main_beianhao.find_one({"mainBeianhao": mainBeianhao})

            if check_mainBeianhao is None:
                if test:
                    items_merge =[]
                else:
                    items_beianlinks = beian_links_crawler.query_by_main_beianhao(mainBeianhao)
                    items_icpchinaz = icp_chinaz_crawler.query_by_main_beianhao(mainBeianhao)
                    items_merge = merge_beian(items_beianlinks, items_icpchinaz)

                    save_collection_beian(collection_beian, items_merge)  # insert infos into Mongo.beian
                # if mainBeianhao could be found in two links
                if len(items_merge) > 0:
                    items_main_beianhao = [{"mainBeianhao": mainBeianhao}]
                    save_collection_mainBeianhao(collection_main_beianhao,
                                                 items_main_beianhao)  # insert mainBeianhao into Mongo.main_beianhao
            else:
                items_merge = list(collection_beian.find({"mainBeianhao": mainBeianhao}))

            save_beian_artifacts(items_merge, source_company_id)  # insert website/homepage into Mysql.source_artifact
            save_beian_company_names(items_merge, source_company_id)  # insert organizer into Mysql.source_company_names
            save_beian_mainbeianhaos(items_merge,
                                     source_company_id)  # insert mainBeianhao into Mysql.source_mainbeiahao
            # 发现更多的artifact(website)和公司名

        # itunes扩展
        # Step B/1 #查询itunes artifact
        logger.info("%s 查询itunes artifact", source_company_id)

        itunes_company_enames = {}
        app_by_name = {}

        for artifact in artifacts:
            if artifact["type"] != 4040:
                continue
            # Get trackid
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

            if trackid is not None:
                app = collection_itunes.find_one({"trackId": trackid})

                if app is None:
                    # mark it as Noactive
                    set_active("source_artifact", "N", artifact["id"])
                else:
                    copy_from_itunes(app, artifact["id"])  # 存在: copy from mongo.itunes
                    # save_artifact_itunes_rel(app["_id"],artifact["id"])
                    set_active("source_artifact", "Y", artifact["id"])

                    # chinese, is_company = name_helper.name_check(app["sellerName"])
                    # if chinese and is_company:
                    #     save_company_name(app, "sellerName", source_company_id)
                    #
                    english, is_company = name_helper.english_name_check(app["sellerName"])
                    if english and is_company:
                        itunes_company_enames["sellerName"] = 1
                        app_by_name = app
                        #     save_company_name(app, "sellerName", source_company_id)
            else:
                set_active("source_artifact", "N", artifact["id"])

                # save the only english name
        if len(itunes_company_enames) == 1:
            conn = db.connect_torndb()
            company_name = conn.get(
                "select * from source_company_name where sourceCompanyId=%s and type=12010 and chinese='N' limit 1",
                source_company_id)
            conn.close()
            if company_name is None:
                save_company_name(app_by_name, "sellerName", source_company_id)

        # Step B/2根据公司名查询更多的itunes artifact
        logger.info("%s 根据公司名查询更多的itunes artifact", source_company_id)
        for source_company_name in source_company_names:
            # producer name
            '''
            check_itunes_producers = list(collection_itunes.find({"developer": source_company_name["name"]}))
            if len(check_itunes_producers) > 0:
                for app in check_itunes_producers:
                    # Check if itunesId is already existed in artifacts
                    if find_itunesId(app["trackId"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_itunes_artifact(app, source_company_id)
                        #save_artifact_itunes_rel(app["_id"], source_artifact_id)
                    save_company_name(app, "developer", source_company_id)
            '''
            if source_company_name["name"] is None or source_company_name["name"].strip() == "":
                continue

            check_itunes_sellers = list(collection_itunes.find({"sellerName": source_company_name["name"]}))
            if len(check_itunes_sellers) > 0:
                '''
                domains = {}
                for app in check_itunes_sellers:
                    sellerUrl = app.get("sellerUrl")
                    flag ,domain = url_helper.get_domain(sellerUrl)
                    if flag is not None and domain is not None:
                        domains[domain] = 1
                '''
                lens_domain = count_domains(check_itunes_sellers, "sellerUrl")
                artifact_status = check_source_artifact(source_company_id)

                for app in check_itunes_sellers:
                    # Check if itunesId is already existed in all artifacts in 1 sourceCompanyId
                    if find_itunesId(app["trackId"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_itunes_artifact(app, source_company_id)

                        if app.has_key("sellerUrl"):
                            # if find_link(app["sellerUrl"], source_company_id) or check_source_artifact(source_company_id):
                            if artifact_status:
                                pass
                            elif lens_domain == 1:
                                artifact_id = save_itunesSellerUrl_artifact(app, source_company_id)

                                if artifact_id is not None:
                                    artifact_status = True

                            # comment due to incorrect expand
                            '''
                            if app.has_key("supportUrl"):
                                if find_link(app["supportUrl"], source_company_id):
                                    pass
                                else:
                                    save_itunesSupportUrl_artifact(app, source_company_id)
                            '''

                            # save_artifact_itunes_rel(app["_id"], source_artifact_id)
                            # save_company_name(app, "sellerName", source_company_id)

        # Step B/3根据域名查询更多的itunes artifact
        logger.info("%s 根据域名查询更多的itunes artifact", source_company_id)
        for artifact in artifacts:
            if artifact["type"] != 4010:
                continue

            if artifact["domain"] is None:
                (flag, domain) = url_helper.get_domain(artifact["link"])
                if flag is None:
                    continue
                if flag is False:
                    continue
            else:
                domain = artifact["domain"]

            if domain is None or domain.strip() == "":
                continue

            if domain in itunesDomainEx:
                continue

            check_itunes_sellerDomains = list(collection_itunes.find({"sellerDomain": domain}))
            if len(check_itunes_sellerDomains) > 0:

                lens_company_names = count_company_names(check_itunes_sellerDomains, "sellerName")
                company_name_status = check_source_company_name(source_company_id)

                for app in check_itunes_sellerDomains:

                    # Check if itunesId is already existed in all artifacts in 1 sourceCompanyId
                    if find_itunesId(app["trackId"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_itunes_artifact(app, source_company_id)

                    if company_name_status:
                        pass
                    elif lens_company_names == 1:

                        # save_artifact_itunes_rel(app["_id"], source_artifact_id)
                        chinese, is_company = name_helper.name_check(app["sellerName"])
                        if chinese and is_company:
                            save_company_name(app, "sellerName", source_company_id)
                            company_name_status = True

                        english, is_company = name_helper.english_name_check(app["sellerName"])
                        if english and is_company:
                            save_company_name(app, "sellerName", source_company_id)
                            company_name_status = True

            check_itunes_supportDomains = list(collection_itunes.find({"supportDomain": domain}))
            if len(check_itunes_supportDomains) > 0 and len(check_itunes_supportDomains) < 100:

                lens_company_names = count_company_names(check_itunes_supportDomains, "sellerName")
                company_name_status = check_source_company_name(source_company_id)

                for app in check_itunes_supportDomains:
                    # Check if itunesId is already existed in all artifacts in 1 sourceCompanyId
                    if find_itunesId(app["trackId"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_itunes_artifact(app, source_company_id)
                        # save_artifact_itunes_rel(app["_id"], source_artifact_id)
                    if company_name_status:
                        pass
                    elif lens_company_names == 1:
                        chinese, is_company = name_helper.name_check(app["sellerName"])
                        if chinese and is_company:
                            save_company_name(app, "sellerName", source_company_id)
                            company_name_status = True

                        english, is_company = name_helper.english_name_check(app["sellerName"])
                        if english and is_company:
                            save_company_name(app, "sellerName", source_company_id)
                            company_name_status = True

        # 发现更多的artifact(website)和公司名,check if existed in source_art..and company_name


        # android扩展
        # Step C/1#查询android artifact
        logger.info("%s 查询android artifact", source_company_id)
        for artifact in artifacts:
            if artifact["type"] != 4050:
                continue
            # Get apkname
            apkname = None
            if artifact["domain"] is None:
                (apptype, appmarket, appid) = url_helper.get_market(artifact["link"])
                # Get apkname of baidu and 360 from android market
                if apptype != 4050:
                    continue

                if appmarket == 16010 or appmarket == 16020:
                    android_app = collection_android_market.find_one({"appmarket": appmarket, "key_int": appid})
                    if android_app:
                        apkname = android_app["apkname"]
                else:
                    apkname = appid
            else:
                apkname = artifact["domain"]

            if apkname is not None:
                app = collection_android.find_one({"apkname": apkname})

                if app is None:
                    # mark it as Noactive
                    set_active("source_artifact", "N", artifact["id"])
                else:
                    copy_from_android(app, artifact["id"])  # 存在: copy from mongo.android
                    # save_artifact_android_rel(app["_id"], artifact["id"])
                    set_active("source_artifact", "Y", artifact["id"])

                    # chinese, is_company = name_helper.name_check(app["author"])
                    # if is_company:
                    #     save_company_name(app, "author", source_company_id)
            else:
                set_active("source_artifact", "N", artifact["id"])

        # Step C/2根据公司名查询更多的android artifact
        logger.info("%s 根据公司名查询更多的android artifact", source_company_id)
        for source_company_name in source_company_names:
            # producer name
            if source_company_name["name"] is None or source_company_name["name"].strip() == "":
                continue

            check_android_authors = list(collection_android.find({"author": source_company_name["name"]}))
            if len(check_android_authors) > 0 and len(check_android_authors) < 200:

                lens_domain = count_domains(check_android_authors, "website")
                artifact_status = check_source_artifact(source_company_id)

                # check if author is consistent
                for app in check_android_authors:
                    # Check if AnId have one 4010
                    if find_androidAppname(app["apkname"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_android_artifact(app, source_company_id)

                        if artifact_status:
                            pass
                        elif lens_domain == 1:
                            artifact_id = save_androidWebsite_artifact(app, source_company_id)

                            if artifact_id is not None:
                                artifact_status = True

                                # save_artifact_android_rel(app["_id"], source_artifact_id)
                                # save_company_name(app, "author", source_company_id)

        # Step C/3根据域名查询更多的android artifact
        logger.info("%s 根据域名查询更多的android artifact", source_company_id)
        for artifact in artifacts:
            if artifact["type"] != 4010:
                continue

            if artifact["domain"] is None:
                (flag, domain) = url_helper.get_domain(artifact["link"])
                if flag is None:
                    continue
                if flag is False:
                    continue
            else:
                domain = artifact["domain"]

            if domain is None or domain.strip() == "":
                continue

            check_android_websiteDomains = list(collection_android.find({"website_domain": domain}))
            if len(check_android_websiteDomains) > 0:

                lens_company_names = count_company_names(check_android_websiteDomains, "author")
                company_name_status = check_source_company_name(source_company_id)

                for app in check_android_websiteDomains:
                    # Check if AndroidId is already existed in artifacts
                    if find_androidAppname(app["apkname"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_android_artifact(app, source_company_id)
                        # save_artifact_android_rel(app["_id"], source_artifact_id)
                    if company_name_status:
                        pass
                    elif lens_company_names == 1:

                        chinese, is_company = name_helper.name_check(app["author"])
                        if is_company:
                            save_company_name(app, "author", source_company_id)
                            company_name_status = True

            check_android_apknameDomains = list(collection_android.find({"apkname_domain": domain}))
            # add threshold to avoid case: domain: com.wowotuan
            if len(check_android_apknameDomains) > 0 and len(check_android_apknameDomains) < 100:

                lens_company_names = count_company_names(check_android_apknameDomains, "author")
                company_name_status = check_source_company_name(source_company_id)

                for app in check_android_apknameDomains:
                    # Check if AndroidId is already existed in artifacts
                    if find_androidAppname(app["apkname"], source_company_id):
                        pass
                    else:
                        source_artifact_id = save_android_artifact(app, source_company_id)
                        # save_artifact_android_rel(app["_id"], source_artifact_id)
                    if company_name_status:
                        pass
                    elif lens_company_names == 1:

                        chinese, is_company = name_helper.name_check(app["author"])
                        if is_company:
                            save_company_name(app, "author", source_company_id)
                            company_name_status = True
        # 发现更多的artifact(website)和公司名


        # 工商查询
        logger.info("%s 工商查询", source_company_id)
        '''
        for source_company_name in source_company_names:
            if source_company_name["type"] != 12010 or source_company_name["chinese"] == 'N':
                continue

            check_goshang_name = collection_goshang.find_one({"name": source_company_name["name"]})
            if check_goshang_name is None:
                company_urls = qinxinbao_search_crawler.query_by_company(source_company_name["name"])
                #Get several urls for related companies, save all data into mongo
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
                    goshangBaseId = save_collection_goshang(collection_goshang, item_qixinbao)

                    #but only save exact 1 company into source_company_goshang_re
                    if item_qixinbao["name"] == source_company_name["name"]:
                        #save_company_goshang_rel(goshangBaseId, source_company_id)
                        pass
            else:
                pass
        '''
        # 曾用名 TODO

        # 清洗website artfiact
        # 查询meta信息, 标记不能访问的?website?, 处理转跳的website
        logger.info("%s website meta", source_company_id)
        for artifact in artifacts:
            if artifact["type"] != 4010:
                continue
            if artifact["link"] is None or artifact["link"].strip() == "":
                set_active("source_artifact", "N", artifact["id"])
                continue

            url = artifact["link"].strip()
            meta = collection_website.find_one({"url": url})
            # if meta is None or meta["httpcode"]==404:
            if meta is None:
                meta = website.get_meta_info(url)
                if meta:
                    websiteId = save_collection_website(collection_website, meta)
                    if websiteId is not None and not test:
                        #screenshot_wesbite(collection_website, websiteId, screenshot_crawler)
                        pass
                else:
                    meta = {
                        "url": artifact["link"],
                        "httpcode": 404
                    }
                    websiteId = save_collection_website(collection_website, meta)
                    set_active("source_artifact", "N", artifact["id"])

            if meta:
                # 发生转跳
                # logger.info(meta)
                if meta["httpcode"] == 200:
                    redirect_url = meta.get("redirect_url")
                    if artifact["link"] != redirect_url:
                        url = url_helper.url_normalize(meta["redirect_url"])
                        (flag_new, domain_new) = url_helper.get_domain(url)

                        meta_new = {
                            "url": url,
                            "domain": domain_new if flag_new is True else None,
                            "redirect_url": url,
                            "title": meta["title"],
                            "tags": meta["tags"],
                            "description": meta["description"],
                            "httpcode": 200

                        }

                        websiteId_new = save_collection_website(collection_website, meta_new)
                        if websiteId_new is not None and not test:
                            #screenshot_wesbite(collection_website, websiteId_new, screenshot_crawler)
                            pass

                        flag, domain = url_helper.get_domain(artifact["link"])
                        if domain_new != domain:  # 跳出原域名
                            set_active("source_artifact", "N", artifact["id"])
                        else:
                            if flag is True:  # 这是个'好'地址
                                set_active("source_artifact", "Y", artifact["id"])
                            else:
                                if flag_new is True:  # 转跳后是个 '好'地址
                                    set_active("source_artifact", "N", artifact["id"])
                                    save_website_artifact(meta_new, source_company_id)
                                else:
                                    set_active("source_artifact", "Y", artifact["id"])
                    else:
                        set_active("source_artifact", "Y", artifact["id"])
                elif meta["httpcode"] == 404:
                    set_active("source_artifact", "N", artifact["id"])

        # verify -> source_artifacts/source_company_name set verify
        logger.info("%s set verify", source_company_id)
        for artifact in artifacts:
            set_expanded("source_artifact", "Y", artifact["id"])
        for source_company_name in source_company_names:
            set_expanded("source_company_name", "Y", source_company_name["id"])
        for main_beianhao in main_beianhaos:
            set_expanded("source_mainbeianhao", "Y", main_beianhao["id"])

        round += 1

def expand():
    #init crawler
    beian_links_crawler = beian_links.BeianLinksCrawler()
    icp_chinaz_crawler = icp_chinaz.IcpchinazCrawler()
    screenshot_crawler = screenshot_website.phantomjsScreenshot()
    # qinxinbao_search_crawler = qixinbao.QixinbaoSearchCrawler()
    # qinxinbao_company_crawler = qixinbao.QixinbaoCompanyCrawler()

    while True:
        # gevent -> list of source_companies

        if len(COMPANIES) == 0:
            return
        source_company_id = COMPANIES.pop(0)

        expand_source_company(source_company_id, beian_links_crawler, icp_chinaz_crawler, screenshot_crawler)



def start_run(concurrent_num):
    while True:
        logger.info("Company expand start...")
        del COMPANIES[:]
        # 查询所有需要扩展的公司源
        conn = db.connect_torndb()
        source_companies = conn.query("select id from source_company where processStatus=0 and (active is null or active='Y') order by id")
        #source_companies = conn.query("select * from source_company where id=31098")
        conn.close()
        for source_company in source_companies:
            sourceCompanyId = source_company["id"]
            if sourceCompanyId is None:
                continue
            COMPANIES.append(sourceCompanyId)

        threads = [gevent.spawn(expand) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        #break
        logger.info("Company expand end.")

        if len(COMPANIES) == 0:
            gevent.sleep(1*60)

if __name__ == "__main__":
    start_run(5)