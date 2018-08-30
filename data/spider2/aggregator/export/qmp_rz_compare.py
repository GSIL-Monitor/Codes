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

sys.path.append(os.path.join(sys.path[0], '../../parser/company/itjuzi'))
# import parser_db_util
import itjuzi_helper

# logger
loghelper.init_logger("qmp_rz_compare", stream=True)
logger = loghelper.get_logger("qmp_rz_compare")

conn = db.connect_torndb()
mongo = db.connect_mongo()
companyname = u'company'
projectName = u'product'
roundName = u'jieduan'


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


def find_companyid(row):
    companyId = find_companies_by_full_name_corporate([row[companyname]]) if pd.notnull(row[companyname]) else []
    if len(companyId) > 0:
        return companyId[0]
    else:
        companyId = find_reference([row[projectName]])
        if companyId is None:
            companyId = find_qmp_company(row)
        return companyId


def find_qmp_company(row):
    companyId = None
    sc = conn.get(
        '''select * from source_company where source=13121 and (name=%s) order by companyId desc limit 1''',
        row[projectName])
    if sc is not None: companyId = sc['companyId']
    return companyId


def compare_select(source_funding, compare_fundings):
    flag = False

    # if len(update_deleteIds)>0: logger.info("Update deleteids: %s",update_deleteIds)
    for cfund in compare_fundings:
        # if source_funding["fundingDate"] is not None and source_funding["investment"] is not None:
        #     column = "fundingDate"
        #     column2 = "investment"
        #     if cfund[column] is not None and \
        #                     (cfund[column] - source_funding[column]).days > -30 and \
        #                     (cfund[column] - source_funding[column]).days < 30 and \
        #                     cfund[column2] is not None and cfund[column2] == source_funding[column2]:
        #         flag = True
        #         # logger.info("Company %s has Funding Date Same for %s/%s/%s and %s/%s/%s/%s", cfund['companyId'],
        #         #             source_funding["id"], source_funding["fundingDate"],
        #         #             source_funding["investment"],
        #         #             cfund["id"], cfund["fundingDate"], cfund["investment"], cfund["round"])

        if source_funding["fundingDate"] is not None:
            column = "fundingDate"
            if cfund[column] is not None and \
                    (cfund[column] - source_funding[column]).days > -30 and \
                    (cfund[column] - source_funding[column]).days < 30:
                flag = True
                # logger.info("Company %s has Funding Date Same for %s/%s/%s and %s/%s/%s/%s", cfund['companyId'],
                #             source_funding["id"], source_funding["fundingDate"],
                #             source_funding["investment"],
                #             cfund["id"], cfund["fundingDate"], cfund["investment"], cfund["round"])
        if source_funding["round"] is not None:
            column2 = "round"
            if cfund[column2] is not None and cfund[column2] > 0 and cfund[column2] == source_funding[column2]:
                flag = True
        # elif source_funding["investment"] is not None:
        #     column2 = "investment"
        #     if cfund[column2] is not None and cfund[column2] > 0 and cfund[column2] == source_funding[column2]:
        #         flag = True
        # logger.info("Company %s has Funding Date Same for %s/%s/%s and %s/%s/%s/%s", cfund['companyId'],
        #             source_funding["id"], source_funding["fundingDate"],
        #             source_funding["investment"],
        #             cfund["id"], cfund["fundingDate"], cfund["investment"], cfund["round"])

        if flag is True:
            break

    return flag


