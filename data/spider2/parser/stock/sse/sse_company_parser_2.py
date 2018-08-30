# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("sse_company_parser_2", stream=True)
logger = loghelper.get_logger("sse_company_parser_2")

SOURCE = 13401 #sse
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)

def process():
    logger.info("sse_company_parser begin...")

    start = 0
    while True:
        mongo = db.connect_mongo()
        collection = mongo.stock.sse
        items = list(collection.find({"processStatus": 1}).limit(100))

        for item in items:
            # try:
                r = parse_company(item)
                logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

                source_company_id = parser_db_util.save_company_standard(r, download_crawler)
                parser_db_util.delete_source_company_name(source_company_id)
                parser_db_util.delete_source_mainbeianhao(source_company_id)
                parser_db_util.save_source_company_name(source_company_id, r["name"],12020)
                parser_db_util.save_source_company_name(source_company_id, r["fullName"],12010)
                main_company_name = name_helper.get_main_company_name(r["fullName"])
                if main_company_name != r["fullName"]:
                    parser_db_util.save_source_company_name(source_company_id, main_company_name,12010)
                logger.info("source_company_id=%s", source_company_id)

                if r["englishName"] is not None and r["englishName"].strip() != "" and r["englishName"].strip() != "-" \
                    and r["englishName"].strip() != "null" and r["englishName"].strip() != "无":
                    parser_db_util.save_source_company_name(source_company_id, r["englishName"], 12010)

                # source_company_id = None
                artifacts=parse_artifact(source_company_id,item)
                logger.info(json.dumps(artifacts, ensure_ascii=False, cls=util.CJsonEncoder))

                parser_db_util.save_artifacts_standard(source_company_id, artifacts)

                parseMember_save(source_company_id, item, download_crawler)


                collection.update({"_id": item["_id"]}, {"$set": {"processStatus": 2}})
                logger.info("processed %s" ,item["sourceId"])

        # break
        mongo.close()
        if len(items) == 0:
            break

    logger.info("sse_company_parser end.")


def parse_company(item):
    logger.info("parse_sse_stock")
    # logger.info(item)
    company_key = item["sourceId"]

    #company basic info
    c = item["baseinfo"]

    field = c["CSRC_GREAT_CODE_DESC"]


    result = parser_db_util.get_location(c["AREA_NAME_DESC"].replace("市",""))
    if result != None:
        location_id = result["locationId"]
    else:
        location_id = None

    fullName = c["FULLNAME"]
    logger.info("parsing :%s|%s", fullName, company_key)
    desc = None
    brief = None
    try:
        desc = item["jqkaBrief"]["desc"]
    except:
        pass
    try:
        brief = item["jqkaBrief"]["brief"].split("。")[0]
        logger.info(len(brief))
        if len(brief) > 99:
            brief = None
    except:
        pass
    productDesc = None
    modelDesc = None
    operationDesc = None
    teamDesc = None
    marketDesc = None
    compititorDesc = None
    advantageDesc = None
    planDesc = None
    otherDesc = None


    return {
        "name": c["shortname"],
        "fullName": fullName.strip(),
        "description": desc,
        "productDesc": productDesc,
        "modelDesc": modelDesc,
        "operationDesc": operationDesc,
        "teamDesc": teamDesc,
        "marketDesc": marketDesc,
        "compititorDesc": compititorDesc,
        "advantageDesc": advantageDesc,
        "planDesc": planDesc,
        "otherDesc": otherDesc,
        "brief": brief,
        "round": 0,
        "roundDesc": None,
        "companyStatus": 2010,
        'fundingType': 0,
        "locationId": location_id,
        "address": c["COMPANY_ADDRESS"] if c.has_key("COMPANY_ADDRESS") and c["COMPANY_ADDRESS"] is not None and c["COMPANY_ADDRESS"].strip()!="" else None,
        "phone": str(c["REPR_PHONE"]) if c.has_key("COMPANY_ADDRESS") and c["REPR_PHONE"] is not None and str(c["REPR_PHONE"]).strip() not in ["","-"] else None,
        "establishDate": None,
        "logo": None,
        "source": SOURCE,
        "sourceId": company_key,
        "field": field,
        "subField": None,
        "tags": None,
        "headCountMin": None,
        "headCountMax": None,
        "englishName": c["FULL_NAME_IN_ENGLISH"] if c.has_key("FULL_NAME_IN_ENGLISH") else None
    }


