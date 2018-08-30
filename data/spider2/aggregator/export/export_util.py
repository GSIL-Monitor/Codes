# -*- coding: utf-8 -*-

import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(sys.path[0], '../../../util'))
sys.path.append(os.path.join(sys.path[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(sys.path[0], '../util'))
# import helper
import pandas as pd
import simhash, datetime

# logger
loghelper.init_logger("blockchain_export", stream=True)
logger = loghelper.get_logger("blockchain_export")

conn = db.connect_torndb()
mongo = db.connect_mongo()


# 简单version
def getinfo_lite(companyId, corporateId):
    if pd.isnull(companyId) or pd.isnull(corporateId): return ''
    info = ""
    verfyinfo = ""
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    cor = conn.query("select * from corporate where (active is null or active='Y')"
                     " and verify is null and id=%s", corporateId)
    if len(cor) > 0:  return '未完全 verify'
    comp = conn.query("select * from company where (active is null or active='Y')"
                      " and verify is null and id=%s", companyId)
    if len(comp) > 0:  return '未完全 verify'
    fundings = conn.query("select * from funding f left join company c on f.companyId=c.id "
                          "where f.companyId=%s and (c.active is null or c.active='Y')  and "
                          "(f.active is null or f.active='Y') and f.verify is null", companyId)
    if len(fundings) > 0:  return '未完全 verify'
    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                           "and verify is null", companyId)
    if len(artifacts) > 0:  return '未完全 verify'
    members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                         "where cmr.companyId=%s and m.verify is null and "
                         "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                         "(cmr.active is null or cmr.active='Y')", companyId)
    if len(members) > 0:  return '未完全 verify'
    comaliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')"
                            " and verify is null", companyId)
    if len(comaliases) > 0:  return '未完全 verify'
    corpaliaes = conn.query("select * from corporate_alias where (active is null or active='Y') "
                            "and verify is null  and corporateId=%s", corporateId)
    if len(corpaliaes) > 0:  return '未完全 verify'
    comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                         "(active is null or active='Y') and verify is null", companyId)
    if len(comrecs) > 0:  return '未完全 verify'

    desc = mongo.company.modify.find_one({'companyId': companyId, 'sectionName': 'desc'})
    if desc is None:  return '未完全 verify'

    conn.close()
    if len(verfyinfo) > 0:
        info = verfyinfo + "未verify"
    else:
        info = "都verify"
    # logger.info("company: %s->%s", companyId, info)
    return info


def getinfo_full(companyId, corporateId):
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
    fundings = conn.query("select * from funding f left join company c on f.companyId=c.id "
                          "where f.companyId=%s and (c.active is null or c.active='Y')  and "
                          "(f.active is null or f.active='Y') and f.verify is null", companyId)
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

    for short_name in shortnames:
        if short_name is None or short_name.strip() == "":
            continue
        short_name = short_name.strip()

        logger.info("short_name: %s", short_name)
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
            candidate_company_ids.append(company_id)
            break

    # return company_ids
    if len(candidate_company_ids) > 0:
        return candidate_company_ids[0]
    else:
        return None

def illegal_df(df):
    for c in df.columns:
        def illegal(row):
            import re
            content = row[c]
            if content is not None:
                ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
                # print 'content:',c,content
                try:
                    content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
                except:
                    pass
            return content

        # print 'c:',c
        df[c] = df.apply(illegal, axis=1)
    return df


def investment_rmb(row):
    # if row.currency is not None and pd.notnull(row.currency):
    try:
        if row.currency == 'USD':
            return int(row.investment) * 6.3333
        elif row.currency == 'RMB':
            return int(row.investment)
    except:
        return None