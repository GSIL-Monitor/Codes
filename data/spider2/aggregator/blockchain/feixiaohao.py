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
loghelper.init_logger("feixiaohao_agg", stream=True)
logger = loghelper.get_logger("feixiaohao_agg")



def getinfo(companyId, corporateId):
    info = ""
    verfyinfo = ""
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    cor = conn.query("select * from corporate where (active is null or active='Y')"
                     " and verify is null and id=%s", corporateId)
    if len(cor) > 0: verfyinfo += "corporate "
    comp = conn.query("select * from company where (active is null or active='Y')"
                      " and verify is null and id=%s", companyId)
    if len(comp) > 0: verfyinfo += "基本信息 "
    fundings = conn.query("select * from funding f left join corporate c on f.corporateId=c.id "
                          "where f.corporateId=%s and (c.active is null or c.active='Y')  and "
                          "(f.active is null or f.active='Y') and f.verify is null", corporateId)
    if len(fundings) > 0: verfyinfo += "融资 "
    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                           "and verify is null", companyId)
    if len(artifacts) > 0: verfyinfo += "产品 "
    members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                         "where cmr.companyId=%s and m.verify is null and "
                         "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                         "(cmr.active is null or cmr.active='Y')", companyId)
    if len(members) > 0: verfyinfo += "团队 "
    comaliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')"
                            " and verify is null", companyId)
    if len(comaliases) > 0: verfyinfo += "产品线短名 "
    corpaliaes = conn.query("select * from corporate_alias where (active is null or active='Y') "
                            "and verify is null  and corporateId=%s", corporateId)
    if len(corpaliaes) > 0: verfyinfo += "corporate公司名 "
    comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                         "(active is null or active='Y') and verify is null", companyId)
    if len(comrecs) > 0:  verfyinfo += "招聘 "

    desc = mongo.company.modify.find_one({'companyId': companyId, 'sectionName': 'desc'})
    if desc is None:  verfyinfo += "简介 "

    conn.close()
    if len(verfyinfo) > 0:
        info = verfyinfo + "未verify"
    else:
        info = "都verify"
    logger.info("company: %s->%s", companyId, info)
    return info

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







if __name__ == '__main__':
    logger.info("Begin...")
    # noo = 0
    conn = db.connect_torndb()
    fp2 = open("company_sh.txt", "w")
    (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp

    while True:
        bcs = conn.query("select * from digital_token where companyId is null and "
                         "(active is null or active !='N')")

        for bc in bcs:
            companyIds = []
            num0 += 1

            websitestr = bc["websites"]

            if websitestr is None:
                num1 += 1
                continue
            else:
                # companyIds = []
                websites = websitestr.split("|")

                for website in websites:
                    tp, market, app_id = url_helper.get_market(website)
                    # logger.info("%s-%s", type(tp),tp)
                    artifact = {
                        "link": website,
                        "domain": app_id,
                        "type": tp
                    }

                    for id in find_companies_by_artifacts([artifact]):
                        if id not in companyIds:
                            companyIds.append(id)
                    # companyIds.extend(find_companies_by_artifacts([artifact]))

                if len(companyIds) == 0:
                    num2 += 1
                elif len(companyIds) > 1:
                    num3 += 1
                else:
                    logger.info("%s matched company: %s   %s", bc["symbol"], companyIds, num4)
                    conn.update("update digital_token set companyId=%s where id=%s", companyIds[0], bc["id"])
                    num4 += 1

        break

    bccs = conn.query("select * from digital_token where companyId is not null and "
                      "(active is null or active !='N')")
    for bcc in bccs:
        links = []
        c = conn.get("select * from company where id=%s", bcc["companyId"])
        links.append('http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"])
        tag = conn.get("select * from company_tag_rel where companyId=%s and tagId=175747 and "
                       "(active is null or active!='N') limit 1",bcc["companyId"])

        line = "%s+++%s+++%s+++%s+++%s+++%s\n" % (bcc["symbol"], bcc["websites"],
                                        "|".join(links) if len(links) > 0 else " ",
                                        c["active"], getinfo(c["id"],c["corporateId"]),
                                             1 if tag is not None else 0)

        fp2.write(line)


    logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
    fp2.close()
    mongo.close()
    conn.close()
        # time.sleep(10*60)