def get_android_domain(app_market, app_id):
    domain = None
    if app_market == 16010 or app_market == 16020:
        android_app = parser_db_util.find_android_market(app_market, app_id)
        if android_app:
            domain = android_app["apkname"]
    else:
        domain = app_id
    return domain


def parse_artifact(source_company_id,item):
    logger.info("parse_artifact")
    c = item["baseinfo"]
    artifacts = []
    website = c.get("WWW_ADDRESS","").strip()

    website = url_helper.url_normalize(website)
    if website is not None and website != "":
        if website.find("http://") == -1 and website.find("https://"):
            website = "http://"+website
        type, market, app_id = url_helper.get_market(website)
        if type == 4010:
            if website.find('sse.com') > 0:
                pass
            else:
                artifact = {
                    "sourceCompanyId": source_company_id,
                    "name": c["shortname"],
                    "description": None,
                    "link": website,
                    "domain": app_id,
                    "type": type
                }
                artifacts.append(artifact)
        elif (type==4040 or type==4050) and app_id is not None:
            domain = get_android_domain(market, app_id)
            if (type==4040 or type==4050) and domain is not None:
                artifact = {
                    "sourceCompanyId": source_company_id,
                    "name": c["shortname"],
                    "description": None,
                    "link": website,
                    "domain": domain,
                    "type": type
                }
                artifacts.append(artifact)

    return artifacts

def get_company_code(name):
    conn = db.connect_torndb()
    if len(name) <8 :
        pinyin = lazy_pinyin(name.decode('utf-8'))
        company_code = ''.join(pinyin)
    else:
        pinyin = lazy_pinyin(name.decode('utf-8'), style=pypinyin.INITIALS)
        company_code = ''.join(pinyin)

    bs = bytes(company_code)
    st = ''
    for b in bs:
        if re.match('-|[0-9a-zA-Z]', b):
            st +=b
    company_code = st

    if len(company_code) >31:
        company_code = company_code[0:30]

    if len(company_code) < 3:
        company_code = company_code+str(random.randint(1, 100))


    conn.close()
    return company_code


def parseMember_save(source_company_id, item, download_crawler):
    company_key = item["sourceId"]
    logger.info("parseMember_save")
    if item.has_key("jqkaBrief") is False:
        return
    m = {"name":item["jqkaBrief"]["chairman"], "job":"董事长"}
    try:
        if m["name"] is None or m["name"].strip()=="":
            return

        position = m.get("job","")

        if position.find("董事长") == -1:
            return

        logger.info("%s-%s",m["name"], position)
        source_member = {
            "source": SOURCE,
            "sourceId": str(company_key)+'_'+get_company_code(m["name"]),
            "name": m["name"],
            "photo_url": None,
            "weibo": None,
            "location": 0,
            "role": position,
            "description": None,
            "education": None,
            "work": None
        }
        # ptype = name_helper.position_check(position)
        ptype = 5010

        source_company_member_rel = {
            "sourceCompanyId": source_company_id,
            "position": position,
            "joinDate": None,
            "leaveDate": None,
            "type": ptype
        }
        # try:
        logger.info(json.dumps(source_member, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(json.dumps(source_company_member_rel, ensure_ascii=False, cls=util.CJsonEncoder))

        parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
        pass
    except:
        pass




if __name__ == "__main__":
    while True:
        process()
        #break   #test
        time.sleep(30*60)