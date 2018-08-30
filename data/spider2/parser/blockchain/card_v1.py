# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from bson.objectid import ObjectId
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
import config
import image_helper
import url_helper
#logger
loghelper.init_logger("card_v1", stream=True)
logger = loghelper.get_logger("card_v1")

#parse data from qimingpian directly, bamy called it step 1 to checkout company



def find_companies_by_full_name_corporate(full_names, idmax=0):
    companyIds = []
    for full_name in full_names:
        if full_name is None or full_name == "":
            continue

        # full_name = name_helper.company_name_normalize(full_name)

        conn = db.connect_torndb()
        corporate_aliases = conn.query(
            "select a.* from corporate_alias a join corporate c on c.id=a.corporateId where "
            "(c.active is null or c.active !='N') and (a.active is null or a.active !='N') "
            "and a.name=%s",
            full_name)
        # conn.close()
        for ca in corporate_aliases:
            # logger.info("*******foΩΩΩund %s",ca)
            company = conn.get(
                "select * from company where corporateId=%s and (active is null or active!='N') limit 1",
                ca["corporateId"])
            if company is not None:
                logger.info("find_company_by_full_name %s: %s", full_name, company["id"])
                if company["id"] not in companyIds:
                    if int(company["id"]) > idmax:
                        companyIds.append(company["id"])
        conn.close()
    return companyIds


def find_reference(shortnames, idmax=0):
    # if source_company["companyId"] is not None:
    #     return source_company["companyId"]
    candidate_company_ids = []
    conn = db.connect_torndb()
    for short_name in shortnames:
        if short_name is None or short_name.strip() == "":
            continue
        short_name = short_name.strip()

        # logger.info("short_name: %s", short_name)
        # candidate_company_ids = []
        cs = list(conn.query("select * from company"
                             " where name=%s and (active is null or active !='N')", short_name))
        for c in cs:
            company_id = c["id"]
            candidate_company_ids.append(company_id)
            break

        aliases = list(conn.query("select a.companyId from company_alias"
                                  " a join company c on c.id=a.companyId " +
                                  "where (c.active is null or c.active!='N') and a.name=%s", short_name))
        for alias in aliases:
            company_id = alias["companyId"]
            if company_id not in candidate_company_ids:
                candidate_company_ids.append(company_id)
            # break
    conn.close()
    return candidate_company_ids
    # if len(candidate_company_ids) > 0:
    #     return candidate_company_ids[0]
    # else:
    #     return None


def find_companies_by_artifacts(source_artifacts, idmax=0):
    companyIds = []
    # author是运营者, apkname是开发者
    # logger.info("find_company_by_artifact")
    #if source_artifact["type"] != 4040 and source_artifact["type"] != 4050:
    for source_artifact in source_artifacts:
        if source_artifact["type"] == 4010:
            if source_artifact["link"] is not None and source_artifact["link"] != "":
                conn = db.connect_torndb()
                artifacts = conn.query("select a.* from artifact a join company c on c.id=a.companyId "
                                       "where (c.active is null or c.active !='N') and a.type=%s and a.link=%s",
                                       source_artifact["type"],
                                       source_artifact["link"])
                conn.close()
                if len(artifacts) > 0:
                    for artifact in artifacts:
                        logger.info("find_company_by_artifact 1, %s, %s, %s", artifact["type"], artifact["link"],
                                    artifact["companyId"])
                        if artifact["companyId"] not in companyIds:
                            if int(artifact["companyId"]) > idmax:
                                companyIds.append(artifact["companyId"])

            if len(companyIds) == 0:
                if source_artifact["domain"] is not None and source_artifact["domain"] != "":
                    conn = db.connect_torndb()
                    artifacts = conn.query("select a.* from artifact a join company c on c.id=a.companyId "
                                        "where (c.active is null or c.active !='N') and a.type=%s and a.domain=%s",
                                            source_artifact["type"],
                                            source_artifact["domain"])
                    conn.close()
                    if len(artifacts) > 0:
                        for artifact in artifacts:
                            logger.info("find_company_by_artifact 2, %s, %s, %s", artifact["type"], artifact["domain"],
                                        artifact["companyId"])
                            if artifact["companyId"] not in companyIds:
                                if int(artifact["companyId"]) > idmax:
                                    companyIds.append(artifact["companyId"])
    return companyIds


