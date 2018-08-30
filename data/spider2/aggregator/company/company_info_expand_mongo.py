# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper
import url_helper
import name_helper
import util


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/website'))
import website

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

collection_source_company = mongo.source.company

COMPANIES=[]

#exception
itunesDomainEx = ["baidu.com","hao123.com","appzg.org"]

source_artifact_columns = {
    "name":             None,
    "description":      None,
    "link":             None,
    "domain":           None,
    "type":             None,
    "verify":           None,
    "active":           None,
    "createTime":       "now",
    "modifyTime":       "now",
    "rank":             None,
    "rankDate":         None,
    "extended":         None,
    "expanded":         None
}

source_company_name_columns = {
    "type":             None,
    "name":             None,
    "verify":           None,
    "chinese":          None,
    "createTime":       "now",
    "modifyTime":       "now",
    "extended":         None,
    "expanded":         None
}

source_mainbeianhao_columns = {
    "mainBeianhao":     None,
    "verify":           None,
    "createTime":       "now",
    "modifyTime":       "now",
    "expanded":         None
}

def populate_column(item, columns):
    item_new = {}
    for column in columns:
        if item.has_key(column) is True:
            item_new[column] = item[column]
        else:
            item_new[column] = columns[column]

        if item_new[column] == "now":
            item_new[column] = datetime.datetime.now()
    return item_new

def save_mongo_source_artifact(source, sourceId, sadata):
    item = populate_column(sadata, source_artifact_columns)
    record = collection_source_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        collection_source_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_artifact": item}})

def save_mongo_source_company_name(source, sourceId, scndata):
    item = populate_column(scndata, source_company_name_columns)
    record = collection_source_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        collection_source_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_company_name": item}})

def save_mongo_source_mainbeianhao(source, sourceId, smdata):
    item = populate_column(smdata, source_mainbeianhao_columns)
    record = collection_source_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        collection_source_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_mainbeianhao": item}})

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

def set_artifact_active(artifact, active_value, source, sourceId):
    # Now artifactStatus is new symbol to mark artifact status, not "active" anymore
    if active_value == 'N':
        artifactStatus = 11
    elif active_value == "Offline" or active_value == "Redirect":
        artifactStatus = 12
    else:
        artifactStatus = 13

    collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_artifact": {
        "$elemMatch": {"type": artifact["type"], "domain": artifact["domain"], "name": artifact["name"], "link": artifact["link"]}}}, {
        '$set': {"source_artifact.$.artifactStatus": artifactStatus}})

def set_artifact_expand(artifact, source, sourceId):
    collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_artifact": {
        "$elemMatch": {"type": artifact["type"], "domain": artifact["domain"], "name": artifact["name"],"link": artifact["link"]}}}, {
        '$set': {"source_artifact.$.expanded": "Y"}})

def set_scname_expand(scname, source, sourceId):
    collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_company_name": {
        "$elemMatch": {"type": scname["type"], "name": scname["name"]}}}, {
        '$set': {"source_company_name.$.expanded": "Y"}})

def set_scbeianhao_expand(scbeianhao, source, sourceId):
    collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_mainbeianhao": {
        "$elemMatch": {"mainBeianhao": scbeianhao["mainBeianhao"]}}}, {
        '$set': {"source_mainbeianhao.$.expanded": "Y"}})

def save_beian_artifacts(items, source, sourceId):
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        homepage = "http://www." + item["domain"]

        source_artifact = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_artifact": {"$elemMatch": {"type": 4010, "link": homepage}}})
        if source_artifact is None:
            source_artifact = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_artifact": {"$elemMatch": {"type": 4010, "domain": item["domain"]}}})

        if source_artifact is None:
            sadata = {
                "name": item["websiteName"],
                "link": homepage,
                "type": 4010,
                "domain": item["domain"],
                "extended": 'Y',
            }
            save_mongo_source_artifact(source, sourceId, sadata)


def save_website_artifact(website, source, sourceId):
    if not find_link(website["url"], source, sourceId):
        try:
            websadata = {
                "name": website["title"],
                "description": None,
                "link": website["url"],
                "type": 4010,
                "domain": website["domain"],
                "extended": 'Y',
            }
            save_mongo_source_artifact(source, sourceId, websadata)
        except:
            pass


def save_beian_mainbeianhaos(items, source, sourceId):
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        source_mainbeianhao= collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_mainbeianhao.mainBeianhao": item["mainBeianhao"]})
        if source_mainbeianhao is None:

            smdata = {
                "mainBeianhao": item["mainBeianhao"],
                "extended": 'Y',
            }
            save_mongo_source_mainbeianhao(source, sourceId, smdata)