def abnormal(x):
    if pd.isnull(x.companyId): return '匹配不到公司'
    if pd.isnull(x.country) and pd.notnull(x.fundingDate):
        collection = mongo.raw.qmp_rz_parser
        if collection.find_one({'product': x.xiniuName}) is None and collection.find_one(
                {'company': x.xiniufullName}) is None:
            return '烯牛独家'
        else:
            return '其它'

    thirdTime = x[u'time'].strip()
    # if len(thirdTime) < 5: return '融资时间不对'

    try:
        thirdTime = datetime.datetime.strptime(thirdTime, '%Y.%m.%d')
    except:
        try:
            thirdTime = datetime.datetime.strptime(thirdTime, '%Y.%m')
        except:
            try:
                thirdTime = datetime.datetime.strptime(x[u'orderbyrztime'].strip(), '%Y%m%d')
            except:
                return '融资时间不对'

    # if x.fundingDate.year != thirdTime.year or x.fundingDate.month != thirdTime.month: return '融资时间不匹配'
    import re
    reg = re.findall(u'\d+[万亿]', x[u'money'])
    if len(reg) == 0:
        source_investment = None
    else:
        amout = reg[0][:-1]
        source_investment = float(amout) * 10000 if u'万' in x[u'money'] else float(amout) * 10000 * 10000

    roundstr = x[u'jieduan']
    if roundstr == "re-A轮":
        roundstr = "Pre-A"
    elif roundstr == "re-IPO":
        roundstr = "Pre-IPO"
    fundingRound, roundStr = itjuzi_helper.getFundingRound(unicode(roundstr))
    if fundingRound == 1011: fundingRound = 1010

    # print thirdTime,source_investment
    source_funding = {'id': 1, 'fundingDate': thirdTime, 'investment': source_investment, 'round': fundingRound}
    if pd.isnull(x['corporateId']): print x

    if compare_select(source_funding,
                      conn.query('select * from funding where corporateId=%s and (active="Y" or active is null)',
                                 x['corporateId'])) is False:
        xiniufunding = conn.get(
            'select * from funding where corporateId=%s and (active="Y" or active is null) order by round desc limit 1',
            x['corporateId'])

        xiniuRound = 0
        if xiniufunding is not None:
            xiniuRound = xiniufunding['round']
        else:
            return '烯牛无融资'

        if fundingRound > 0 and fundingRound > xiniuRound: return '企名片轮次靠后'

        return '烯牛轮次靠后'
    return '都匹配'


def illegal_df(df, columns):
    for c in df.columns:
        if c not in columns: continue

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

        # print 'c:', c
        df[c] = df.apply(illegal, axis=1)
    return df


def getFundingRound(roundStr):
    fundingRound = 0
    if roundStr.startswith("尚未获投"):
        fundingRound = 1000
        roundStr = "尚未获投"
    elif roundStr.startswith("种子"):
        fundingRound = 1010
        roundStr = "种子轮"
    elif roundStr.startswith("天使"):
        fundingRound = 1011
        roundStr = "天使轮"
    elif roundStr.startswith("Pre-A"):
        fundingRound = 1020
        roundStr = "Pre-A轮"
    elif roundStr.startswith("A+"):
        fundingRound = 1031
        roundStr = "A+轮"
    elif roundStr.startswith("A"):
        fundingRound = 1030
        roundStr = "A轮"
    elif roundStr.startswith("Pre-B"):
        fundingRound = 1039
        roundStr = "Pre-B"
    elif roundStr.startswith("B+"):
        fundingRound = 1041
        roundStr = "B+轮"
    elif roundStr.startswith("B"):
        fundingRound = 1040
        roundStr = "B轮"
    elif roundStr.startswith("C+"):
        fundingRound = 1051
        roundStr = "C轮"
    elif roundStr.startswith("C"):
        fundingRound = 1050
        roundStr = "C轮"
    elif roundStr.startswith("D"):
        fundingRound = 1060
        roundStr = "D轮"
    elif roundStr.startswith("E"):
        fundingRound = 1070
        roundStr = "E轮"
    elif roundStr.startswith("F"):
        fundingRound = 1080
        roundStr = "F轮"
    elif roundStr.startswith("Pre-IPO"):
        fundingRound = 1080
        roundStr = "Pre-IPO"
    elif roundStr.startswith("新三板"):
        fundingRound = 1105
        roundStr = "新三板"
    elif roundStr.startswith("定向增发"):
        fundingRound = 1106
        roundStr = "新三板定增"
    elif (roundStr.startswith("IPO") or roundStr.startswith("已上市")) and roundStr.find("IPO上市后") == -1:
        fundingRound = 1110
        roundStr = "上市"
    elif roundStr.startswith("已被收购") or roundStr.startswith("并购"):
        fundingRound = 1120
        roundStr = "并购"
    elif roundStr.startswith("战略投资") or roundStr.startswith("战略融资") or roundStr.startswith("IPO上市后"):
        fundingRound = 1130
        roundStr = "战略投资"
    elif roundStr.startswith("私有化"):
        fundingRound = 1140
        roundStr = "私有化"
    elif roundStr.startswith("债权融资"):
        fundingRound = 1150
        roundStr = "债权融资"
    elif roundStr.startswith("股权转让"):
        fundingRound = 1160
        roundStr = "股权转让"
    if roundStr.startswith("众筹"):
        fundingRound = 1009
        roundStr = "众筹"

    return fundingRound, roundStr


