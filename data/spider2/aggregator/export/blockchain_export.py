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
import export_util

# logger
loghelper.init_logger("blockchain_export", stream=True)
logger = loghelper.get_logger("blockchain_export")

conn = db.connect_torndb()
mongo = db.connect_mongo()


def blockchain_export(type=1):
    sql = '''select distinct c.id companyId,c.name,c.code,c.corporateId
    ,co.establishdate,
        case when f.round=1000 then "尚未获投"
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
        when f.round=1130 then "战略投资" end as roundDesc,f.fundingDate,f.id fundingId,
        case when c.companyStatus=2010 then "正常" 
        when c.companyStatus=2015 then "融资中" 
        when c.companyStatus=2020 then "已关闭" 
        when c.companyStatus=2025 then "停止更新"  end companyStatus,
        f.investment/10000 investment,

        case when f.currency=3010 then "USD"
        when f.currency=3020 then "RMB"
        when f.currency=3030 then "SGD"
        when f.currency=3040 then "EUR"
        when f.currency=3050 then "GBP"
        when f.currency=3060 then "JPY"
        when f.currency=3070 then "HKD"
        when f.currency=3080 then "AUD" end as currency,

        f.precise,f.investorsRaw
        ,i.name as investorName,        case when co.locationId>370 then '国外' else '国内' end as location


        from company c join corporate co on co.id=c.corporateid
        left join company_tag_rel r on r.companyId=c.id  and (r.active = 'Y' or r.active is null)
        left join tag t on r.tagId=t.id and (t.active = 'Y' or t.active is null) and t.type in (11010,11011)
        left join funding f on c.id=f.companyId and (f.active='Y' or f.active is null) 
        left join funding_investor_rel r2 on r2.fundingid=f.id
        left join investor i on r2.investorId=i.id
        where (c.active != 'N' or c.active is null) 
        and r.tagId=175747
        order by f.fundingdate desc
        '''

    results = conn.query(sql)

    logger.info('mysql returns %s results', len(results))

    import pandas as pd
    df = pd.DataFrame(results)
    df['row'] = df.groupby('companyId')['fundingDate'].rank(ascending=0, method='first')

    if type == 1:
        df2 = df[(df.row == 1) | pd.isnull(df.row)]
        df2['verify'] = df.apply(lambda x: export_util.getinfo_lite(x.companyId, x.corporateId), axis=1)
        df2[u'有融资'] = df.apply(lambda x: True if x.fundingId > 0 else False, axis=1)
        columns = ["code", "name", 'location', "companyStatus", "establishdate", "roundDesc", u'有融资', "fundingId",
                   "fundingDate", 'verify']
    else:
        df2 = df

        # rank by invenstment
        df2['investment_rmb'] = df2.apply(export_util.investment_rmb, axis=1)
        columns = ["code", "name", 'location', "companyStatus", "establishdate", "roundDesc", "fundingId",
                   "fundingDate",
                   "investment", "currency", 'investment_rmb', "precise", "investorsRaw", 'investorName']
    df2.to_excel('export.xlsx', index=0, columns=columns)

# sql 统计数量
'''
select count(distinct c.id)
-- select c.code,r.active
from company c
    left join company_tag_rel r on r.companyId=c.id   and (r.active = 'Y' or r.active is null)
    left join tag t on r.tagId=t.id and (t.active = 'Y' or t.active is null) and t.type in (11010,11011)
--    join funding f on c.id=f.companyId and (f.active='Y' or f.active is null) 
    where r.tagId=175747
    and (c.active != 'N' or c.active is null) 

'''

# type : 1.公司去重 2.融资详情
if __name__ == '__main__':
    blockchain_export()