def save_beian_company_names(items, source, sourceId):
    for item in items:
        if item.has_key("whoisExpire") and item["whoisExpire"] == 'Y':
            continue

        if item["organizerType"] != "企业":
            continue

        company_name = name_helper.company_name_normalize(item["organizer"])

        source_company_name = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_company_name.name": company_name})

        if source_company_name is None:

            scndata = {
                "name": company_name,
                "chinese": 'Y',
                "type": 12010,
                "extended": 'Y',
            }
            save_mongo_source_company_name(source, sourceId, scndata)


def copy_from_itunes(app, artifact, source, sourceId):
    if app.has_key("description"):

        collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_artifact": {
            "$elemMatch": {"type": artifact["type"], "domain": artifact["domain"], "name": artifact["name"],"link": artifact["link"]}}}, {
            '$set': {"source_artifact.$.name": app["trackName"],
                     "source_artifact.$.description": app["description"],
                     "source_artifact.$.link": app["trackViewUrl"],
                     "source_artifact.$.domain": app["trackId"],
                     "source_artifact.$.modifyTime": datetime.datetime.now()}})
    else:

        collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_artifact": {
            "$elemMatch": {"type": artifact["type"], "domain": artifact["domain"], "name": artifact["name"],"link": artifact["link"]}}}, {
            '$set': {"source_artifact.$.name": app["trackName"],
                      "source_artifact.$.link": app["trackViewUrl"],
                      "source_artifact.$.domain": app["trackId"],
                      "source_artifact.$.modifyTime": datetime.datetime.now()}})



def save_itunes_artifact(app, source, sourceId):
    try:
        itunessadata = {
            "name": app["trackName"],
            "description": app["description"],
            "link": app["trackViewUrl"],
            "type": 4040,
            "domain": app["trackId"],
            "extended": 'Y'
        }
        save_mongo_source_artifact(source, sourceId, itunessadata)
    except:
        pass


#here should check all artifacts under sourceCompanyId
def find_itunesId(itunesId, source, sourceId):
    artifacts = find_mongo_data(collection_source_company, "source_artifact", source, sourceId, nonexpand=False)
    #Check if itunesId is already existed in artifacts
    for artifact in artifacts:
        if artifact["type"] != 4040:
           continue

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

def copy_from_android(app, artifact, source, sourceId):

    collection_source_company.update_one({"source": source, "sourceId": sourceId, "source_artifact": {
        "$elemMatch": {"type": artifact["type"], "domain": artifact["domain"], "name": artifact["name"], "link": artifact["link"]}}}, {
                         '$set': {"source_artifact.$.name": app["name"],
                                  "source_artifact.$.description": app["description"],
                                  "source_artifact.$.link": app["link"],
                                  "source_artifact.$.domain": app["apkname"],
                                  "source_artifact.$.modifyTime": datetime.datetime.now()}})

def save_android_artifact(app, source, sourceId):

    andsadata = {
        "name": app["name"],
        "description": app["description"],
        "link": app["link"],
        "type": 4050,
        "domain": app["apkname"],
        "extended": 'Y',
    }
    save_mongo_source_artifact(source, sourceId, andsadata)

def save_company_name(app, item_of_name, source, sourceId):
    company_name = app[item_of_name]
    if company_name is None or company_name.strip() == "":
        return

    company_name = name_helper.company_name_normalize(company_name)

    source_company_name = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_company_name.name": company_name})

    if source_company_name is None:
        (chinese, company) = name_helper.name_check(app[item_of_name])
        if chinese is True:
            chinese_type = "Y"
        else:
            chinese_type = "N"

        scnamedata = {
            "name": company_name,
            "chinese": chinese_type,
            "type": 12010,
            "extended": 'Y',
        }
        save_mongo_source_company_name(source, sourceId, scnamedata)

#here should check all artifacts under sourceCompanyId
def find_androidAppname(androidApk, source, sourceId):
    if androidApk is None or androidApk.strip() == "":
        return True

    artifacts = find_mongo_data(collection_source_company, "source_artifact", source, sourceId, nonexpand=False)
    #Check if apkname is already existed in artifacts
    for artifact in artifacts:
        if artifact["type"] != 4050:
           continue

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