def getxiniuround(x):
    roundstr = x[roundName]
    if roundstr == "re-A轮":
        roundstr = "Pre-A"
    elif roundstr == "re-IPO":
        roundstr = "Pre-IPO"

    fundingRound, roundStr = getFundingRound(unicode(roundstr))
    return unicode(roundStr)


def run_api(conn, mongo, startDate, endDate=None):
    # startDate = '2018-1-1'
    # endDate = '2018-6-25'
    sql = '''
    select distinct f.id fid,c.corporateId,f.round
       ,case when f.source=69002 then f.gsDetectdate when f.publishDate is not null then f.publishDate  else  f.fundingdate end publishDate
       ,f.fundingDate,c.id as companyID,c.name as companyName,
        case when co.locationId>370 then '国外' else '国内' end as location
        ,a.vipTags,a.tags,
        case when co.round=1000 then "尚未获投"
        when co.round=1010 then "种子轮"
        when co.round=1011 then "天使轮"
        when co.round=1020 then "Pre-A轮"
        when co.round=1030 then "A轮"
        when co.round=1031 then "A+轮"
        when co.round=1039 then "Pre-B"
        when co.round=1040 then "B轮"
        when co.round=1041 then "B+轮"
        when co.round=1050 then "C轮"
        when co.round=1051 then "C+轮"
        when co.round=1060 then "D轮"
        when co.round=1070 then "E轮"
        when co.round=1080 then "F轮"
        when co.round=1090 then "后期阶段"
        when co.round=1100 then "Pre-IPO"
        when co.round=1105 then "新三板"
        when co.round=1106 then "新三板定增"
        when co.round=1110 then "上市"
        when co.round=1120 then "并购"
        when co.round=1140 then "私有化"
        when co.round=1150 then "债权融资"
        when co.round=1160 then "股权转让"
        when co.round=1130 then "战略投资"
        when co.round=1111 then "Post-IPO" 
        when co.round=1131 then "战略合并"          
        when co.round=1009 then "众筹"          
        when co.round=1109 then "ICO"          
        when co.round=1112 then "定向增发"          
         end as CompanyRoundDesc,
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
        when f.round=1130 then "战略投资"
        when f.round=1111 then "Post-IPO" 
        when f.round=1131 then "战略合并"   
        when f.round=1009 then "众筹"          
        when f.round=1109 then "ICO"          
        when f.round=1112 then "定向增发"  
         end as roundDesc,
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
        when f.currency=3080 then "AUD"
        when f.currency=3090 then "IDR"
         end as currency,

        f.precise,f.investorsRaw,f.newsId,
        l.locationName,co.establishDate

        ,case when f.investorsRaw like "%%红杉%%" then "红杉"
        when f.investorsRaw like "%%经纬%%" then "经纬"
        when f.investorsRaw like "%%IDG%%" then "IDG"
        when f.investorsRaw like "%%真格%%" then "真格"
        when f.investorsRaw like "%%创新工场%%" then "创新工场"
        when f.investorsRaw like "%%北极光%%" then "北极光"
        when f.investorsRaw like "%%纪源资本%%" then "纪源资本"
        when f.investorsRaw like "%%险峰长青%%" then "险峰长青"
        when f.investorsRaw like "%%蓝驰创投%%" then "蓝驰创投"
        when f.investorsRaw like "%%金沙江创投%%" then "金沙江创投"
        when f.investorsRaw like "%%贝塔斯曼%%" then "贝塔斯曼"
        when f.investorsRaw like "%%华创资本%%" then "华创资本"
        when f.investorsRaw like "%%晨兴资本%%" then "晨兴资本"
        when f.investorsRaw like "%%光速中国%%" then "光速中国"
        when f.investorsRaw like "%%启明创投%%" then "启明创投"
        when f.investorsRaw like "%%DCM%%" then "DCM"
        when f.investorsRaw like "%%顺为资本%%" then "顺为资本"
        when f.investorsRaw like "%%赛富%%" then "赛富"
        when f.investorsRaw like "%%深创投%%" then "深创投"
        when f.investorsRaw like "%%达晨创投%%" then "达晨创投"
        when f.investorsRaw like "%%峰瑞资本%%" then "峰瑞资本"
        when f.investorsRaw like "%%戈壁%%" then "戈壁"
        when f.investorsRaw like "%%联想之星%%" then "联想之星"
        when f.investorsRaw like "%%梅花%%" then "梅花"
        when f.investorsRaw like "%%英诺%%" then "英诺"
        when f.investorsRaw like "%%明势资本%%" then "明势资本"  end as famous
        ,c.brief,c.description,c.code companyCode,i.investorName
        ,u.username

        from company c join funding f on c.id=f.companyId
        join corporate co on c.corporateId=co.id
        left join location l on co.locationid=l.locationid
        left join
        (
         select  f.id fid,group_concat(i.name) as investorName
         from funding  f
         left join funding_investor_rel r on r.fundingid=f.id
         left join investor i on r.investorId=i.id
         where  (f.active = 'Y' or f.active is null)
         group by f.id
         ) i on i.fid=f.id

        join
        (select c.name,c.code,c.id,group_concat(t.name) as tags ,group_concat(t1.name order by r.confidence desc) as vipTags
        from company c
        left join company_tag_rel r on r.companyId=c.id and (r.active = 'Y' or r.active is null)
        left join tag t on r.tagId=t.id and (t.active = 'Y' or t.active is null) and t.type in (11010,11011,11100)
        left join tag t1 on r.tagId=t1.id and (t1.active = 'Y' or t1.active is null) and t1.type = 11012
        where (c.active = 'Y' or c.active is null)
        group by c.name,c.code
        order by t.type desc
        ) a on a.id=c.id

        left join user u on u.id=f.modifyUser 

        where
        (c.active = 'Y' or c.active is null) and (f.active = 'Y' or f.active is null)
        -- YEARWEEK(date_format(f.publishDate ,'%%Y-%%m-%%d'),1) = YEARWEEK(now(),1)-1
        -- DATE_FORMAT( f.publishDate, '%%Y'  ) = DATE_FORMAT( CURDATE() , '%%Y'  )
        -- DATE_FORMAT( f.modifyTime, '%%Y-%%m'  ) = DATE_FORMAT( CURDATE() , '%%Y-%%m'  )
        -- (DATE_FORMAT( f.modifyTime, '%%Y'  ) >= '2018' or DATE_FORMAT( f.createTime, '%%Y'  ) >= '2018'  )
        -- (c.name like '%%乐视%%')
        -- (f.investorsRaw like '%%乐视%%' or i.investorName like '%%乐视%%' or c.id in (6400, 156236, 26244, 14550, 25565, 211867, 114194, 3476, 133550, 123671, 59289, 203547, 3356, 23130, 6944, 2928, 45773, 206499, 117702, 136793, 1191, 13609, 9770, 169772, 5038, 28207, 153497, 18019, 44338, 9843, 12150, 13239, 210360, 46361, 22459, 169404, 136638, 10178, 169590, 15174, 95598, 27976, 70092, 19191, 3788, 133602, 125518, 77775, 123088, 12113, 134995, 64213, 124886, 142408, 169177, 95578, 19293, 181214, 11488, 1633, 10082, 18531, 151325, 122213, 27110, 158908, 6506, 30187, 48878, 195184, 7026, 131571, 6984, 19189, 125302, 9833, 147192, 203960, 60156, 136547, 18942))
        -- (f.modifyTime>='2015-1-1'  or f.createTime>='2015-1-1')
        order by c.id,f.id
    '''
    results = conn.query(sql)

    df = pd.DataFrame(results)
    fids = [i['fid'] for i in results]

    collection = mongo.company.funding_news
    results2 = list(collection.find({'funding_id': {'$in': fids}}))

    df2 = pd.DataFrame(results2)
    dfMerge = pd.merge(df, df2, how='left', left_on='fid', right_on='funding_id')

    def process_date(row):
        if pd.isnull(row.publishDate):
            if pd.notnull(row.date) and isinstance(row.date, float):
                return pd.to_datetime(str(int(row.date))[:-3], unit='s')
            else:
                return pd.to_datetime(row.date)
        else:
            # return row.publishDate + datetime.timedelta(hours=8)
            return row.publishDate

    dfMerge['publishDateMerge'] = dfMerge.apply(process_date, axis=1)

    startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    dfMerge2 = dfMerge[dfMerge.publishDateMerge >= startDate]

    if endDate != '':
        endDate = datetime.datetime.strptime(endDate, '%Y-%m-%d')
        dfMerge2 = dfMerge2[dfMerge2.publishDateMerge < endDate + datetime.timedelta(days=1)]

    def investment_rmb(row):
        # if row.currency is not None and pd.notnull(row.currency):
        try:
            if row.currency == 'USD':
                return int(row.investment) * 6.3378
            elif row.currency == 'RMB':
                return int(row.investment)
        except:
            return None

    # rank by invenstment
    dfMerge2['investment_rmb'] = dfMerge2.apply(investment_rmb, axis=1)
    dfMerge2['sector'] = dfMerge2.apply(lambda x: x['vipTags'].split(',')[0] if x['vipTags'] is not None else '',
                                        axis=1)

    dfMerge2 = dfMerge2.sort_values(by=['companyID', 'fundingDate'], ascending=[1, 0])
    dfMerge2['row'] = dfMerge2.groupby('companyID')['fundingDate'].rank(ascending=0, method='first')

    columns = ['publishDateMerge', 'fundingDate', 'corporateId', 'companyID', 'companyCode', 'companyName',
               'companyStatus', 'location',
               'vipTags', 'sector', 'tags', 'CompanyRoundDesc',
               'roundDesc', 'investment', 'currency', 'investment_rmb', 'precise', 'investorsRaw', 'investorName',
               'newsId',
               'date', 'link', 'locationName', 'establishDate', 'famous', 'row', 'brief', 'description', 'username',
               'investmentDetail']

    def investmentDetail(row):
        currencyMap = {'RMB': '¥', 'USD': '$'}
        currency = currencyMap.get(row.currency)
        investment = row['investment']
        if pd.isnull(investment) or investment == 0:
            investmentFinal = '金额未知'
            currency = ''
        else:
            investment = int(investment)
            if row.precise == 'Y' or row.precise is None:
                if investment >= 10000:
                    investmentFinal = '%g亿' % (float(investment) / 10000)
                else:
                    investmentFinal = '%s万' % investment
            else:
                if investment >= 10000:
                    investmentFinal = '数亿'
                elif investment >= 1000:
                    investmentFinal = '数千万'
                elif investment >= 100:
                    investmentFinal = '数百万'
                elif investment >= 10:
                    investmentFinal = '数十万'

        investmentDetail = '%s %s%s\n%s' % (
            row.roundDesc, currency, investmentFinal, row.investorsRaw if pd.notnull(row.investorsRaw) else '')
        return investmentDetail

    dfMerge2['investmentDetail'] = dfMerge2.apply(investmentDetail, axis=1)

    def illegal(row):
        import re
        content = row.description
        if content is not None:
            ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
            content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
        return content

    dfMerge2['description'] = dfMerge2.apply(illegal, axis=1)
    dfMerge3 = dfMerge2[dfMerge2.location == '国内']

    columns = ['publishDateMerge', 'fundingDate', 'companyID', 'companyCode', 'companyName',
               'location',
               'sector', 'CompanyRoundDesc',
               'roundDesc', 'investment', 'currency', 'investment_rmb', 'precise', 'investorsRaw',
               'locationName', 'establishDate']

    # def illegal_df(df):
    #     for c in df.columns:
    #         def illegal(row):
    #             import re
    #             content = row[c]
    #             if content is not None:
    #                 ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    #                 # print 'content:',c,content
    #                 try:
    #                     content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
    #                 except:
    #                     pass
    #             return content
    #
    #         # print 'c:',c
    #         df[c] = df.apply(illegal, axis=1)
    #     return df
    #
    # dfMerge2 = illegal_df(dfMerge2)

    # dfMerge2.to_excel('funding_news_report.xlsx', sheet_name=u'明细', index=0, columns=columns, encoding="utf-8")

    return dfMerge2, columns


