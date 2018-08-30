# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
from kr36_location import kr36_cities


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("36kr_investor_parser_2", stream=True)
logger = loghelper.get_logger("36kr_investor_parser_2")

SOURCE = 13023  #36kr
TYPE = 36003   #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)

def formCityName(name):
    if name.find("省")>=0:
        name = name.split("省")[1]
    if name.endswith("市"):
        return name.split("市")[0]
    if name.endswith("县"):
        return name.split("县")[0]
    return name


def process():
    logger.info("36kr_investor_parser begin...")

    start = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)
        # items = [parser_db_util.find_process_one(SOURCE,TYPE,18)]
        for item in items:
            r = parse_investor(item)
            logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))

            source_investor_id = parser_db_util.save_investor_standard_new(r, download_crawler)

            if len(r["addresses"]) > 0 :
                parser_db_util.save_investor_contact_standard(source_investor_id, r["addresses"])


            parseMember_save(source_investor_id, item, download_crawler)


            parser_db_util.update_processed(item["_id"])
            logger.info("processed %s" ,item["url"])
            # break
        # break
        if len(items) == 0:
            break

    logger.info("36kr_investor_parser end.")


def parse_investor(item):
    logger.info("parse_investor")
    investor_key = item["key"]

    c = item["content"]["basic"]["data"]

    establish_date = None
    if c.has_key("startDate"):
        d = time.localtime(c["startDate"]/1000)
        if d.tm_year > 1980:
            establish_date = datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)

    addresses = []

    for ad in c.get("addresses",[]):
        address1 = None
        address2 = None
        if ad.has_key("city"):
            address1 = ad["city"]
        if ad.has_key("address"):
            address2 = ad["address"]

        location_id = 0
        if address1 is not None and address1.strip()!="":
            city = address1
            if city != None:
                location = parser_db_util.get_location(formCityName(city))
                if location != None:
                    location_id= location["locationId"]

        if location_id==0 and address2 != None and address2.strip()!="":
            city = address2
            if city != None:
                location = parser_db_util.get_location(formCityName(city))
                if location != None:
                    location_id = location["locationId"]

        if (address2 is not None and address2.strip()!="") or (ad.get("phone",None) is not None and ad.get("phone",None).strip() !="") or \
                                ad.get("email", None) is not None and ad.get("email", None).strip() != "" :
            addresses.append({
                "locationId": location_id,
                "address": address2,
                "phone": ad.get("phone",None) if ad.get("phone",None) is not None and ad.get("phone",None).strip() !="" else None,
                "email": ad.get("email", None) if ad.get("email", None) is not None and ad.get("email",
                                                                                               None).strip() != "" else None,
            })

    name = c["nameAbbr"]
    fullName = c["name"]
    if (name is None or name.strip() == "") and (fullName is None or fullName.strip() ==""):
        logger.info("*******************wrong thing")
        return {
            "wrong": 1,
            "key": investor_key
        }
    else:
        return {
            "name": fullName if name is None or name.strip() == "" else name,
            "fullName": None if fullName is None or fullName.strip() == "" else fullName,
            "description": None if c.get("intro",None) is None or c.get("intro",None).strip() == "" else c["intro"],
            "website": None if c.get("website",None) is None or c.get("website",None).strip() == "" else c["website"],
            "logo": None if c.get("logo",None) is None or c.get("logo",None).strip() == "" else c["logo"],
            "source": SOURCE,
            "sourceId": str(investor_key),
            "wechatId": None if c.get("weixin",None) is None or c.get("weixin",None).strip() == "" else c["weixin"],
            "weibo": None if c.get("weibo",None) is None or c.get("weibo",None).strip() == "" else c["weibo"],
            "enName": None if c.get("enNameAbbr",None) is None or c.get("enNameAbbr",None).strip() == "" else c["enNameAbbr"],
            "enFullName": None if c.get("enName",None) is None or c.get("enName",None).strip() == "" else c["enName"],
            "establishDate": establish_date,
            "addresses": addresses
            }

    #source_company_id = parser_util.insert_source_company(source_company)


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

def parseMember_save(source_investor_id, item, download_crawler):
    logger.info("parseMember_save")
    members = item["content"]["member"]["data"]["member"]
    sm = []
    for m in members:
        if m.has_key("userInfo") is False:
            continue
        mu = m["userInfo"]
        if mu.get("name",None) is None or mu.get("name",None).strip() == "":
            continue

        logger.info(mu["name"])

        desc = mu.get("intro",None)
        position = m.get("title",None)


        logo = mu.get("avatar", None)

        source_member = {
            "source": SOURCE,
            "sourceId": str(mu["uid"]) if mu.get("uid",None) is not None and str(mu.get("uid",None)).strip() !="" else get_company_code(mu["name"]),
            "name": mu["name"],
            "logo": logo,
            "position": position,
            "description": desc,
        }

        try:
            # logger.info(json.dumps(source_member, ensure_ascii=False, cls=util.CJsonEncoder))
            sm.append(source_member)
            # logger.info(source_member)
            # logger.info(source_company_member_rel)
        except:
            pass

    logger.info(len(sm))
    parser_db_util.save_investor_member_standard(source_investor_id, sm, download_crawler)




if __name__ == "__main__":
    while True:
        process()
        #break   #test
        time.sleep(30*60)