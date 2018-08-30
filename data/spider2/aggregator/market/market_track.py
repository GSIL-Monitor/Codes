# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json
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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/website'))
import website

#logger
loghelper.init_logger("company_expand", stream=True)
logger = loghelper.get_logger("company_expand")

#mongo
mongo = db.connect_mongo()
#create index?
#collection = mongo.crawler_v3.projectdata

collection_itunes = mongo.market.itunes

collection_android = mongo.market.android
collection_android_market = mongo.market.android_market
collection_website = mongo.info.website

COMPANIES=[]

#exception
itunesDomainEx = ["baidu.com","hao123.com","appzg.org"]


def update_domain(domain, row_id):
    conn = db.connect_torndb_proxy()
    sql = "update artifact set domain=%s where id=%s"
    conn.update(sql, domain, row_id)
    conn.close()

def update_domain_artifact():
    # conn = db.connect_torndb()
    conn = db.connect_torndb_proxy()
    arts = conn.query("select * from artifact where (active ='Y' or active is null) and domain is null")
    for art in arts:
        if art["type"] in [4010, 4040, 4050]:
            (linktype,appmarket , domain) = url_helper.get_market(art["link"])
            if domain is not None:
                update_domain(domain, art["id"])
        if art["type"] in [4020]:
            if art["link"] is not None and art["link"].strip()!="":
                update_domain(art["link"], art["id"])
    conn.close()


def patch_company_establish_date(company_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang
    company1 = conn.get("select * from company where id=%s", company_id)
    establish_date = None
    if company1["corporateId"] is not None:

        corporate = conn.get("select * from corporate where id=%s", company1["corporateId"])
        if corporate is not None and corporate["fullName"] is not None:
            gongshang = collection_gongshang.find_one({"name": corporate["fullName"]})

            if gongshang is not None and gongshang.has_key("establishTime"):
                try:
                    if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] != establish_date):
                        establish_date = gongshang["establishTime"]
                except:
                    pass

        if establish_date is None:
            aliases = conn.query("select * from corporate_alias where "
                                 "(active is null or active !='N') and corporateId=%s", company1["corporateId"])
            for alias in aliases:
                gongshang = collection_gongshang.find_one({"name": alias["name"]})
                if gongshang is not None and gongshang.has_key("establishTime"):
                    try:
                        if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] != establish_date):
                            establish_date = gongshang["establishTime"]
                    except:
                        pass
                if establish_date is not None:
                    break

        if establish_date is not None:

            logger.info("Company: %s establishDate: %s", company_id, establish_date)
            try:
                conn.update("update corporate set establishDate=%s where id=%s", establish_date, company1["corporateId"])
            except:
                pass

        #patch round
        if corporate is not None:
            funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') "
                               "order by fundingDate desc limit 1",
                               corporate["id"])
            if funding is not None:
                # corporate = conn.get("select * from corporate where id=%s", corporate_id)
                # if corporate is not None:
                conn.update("update corporate set round=%s where id=%s",
                            funding["round"],  corporate["id"])
            else:
                if corporate["round"] is not None:
                    conn.update("update corporate set round=-1 where id=%s", corporate["id"])
    conn.close()
    mongo.close()

def patch_company_location(company_id):
    conn = db.connect_torndb_proxy()
    company1 = conn.get("select * from company where id=%s", company_id)
    if company1["corporateId"] is not None:
        corporate = conn.get("select * from corporate where id=%s", company1["corporateId"])

        if corporate is not None and (corporate["locationId"] is None or corporate["locationId"] == 0):
            locationId = None

            alias0 = [{"name":corporate["fullName"]}] if corporate["fullName"] is not None else []
            aliases = conn.query("select * from corporate_alias where corporateId=%s and "
                                 "(active is null or active ='Y') and verify='Y'",
                                 company1["corporateId"])
            for alias in alias0+aliases:
                logger.info(alias["name"])
                loc1, loc2 = name_helper.get_location_from_company_name(alias["name"])
                logger.info("%s/%s",loc1,loc2)
                if loc1 is not None:
                    l = conn.get("select *from location where locationName=%s", loc1)
                    if l:
                        locationId = l["locationId"]
                        break
            if locationId is not None:
                conn.update("update corporate set locationId=%s where id=%s", locationId, company1["corporateId"])
    conn.close()


