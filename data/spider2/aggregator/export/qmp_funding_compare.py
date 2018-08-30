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

sys.path.append(os.path.join(sys.path[0], '../export'))
import export_util
import pandas as pd

# logger
loghelper.init_logger("lagou_export", stream=True)
logger = loghelper.get_logger("lagou_export")

conn = db.connect_torndb()
mongo = db.connect_mongo()

def run():
    df = pd.read_excel(u'QMP.xlsx')

    projectColName = u'项目名称'

    df[projectColName] = df.apply(
        lambda x: str(x[projectColName]).strip().replace("(", "（").replace(")", "）").replace(" ", ""),
        axis=1)

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

    def find_companyid(row):
        # companyId = find_companies_by_full_name_corporate([row.companyname])
        companyId = []
        if len(companyId) > 0:
            return companyId[0]
        else:
            return find_reference([row[projectColName], row[projectColName].lower(), row[projectColName].upper()])

    df['companyId'] = df.apply(find_companyid, axis=1)

    comapnyIds = list(df[pd.notnull(df.companyId)].companyId)

    results = conn.query('''select c.id companyId,c.corporateId,c.code,c.name xiniuName,c.active
    from company c 
    where c.id in %s
    ''', comapnyIds)

    df2 = pd.DataFrame(results)
    df3 = pd.merge(df, df2, on='companyId', how='left')

    # 简单
    def getinfo(companyId, corporateId):
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

    df3['verify'] = df3.apply(lambda x: getinfo(x.companyId, x.corporateId), axis=1)
    df3 = illegal_df(df3)
    df3.to_excel('export.xlsx', index=0)


def yitai_excel_funding():
    import pandas as pd
    df = pd.read_excel(u'企名片投融资对比合并.xlsx')

    projectName = u'产品'
    df[projectName] = df.apply(
        lambda x: str(x[projectName]).strip().replace("(", "（").replace(")", "）").replace(" ", ""),
        axis=1)

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

    df['companyId'] = df.apply(lambda row: find_reference([row[projectName]]), axis=1)

    companyId = list(df[pd.notnull(df.companyId)].companyId)

    results = conn.query('''select distinct  c.id companyId,c.corporateId,c.code,c.name xiniuName,c.active ,f.fundingDate,case when f.round=1000 then "尚未获投"
        when f.round=1010 then "种子轮"
        when f.round=1011 then "天使轮"
        when f.round=1020 then "Pre-A轮"
        when f.round=1030 then "A轮"
        when f.round=1031 then "A+轮"
        when f.round=1039 then "Pre-B"
        when f.round=1040 then "B轮"
        when f.round=1041 then "B+轮"
        when f.round=1050 then "C轮"
        when f.round=1051 then "C+轮"
        when f.round=1060 then "D轮"
        when f.round=1070 then "E轮"
        when f.round=1080 then "F轮"
        when f.round=1090 then "后期阶段"
        when f.round=1100 then "Pre-IPO"
        when f.round=1105 then "新三板"
        when f.round=1106 then "新三板定增"
        when f.round=1110 then "上市"
        when f.round=1120 then "并购"
        when f.round=1140 then "私有化"
        when f.round=1150 then "债权融资"
        when f.round=1160 then "股权转让"
        when f.round=1130 then "战略投资"
        when f.round=1111 then "Post-IPO" 
        when f.round=1131 then "战略合并"   
        when f.round=1009 then "众筹"          
        when f.round=1109 then "ICO"          
        when f.round=1112 then "定向增发"  
         end as roundDesc,f.investment/10000 investment,

        case when f.currency=3010 then "USD"
        when f.currency=3020 then "RMB"
        when f.currency=3030 then "SGD"
        when f.currency=3040 then "EUR"
        when f.currency=3050 then "GBP"
        when f.currency=3060 then "JPY"
        when f.currency=3070 then "HKD"
               when f.currency=3080 then "AUD"
        when f.currency=3090 then "IDR"
         end as currency,

        f.precise
    from company c left join funding f on c.id=f.companyId
    where c.id in %s
    and (f.active is null or f.active='Y')
    order by f.fundingdate desc
    ''', companyId)

    df2 = pd.DataFrame(results)
    df3 = pd.merge(df, df2, on='companyId', how='left')
    df3['row'] = df3.groupby([u'序号', u'产品', u'最近融资时间'])['fundingDate'].rank(ascending=False, method='first')
    df3 = df3[(df3.row == 1) | (pd.isnull(df3.row))]

    # 简单
    def getinfo(companyId, corporateId):
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

    df3['verify'] = df3.apply(lambda x: getinfo(x.companyId, x.corporateId) if x.companyId > 0 else '', axis=1)

    # df3 = illegal_df(df3)

    def abnormal(x):
        if pd.isnull(x.companyId): return '匹配不到公司'

        thirdTime = x[u'最近融资时间']
        if len(thirdTime) < 5: return '融资时间不对'

        try:
            thirdTime = datetime.datetime.strptime(thirdTime, '%Y.%m.%d')
        except:
            try:
                thirdTime = datetime.datetime.strptime(thirdTime, '%Y.%m')
            except:
                return '融资时间不对'

        if x.fundingDate.year != thirdTime.year or x.fundingDate.month != thirdTime.month: return '融资时间不匹配'

    df3[u'可疑'] = df3.apply(abnormal, axis=1)

    df3.to_excel('export.xlsx', index=0)