def run(output, startDate, endDate):
    # startDate='20080101' endDate='20130101'  ==  2008 to 2012
    collection = mongo.raw.qmp_rz_parser
    df = pd.DataFrame(list(collection.find({'orderbyrztime': {'$gte': startDate, '$lt': endDate}})))

    df[projectName] = df.apply(lambda x: str(x[projectName]).strip().replace("(", "（").replace(")", "）"), axis=1)
    df[companyname] = df.apply(lambda x: str(x[companyname]).strip().replace("(", "（").replace(")", "）"), axis=1)

    df['companyId'] = df.apply(find_companyid, axis=1)
    companyId = list(df[pd.notnull(df.companyId)].companyId)


    startDate = datetime.datetime.strptime(startDate, '%Y%m%d').strftime("%Y-%m-%d")
    endDate = datetime.datetime.strptime(endDate, '%Y%m%d').strftime("%Y-%m-%d")

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
         end as currency
         ,case when f.publishdate is not null then f.publishdate else f.fundingdate end fundingdateMerge,

        f.precise,
                case when co.locationId>370 then 'EN' else 'CN' end as location,co.fullName xiniufullName

    from company c left join funding f on c.id=f.companyId  and (f.active is null or f.active='Y')
    join corporate co on c.corporateid=co.id
    where c.id in %s or (case when f.publishdate is not null then f.publishdate else f.fundingdate end>=%s and case when f.publishdate is not null then f.publishdate else f.fundingdate end<%s)  -- and f.round not in (1120,1110,1105,1106))
    order by f.fundingdate desc
    ''', companyId, startDate, endDate)  # todo!

    df2 = pd.DataFrame(results)
    df3 = pd.merge(df, df2, on='companyId', how='outer')
    df3['row'] = df3.groupby(['id', projectName, u'time'])['fundingDate'].rank(ascending=False, method='first')
    df3 = df3[(df3.row == 1) | (pd.isnull(df3.row))]

    df3[u'可疑'] = df3.apply(abnormal, axis=1)
    df3[u'country'] = df3.apply(lambda x: x.country if pd.notnull(x.country) else x.location, axis=1)

    columns = u'可疑 id country detail	product	company	hangye1	hangye2	yewu	province	jieduan	time    orderbyrztime	money   tzr	companyId	corporateId	active	code	xiniuName	roundDesc	fundingdateMerge	investment	currency	precise'.split()

    df3 = illegal_df(df3, columns)

    df4 = df3[(df3[u'可疑'] != u'其它')]

    df4.drop(['_id'], axis=1).to_excel(output, index=0, columns=columns)


def round_compare(out, startDate, endDate):
    # 双方轮次分布统计，时间段内
    collection = mongo.raw.qmp_rz_parser
    df = pd.DataFrame(list(collection.find({'orderbyrztime': {'$gte': startDate, '$lt': endDate}})))
    df = df[df.country == 'CN']

    df['round_qmp'] = df.apply(getxiniuround, axis=1)
    pivot1 = df.groupby('round_qmp')[roundName].count().to_frame().reset_index()


    startDate = datetime.datetime.strptime(startDate, '%Y%m%d').strftime("%Y-%m-%d")
    endDate = (datetime.datetime.strptime(endDate, '%Y%m%d') + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    dfMerge3, _ = run_api(conn, mongo, startDate, endDate)
    dfMerge3 = dfMerge3[dfMerge3.location == '国内']


    pivot2 = dfMerge3.groupby(['round', 'roundDesc'])['companyCode'].count().to_frame().reset_index()
    df3 = pd.merge(pivot1, pivot2, how='outer', left_on='round_qmp', right_on='roundDesc')
    df3['轮次'] = df3.apply(lambda x: x.roundDesc if pd.notnull(x.roundDesc) else x.round_qmp, axis=1)
    df3 = df3.sort_values(by=['round'], ascending=[1])

    df3 = df3.rename(columns={roundName: '企名片', 'companyCode': '烯牛'})
    df3.to_excel(out, index=0, columns='轮次	企名片	烯牛'.split())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        output = sys.argv[1]
        startDate = sys.argv[2]
        endDate = sys.argv[3]
        type = sys.argv[4]

        if type == 1:
            run(output, startDate, endDate)
        else:
            round_compare(output, startDate, endDate)
    else:
        run('export.xlsx', '20180701', '20180801')
        round_compare('export2.xlsx', '20180701', '20180801')