def find_link(link, source, sourceId):
    if link is None:
        return True
    if link.strip() == "":
        return True

    artifact = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_artifact": {"$elemMatch": {"type": 4010, "link": link}}})
    if artifact is None:
        flag, domain = url_helper.get_domain(link)
        if domain is not None:
            artifact = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_artifact": {"$elemMatch": {"type": 4010, "domain": domain}}})

    if artifact is None:
        return False
    else:
        return True


def save_itunesSellerUrl_artifact(app, source, sourceId):
    url = app["sellerUrl"]
    flag, domain = url_helper.get_domain(url)
    if flag is not True:
        return None

    if find_link(app["sellerUrl"], source, sourceId):
        return None

    try:
        itunessellersadata = {
            "name": app["sellerName"],
            "description": app["description"],
            "link": app["sellerUrl"],
            "type": 4010,
            "domain": app["sellerDomain"],
            "extended": 'Y',
        }
        save_mongo_source_artifact(source, sourceId, itunessellersadata)
        return 1
    except:
        return None


def save_androidWebsite_artifact(app, source, sourceId):
    url = app["website"]
    flag, domain = url_helper.get_domain(url)
    if flag is not True:
        return None
    if find_link(url, source, sourceId):
        return None

    try:
        andwebsadata = {
            "name": app["name"],
            "description": app["description"],
            "link": app["website"],
            "type": 4010,
            "domain": app["website_domain"],
            "extended": 'Y',
        }
        save_mongo_source_artifact(source, sourceId, andwebsadata)
        return 1
    except:
        return None


def filter_domain(items, domain):
    items_new = []
    for item in items:
        if item["domain"] == domain:
            items_new.append(item)

    return items_new

def check_source_artifact(source, sourceId):
    artifact = collection_source_company.find_one({"source": source, "sourceId": sourceId,
                                                   "source_artifact": {"$elemMatch": {"type": 4010, "$or":[{"active": None},{"active":'Y'}]}}})
    if artifact is None:
        return False
    else:
        return True

def check_source_company_name(source, sourceId):
    company_name = collection_source_company.find_one({"source": source, "sourceId": sourceId,
                                                       "source_company_name": {"$elemMatch": {"type": 12010, "$or":[{"verify": None},{"verify":'Y'}]}}})
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

def find_mongo_data(collection_name, table_name, source, sourceId, nonexpand=True):
    new_data = []
    sourcecompany = collection_name.find_one({"source": source, "sourceId": sourceId})
    if sourcecompany is not None:
        table_data = sourcecompany[table_name]
        for data in table_data:
            if nonexpand is True:
                if data.has_key("expanded") and data["expanded"] == 'Y':
                    pass
                else:
                    new_data.append(data)
            else:
                new_data.append(data)
    return new_data

def expand_clean(source, sourceId):
    sourcecompany = collection_source_company.find_one({"source": source, "sourceId": sourceId})
    new_data = {}
    for table in ["source_artifact", "source_company_name", "source_mainbeianhao"]:
        new_data[table] = []
        if sourcecompany.has_key(table):
            table_data = sourcecompany[table]
            for data in table_data:
                if data.has_key("extended") and data.has_key("verify") and data["extended"] is None and (data["verify"] == 'Y' or data["verify"] is None):
                    data["expanded"] = None
                    new_data[table].append(data)
    collection_source_company.update_one({"_id": sourcecompany["_id"]},
                                         {'$set': {"source_company_name": new_data["source_company_name"],
                                                   "source_artifact": new_data["source_artifact"],
                                                   "source_mainbeianhao": new_data["source_mainbeianhao"]}})