def patch_corporate_alias(company_id):
    conn = db.connect_torndb_proxy()
    company = conn.get("select * from company where id=%s", company_id)
    if company["corporateId"] is not None:
        corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
        corporate_a = [{"name": corporate["fullName"]}]
        for s in corporate_a:
            if s["name"] is None or s["name"].strip() == "":
                continue
            name = s["name"].strip()
            alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s limit 1",
                             company["corporateId"], name)
            if alias is None:
                sql = "insert corporate_alias(corporateId,name,active,createTime,modifyTime) \
                            values(%s,%s,%s,now(),now())"
                conn.insert(sql, company["corporateId"], name, None)
    conn.close()

def add_website(company_id):
    conn = db.connect_torndb_proxy()
    artifacts = conn.query("select * from artifact where companyId=%s and "
                           "type=4010 and (active is null or active='Y')", company_id)
    for art in artifacts:
        record = collection_website.find_one({"url": art["link"]})
        if record is None:
            getWebsite(art["link"])
    conn.close()



def getWebsite(URL):
    logger.info("Checking : %s", URL)
    meta = website.get_meta_info(URL)
    if meta is None :
        meta = {
            "url": URL,
            "httpcode": 404
        }
        saveWebsite(meta)
    else:
        saveWebsite(meta)
        # screenshot(URL)


def saveWebsite(item):
    # in case that related websites have been saved before
    record = collection_website.find_one({"url": item["url"]})
    if record is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        try:
            id = collection_website.insert(item)
        except:
            return None



def set_active(table, active_value, row_id):
    conn = db.connect_torndb()
    sql = "update " + table + " set active=%s where id=%s"
    conn.update(sql, active_value, row_id)
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
        logger.info(e)
        artifact_id = None
    conn.close()
    return artifact_id

#here should be all artifacts under companyId
def find_androidAppname(androidApk, companyId):
    if androidApk is None or androidApk.strip() == "":
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
            return True
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


def expand():

    while True:
        # gevent -> list of companies

        if len(COMPANIES) == 0:
            return
        company_id = COMPANIES.pop(0)
        logger.info("Company id: %s Start app check!!!", company_id)

        conn = db.connect_torndb()
        company_names = conn.query("select * from corporate_alias where corporateId in (select corporateId from "
                                   "company where id=%s) and (active is null or active='Y')", company_id)
        artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')", company_id)
        artifacts_and = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') and type=4050",
                               company_id)
        logger.info(json.dumps(company_names, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))
        conn.close()

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

            if len(artifacts_and) <= 4:
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



def start_run(concurrent_num):
    while True:
        logger.info("patch domain")
        update_domain_artifact()
        logger.info("Company apps expand start...")

        # 查询所有需要扩展的公司源
        # conn = db.connect_torndb()
        conn = db.connect_torndb_proxy()
        companies = conn.query("select id from company where (active is null or active !='N') order by id")
        # companies = conn.query("select * from company where id=309492")
        conn.close()
        for company in companies:
            CompanyId = company["id"]
            if CompanyId is None:
                continue
            patch_corporate_alias(CompanyId)
            patch_company_establish_date(CompanyId)
            patch_company_location(CompanyId)
            COMPANIES.append(CompanyId)
            add_website(CompanyId)

        threads = [gevent.spawn(expand) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


        logger.info("Company apps expand end.")
        break

        # gevent.sleep(10*60)

if __name__ == "__main__":
    start_run(1)
    # patch_company_establish_date(819)