def insert_cop_st_rel(corporateId,sourceId,stockExchangeId,status,listingDate,applyDate,delistDate,stockWeb,industry):
    conn = db.connect_torndb()
    cop_st_rel = conn.get("select * from corporate_stock_exchange_rel where corporateId=%s and "
                          "stockExchangeId=%s limit 1", corporateId, stockExchangeId)
    logger.info("stock: %s, %s, %s", stockExchangeId,sourceId,listingDate)
    if cop_st_rel is None:
        sql = "insert corporate_stock_exchange_rel(corporateId,stockExchangeId,status,createTime,modifyTime," \
              "applyDate,listDate,delistDate,stockSymbol,stockExchangeUrl,csrc_great_code_desc) " \
              "values(%s,%s,%s,now(),now(),%s,%s,%s,%s,%s,%s)"
        cop_st_rel_id = conn.insert(sql, corporateId, stockExchangeId,status,applyDate,
                                    listingDate,delistDate,str(sourceId),stockWeb,industry)
    else:
        cop_st_rel_id = cop_st_rel["id"]
        sql = "update corporate_stock_exchange_rel set status=%s,modifyTime=now(),applyDate=%s," \
              "listDate=%s,delistDate=%s,stockExchangeUrl=%s,csrc_great_code_desc=%s where id=%s"
        # conn.update(sql, status,applyDate,listingDate,delistDate,stockWeb,industry,cop_st_rel_id)
    conn.close()
    return cop_st_rel_id

def update_ipoStatus(corporateId,seid):
    # conn = db.connect_torndb()
    # istatus = 70030
    # ilocationid = 340
    # conn.update("update corporate set ipoStatus=%s, stockExchangeId=%s where id=%s", istatus, seid, corporateId)
    # conn.close()
    pass






def aggregate(item, tt=1):
    company_ids = []
    flag = False
    btb = item["data"]["btb"]
    basic = item["data"]["basic"]
    if btb["bz_code"] is not None and btb["bz_code"].strip() != "":
        # logger.info(btb["source"])
        fullName = basic["company"]
        shortName = basic["product"]
        website = basic["gw_link"]
        type, market, app_id = url_helper.get_market(website)
        artifact = {
            "link": website,
            "domain": app_id,
            "type": type
        }
        website1 = btb["gw"]
        type, market, app_id = url_helper.get_market(website1)
        artifact1 = {
            "link": website,
            "domain": app_id,
            "type": type
        }


        if tt == 1:
            if len(find_companies_by_full_name_corporate([fullName])) > 0:
                company_ids = find_companies_by_full_name_corporate([fullName])
                logger.info("%s found fullName by %s", btb["bz_code"], fullName)
                flag = 2
            elif len(find_companies_by_artifacts([artifact])) > 0:
                company_ids = find_companies_by_artifacts([artifact])
                logger.info("%s found artifact by %s", btb["bz_code"], website)
                flag = 3
            elif len(find_reference([shortName, btb["bz_code"]])) > 0:
                company_ids = find_reference([shortName, btb["bz_code"]])
                logger.info("%s found shortName by %s", btb["bz_code"], shortName)
                flag = 4
            else:
                flag = 5
        else:
            if len(find_companies_by_artifacts([artifact1])) > 0:
                logger.info("%s found artifact by %s", btb["bz_code"], website)
                flag = 4

            else:
                flag = 5

    else:
        flag = 0

    return flag, company_ids



if __name__ == '__main__':
    logger.info("Begin...")
    # noo = 0
    conn = db.connect_torndb()
    fp2 = open("company_sh.txt", "w")
    while True:
        (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
        mongo = db.connect_mongo()
        collection = mongo.raw.qmp

        while True:
            # items = list(collection.find({"_id" : ObjectId("5ab855c51045403176b867a4")}).limit(100))
            items = list(collection.find({"url":"http://vip.api.qimingpian.com/d/c3"},
                                         {"data.basic":1,"data.btb":1,"postdata":1}))
            logger.info("items : %s", len(items))
            for item in items:
                basic = item["data"]["basic"]
                btb = item["data"]["btb"]
                pdata = item["postdata"]
                source_link = btb["source_link"]
                f, cids = aggregate(item, 1)
                # pass
                if f == 0:
                    num0 += 1
                elif f == 1:
                    num1 += 1
                elif f == 2:
                    num2 += 1
                elif f == 3:
                    num3 += 1
                elif f == 4:
                    num4 += 1
                elif f == 5:
                    num5 += 1
                rlink = "http://vip.qimingpian.com/#/detailcom?src=magic&ticket=%s&id=%s" % (pdata["ticket"],pdata["id"])
                links = []
                for cid in cids:
                    c = conn.get("select * from company where id=%s", cid)
                    links.append('http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"])

                if len(basic["rongzi"])>0:
                    rongzi = 1
                else:
                    rongzi = 0

                line = "%s+++%s+++%s+++%s+++%s+++%s+++%s\n" % (basic["product"],btb["bz_code"]+" ",
                                                               basic["company"]+"|"+basic["gw_link"],
                                                               source_link if len(source_link)>0 else " ",
                                                               "|".join(links) if len(links)>0 else " ",
                                                               rongzi, rlink)
                fp2.write(line)
            break
            # if len(items) == 0:
            #     break


        # break
        logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
        fp2.close()
        mongo.close()
        conn.close()
        # time.sleep(10*60)
        break