def expand_source_company(source, sourceId, beian_links_crawler, icp_chinaz_crawler, screenshot_crawler, test=False):
    logger.info("source: %s, sourceId: %s Start expand!!!", source, sourceId)
    logger.info("clean old expanded data")

    expand_clean(source, sourceId)
    sourcecompany = collection_source_company.find_one({"source": source, "sourceId": sourceId})
    # exit()
    company_fullname = sourcecompany["source_company"]["fullName"]
    if company_fullname is not None and company_fullname.strip() != "":
        company_fullname = name_helper.company_name_normalize(company_fullname)

        scnames = sourcecompany["source_company_name"]
        check_fullname = False
        for scname in scnames:
            if scname["name"] == company_fullname:
                check_fullname = True
                break
        if check_fullname is False:
            (chinese, company) = name_helper.name_check(company_fullname)
            if chinese is True:
                chinese_type = "Y"
            else:
                chinese_type = "N"
            scname_data ={
                "name": company_fullname,
                "chinese": chinese_type,
                "type": 12010,
            }
            save_mongo_source_company_name(source, sourceId, scname_data)

    round = 1

    while True:
        if round >= 6:
            collection_source_company.update_one({"_id": sourcecompany["_id"]},{'$set': {"scexpanded": True, "modifyTime": datetime.datetime.now()}})
            break

        source_company_names = find_mongo_data(collection_source_company, "source_company_name", source, sourceId)
        main_beianhaos = find_mongo_data(collection_source_company, "source_mainbeianhao", source, sourceId)
        artifacts = find_mongo_data(collection_source_company, "source_artifact", source, sourceId)

        logger.info(json.dumps(source_company_names, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(main_beianhaos, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))

        # Check if there are new stuff which need to do expansion
        if len(source_company_names) == 0 and len(artifacts) == 0 and len(main_beianhaos) == 0:
            collection_source_company.update_one({"_id": sourcecompany["_id"]}, {'$set': {"scexpanded": True, "modifyTime": datetime.datetime.now()}})
            break

        logger.info("source: %s, sourceId: %s expand for round %d", source, sourceId, round)

        # Step A/1:按公司名,备案查询
        logger.info("source: %s, sourceId: %s 按公司名备案查询", source, sourceId)
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

            check_name = list(collection_beian.find({"organizer": source_company_name["name"]}))
            # Case that one company_name has multiple beian# : 上海汇翼->(today.ai/teambition.com)#If only one found in Mongo.beian(organizer) it is fine
            if len(check_name) == 0:
                if test:
                    items_beianlinks = []
                else:
                    items_beianlinks = beian_links_crawler.query_by_company_name(source_company_name["name"])
                    save_collection_beian(collection_beian, items_beianlinks)  # insert infos into Mongo.beian
            else:
                items_beianlinks = check_name
            save_beian_artifacts(items_beianlinks, source, sourceId)  # insert website/homepage into Mysql.source_artifact
            save_beian_company_names(items_beianlinks, source, sourceId)  # insert organizer into Mysql.source_company_names
            save_beian_mainbeianhaos(items_beianlinks, source, sourceId)  # insert mainBeianhao into Mysql.source_mainbeiahao

            # beian
            # 发现更多的artifact(website)和公司名,主备案号

        # Step A/2:按domian,备案查询
        logger.info("source: %s, sourceId: %s 按domian备案查询", source, sourceId)
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

            check_domain = list(collection_beian.find({"domain": domain}))

            if len(check_domain) == 0:
                if test:
                    items_merge =[]
                else:
                    items_beianlinks = beian_links_crawler.query_by_domain(domain)
                    items_icpchinaz = icp_chinaz_crawler.query_by_domain(domain)
                    items_merge = merge_beian(items_beianlinks, items_icpchinaz)

                    save_collection_beian(collection_beian, items_merge)  # insert infos into Mongo.beian
            else:
                items_merge = check_domain

            # filer by check domain to avoid sinaapp.cn case
            items_merge = filter_domain(items_merge, domain)

            save_beian_artifacts(items_merge, source, sourceId)  # insert website/homepage into Mysql.source_artifact
            save_beian_company_names(items_merge, source, sourceId)  # insert organizer into Mysql.source_company_names
            save_beian_mainbeianhaos(items_merge, source, sourceId)  # insert mainBeianhao into Mysql.source_mainbeiahao

            # beian
            # 发现更多的artifact(website)和公司名,主备案号

        # Step A/3 #按主备案号查询
        logger.info("source: %s, sourceId: %s 按主备案号查询", source, sourceId)
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
                    save_collection_mainBeianhao(collection_main_beianhao, items_main_beianhao)  # insert mainBeianhao into Mongo.main_beianhao
            else:
                items_merge = list(collection_beian.find({"mainBeianhao": mainBeianhao}))

            save_beian_artifacts(items_merge, source, sourceId)  # insert website/homepage into Mysql.source_artifact
            save_beian_company_names(items_merge, source, sourceId)  # insert organizer into Mysql.source_company_names
            save_beian_mainbeianhaos(items_merge, source, sourceId)  # insert mainBeianhao into Mysql.source_mainbeiahao
            # 发现更多的artifact(website)和公司名

        # itunes扩展
        # Step B/1 #查询itunes artifact
        logger.info("source: %s, sourceId: %s 查询itunes artifact", source, sourceId)

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
                    set_artifact_active(artifact, "N", source, sourceId)
                else:
                    copy_from_itunes(app, artifact, source, sourceId)  # 存在: copy from mongo.itunes
                    if app.has_key("offline") and app["offline"] is True:
                        set_artifact_active(artifact, "Offline", source, sourceId)
                    else:
                        set_artifact_active(artifact, "Y", source, sourceId)

                    english, is_company = name_helper.english_name_check(app["sellerName"])
                    if english and is_company:
                        itunes_company_enames["sellerName"] = 1
                        app_by_name = app
            else:
                set_artifact_active(artifact, "N", source, sourceId)

        # save the only english name
        if len(itunes_company_enames) == 1:
            company_name = collection_source_company.find_one({"source": source, "sourceId": sourceId, "source_company_name": {"$elemMatch": {"type": 12010, "chinese":"N"}}})

            if company_name is None:
                save_company_name(app_by_name, "sellerName", source, sourceId)

        # Step B/2根据公司名查询更多的itunes artifact
        logger.info("source: %s, sourceId: %s 根据公司名查询更多的itunes artifact", source, sourceId)
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
                artifact_status = check_source_artifact(source, sourceId)

                for app in check_itunes_sellers:
                    # Check if itunesId is already existed in all artifacts in 1 sourceCompanyId
                    if find_itunesId(app["trackId"], source, sourceId):
                        pass
                    else:
                        save_itunes_artifact(app, source, sourceId)

                        if app.has_key("sellerUrl"):
                            # if find_link(app["sellerUrl"], source_company_id) or check_source_artifact(source_company_id):
                            if artifact_status:
                                pass
                            elif lens_domain == 1:
                                artifact_id = save_itunesSellerUrl_artifact(app, source, sourceId)

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
        logger.info("source: %s, sourceId: %s 根据域名查询更多的itunes artifact", source, sourceId)
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
                company_name_status = check_source_company_name(source, sourceId)

                for app in check_itunes_sellerDomains:

                    # Check if itunesId is already existed in all artifacts in 1 sourceCompanyId
                    if find_itunesId(app["trackId"], source, sourceId):
                        pass
                    else:
                        save_itunes_artifact(app, source, sourceId)

                    if company_name_status:
                        pass
                    elif lens_company_names == 1:

                        # save_artifact_itunes_rel(app["_id"], source_artifact_id)
                        chinese, is_company = name_helper.name_check(app["sellerName"])
                        if chinese and is_company:
                            save_company_name(app, "sellerName", source, sourceId)
                            company_name_status = True

                        english, is_company = name_helper.english_name_check(app["sellerName"])
                        if english and is_company:
                            save_company_name(app, "sellerName", source, sourceId)
                            company_name_status = True

            check_itunes_supportDomains = list(collection_itunes.find({"supportDomain": domain}))
            if len(check_itunes_supportDomains) > 0 and len(check_itunes_supportDomains) < 100:

                lens_company_names = count_company_names(check_itunes_supportDomains, "sellerName")
                company_name_status = check_source_company_name(source, sourceId)

                for app in check_itunes_supportDomains:
                    # Check if itunesId is already existed in all artifacts in 1 sourceCompanyId
                    if find_itunesId(app["trackId"], source, sourceId):
                        pass
                    else:
                        save_itunes_artifact(app, source, sourceId)
                        # save_artifact_itunes_rel(app["_id"], source_artifact_id)
                    if company_name_status:
                        pass
                    elif lens_company_names == 1:
                        chinese, is_company = name_helper.name_check(app["sellerName"])
                        if chinese and is_company:
                            save_company_name(app, "sellerName", source, sourceId)
                            company_name_status = True

                        english, is_company = name_helper.english_name_check(app["sellerName"])
                        if english and is_company:
                            save_company_name(app, "sellerName", source, sourceId)
                            company_name_status = True

        # 发现更多的artifact(website)和公司名,check if existed in source_art..and company_name


        # android扩展
        # Step C/1#查询android artifact
        logger.info("source: %s, sourceId: %s 查询android artifact", source, sourceId)
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
                    set_artifact_active(artifact, "N", source, sourceId)
                else:
                    copy_from_android(app, artifact, source, sourceId)  # 存在: copy from mongo.android
                    set_artifact_active(artifact, "Y", source, sourceId)

                    # chinese, is_company = name_helper.name_check(app["author"])
                    # if is_company:
                    #     save_company_name(app, "author", source_company_id)
            else:
                set_artifact_active(artifact, "N", source, sourceId)

        # Step C/2根据公司名查询更多的android artifact
        logger.info("source: %s, sourceId: %s 根据公司名查询更多的android artifact", source, sourceId)
        for source_company_name in source_company_names:
            # producer name
            if source_company_name["name"] is None or source_company_name["name"].strip() == "":
                continue

            check_android_authors = list(collection_android.find({"author": source_company_name["name"]}))
            if len(check_android_authors) > 0 and len(check_android_authors) < 200:

                lens_domain = count_domains(check_android_authors, "website")
                artifact_status = check_source_artifact(source, sourceId)

                # check if author is consistent
                for app in check_android_authors:
                    # Check if AnId have one 4010
                    if find_androidAppname(app["apkname"], source, sourceId):
                        pass
                    else:
                        save_android_artifact(app, source, sourceId)

                        if artifact_status:
                            pass
                        elif lens_domain == 1:
                            artifact_id = save_androidWebsite_artifact(app, source, sourceId)

                            if artifact_id is not None:
                                artifact_status = True

                                # save_artifact_android_rel(app["_id"], source_artifact_id)
                                # save_company_name(app, "author", source_company_id)

        # Step C/3根据域名查询更多的android artifact
        logger.info("source: %s, sourceId: %s 根据域名查询更多的android artifact", source, sourceId)
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
                company_name_status = check_source_company_name(source, sourceId)

                for app in check_android_websiteDomains:
                    # Check if AndroidId is already existed in artifacts
                    if find_androidAppname(app["apkname"], source, sourceId):
                        pass
                    else:
                        save_android_artifact(app, source, sourceId)
                        # save_artifact_android_rel(app["_id"], source_artifact_id)
                    if company_name_status:
                        pass
                    elif lens_company_names == 1:

                        chinese, is_company = name_helper.name_check(app["author"])
                        if is_company:
                            save_company_name(app, "author", source, sourceId)
                            company_name_status = True

            check_android_apknameDomains = list(collection_android.find({"apkname_domain": domain}))
            # add threshold to avoid case: domain: com.wowotuan
            if len(check_android_apknameDomains) > 0 and len(check_android_apknameDomains) < 100:

                lens_company_names = count_company_names(check_android_apknameDomains, "author")
                company_name_status = check_source_company_name(source, sourceId)

                for app in check_android_apknameDomains:
                    # Check if AndroidId is already existed in artifacts
                    if find_androidAppname(app["apkname"], source, sourceId):
                        pass
                    else:
                        save_android_artifact(app, source, sourceId)
                        # save_artifact_android_rel(app["_id"], source_artifact_id)
                    if company_name_status:
                        pass
                    elif lens_company_names == 1:

                        chinese, is_company = name_helper.name_check(app["author"])
                        if is_company:
                            save_company_name(app, "author", source, sourceId)
                            company_name_status = True
        # 发现更多的artifact(website)和公司名

        # 曾用名 TODO

        # 清洗website artfiact
        # 查询meta信息, 标记不能访问的?website?, 处理转跳的website
        logger.info("source: %s, sourceId: %s website meta", source, sourceId)
        for artifact in artifacts:
            if artifact["type"] != 4010:
                continue
            if artifact["link"] is None or artifact["link"].strip() == "":
                # set_active("source_artifact", "N", artifact["id"])
                set_artifact_active(artifact, "N", source, sourceId)
                continue

            url = artifact["link"].strip()
            meta = collection_website.find_one({"url": url})
            if meta is None or meta["httpcode"]==404:
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
                    set_artifact_active(artifact, "N", source, sourceId)

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
                            set_artifact_active(artifact, "Redirect", source, sourceId)
                        else:
                            if flag is True:  # 这是个'好'地址
                                set_artifact_active(artifact, "Y", source, sourceId)
                            else:
                                if flag_new is True:  # 转跳后是个 '好'地址
                                    set_artifact_active(artifact, "Redirect", source, sourceId)
                                    save_website_artifact(meta_new, source, sourceId)
                                else:
                                    set_artifact_active(artifact, "Y", source, sourceId)
                    else:
                        set_artifact_active(artifact, "Y", source, sourceId)
                elif meta["httpcode"] == 404:
                    set_artifact_active(artifact, "N", source, sourceId)

        # verify -> source_artifacts/source_company_name set verify
        logger.info("source: %s, sourceId: %s set verify", source, sourceId)
        for artifact in artifacts:
            set_artifact_expand(artifact, source, sourceId)
        for source_company_name in source_company_names:
            set_scname_expand(source_company_name, source, sourceId)
        for main_beianhao in main_beianhaos:
            set_scbeianhao_expand(main_beianhao, source, sourceId)

        round += 1

if __name__ == "__main__":
    pass
