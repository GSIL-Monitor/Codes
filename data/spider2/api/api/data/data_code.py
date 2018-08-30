# -*- coding: utf-8 -*-
import pandas as pd
import datetime


def run(conn, mongo, startDate, endDate=None):
    # startDate = '2018-4-1'
    # endDate = '2018-7-1'
    sql = '''
    select distinct f.id fid,c.corporateId
       ,case when f.source=69002 then f.gsDetectdate else f.publishDate end publishDate
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
         and (r.active = 'Y' or r.active is null)
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
        and
        -- YEARWEEK(date_format(f.publishDate ,'%%Y-%%m-%%d'),1) = YEARWEEK(now(),1)-1
        -- DATE_FORMAT( f.publishDate, '%%Y'  ) = DATE_FORMAT( CURDATE() , '%%Y'  )
        -- DATE_FORMAT( f.modifyTime, '%%Y-%%m'  ) = DATE_FORMAT( CURDATE() , '%%Y-%%m'  )
        (DATE_FORMAT( f.modifyTime, '%%Y'  ) >= '2018' or DATE_FORMAT( f.createTime, '%%Y'  ) >= '2018'  )
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

    # dfMerge2.to_excel('funding_news_report.xlsx', sheet_name=u'明细', index=0,
    #                   columns=columns, encoding="utf-8")

    return dfMerge2, columns


rmap = {
    1000: '未融资',
    1010: '天使轮',
    1011: '天使轮',
    1020: 'pre-A',
    1030: 'A',
    1031: 'A+',
    1039: 'Pre-B',
    1040: 'B',
    1041: 'B+',
    1050: 'C',
    1060: 'D',
    1070: 'E',
    1080: 'F',
    1090: '后期阶段',
    1100: 'pre-IPO',
    1105: '新三板',
    1106: '新三板定增',
    1110: 'IPO',
    1120: '被收购',
    1130: '战略投资',
    1140: '私有化',
    1150: '债权融资',
    1160: '股权转让',
}

currentmap = {
    3010: "美元",
    3020: "人民币",
    3030: "新加坡元",
    3040: "欧元",
    3050: "英镑",
    3060: "日元",
    3070: "港币",
    3080: "澳元",
}


def get_amount(amount, precise):
    def pp(value):
        if value is None:
            return ''
        if value >= 1 and value < 10:
            return '数'
        elif value >= 10 and value < 100:
            return '数十'
        elif value >= 100 and value < 1000:
            return '数百'
        elif value >= 1000 and value < 10000:
            return '数千'
        else:
            return ''

    if amount is None:
        return "金额不详"
    elif amount == 0:
        return "金额不详"
    elif float(amount) / float(100000000) > 1:
        if precise is None or precise == 'Y':
            return str(float(amount) / float(100000000)) + '亿'
        else:
            return pp(float(amount) / float(100000000)) + '亿'
    elif float(amount) / float(10000) > 1:
        if precise is None or precise == 'Y':
            return str(float(amount) / float(10000)) + '万'
        else:
            return pp(float(amount) / float(10000)) + '万'
    else:
        return "金额不详"


def extract_sf(conn, date):
    rd = []
    # conn = db.connect_torndb()
    # sourceCompanyIds = []
    # rd["IT桔子"] = []
    # rd["36氪"] = []
    source_fundings = conn.query("select * from source_funding where "
                                 "fundingDate>=%s and fundingDate<%s", date, date + datetime.timedelta(days=1))
    for source_funding in source_fundings:
        # if source_funding["sourceCompanyId"] not in sourceCompanyIds:
        #     sourceCompanyIds.append(source_funding["sourceCompanyId"])

        # for sourceCompanyId in sourceCompanyIds:
        rds = {}
        sourceCompanyId = source_funding["sourceCompanyId"]
        source_company = conn.get("select * from source_company where id=%s and (active is null or active='Y')",
                                  sourceCompanyId)
        if source_company is None: continue
        if source_company["source"] not in [13022, 13030]: continue

        investors = [ii["name"] for ii in conn.query("select i.name from source_funding_investor_rel fir join "
                                                     "source_investor i "
                                                     "on fir.sourceInvestorId=i.id where fir.sourceFundingId=%s",
                                                     source_funding["id"])]
        amount = get_amount(source_funding["investment"], source_funding["precise"])
        fi = {
            "date": str(source_funding["fundingDate"].date()) if source_funding["fundingDate"] is not None else "",
            "round": rmap[int(source_funding["round"])] if (source_funding["round"] is not None and
                                                            rmap.has_key(int(source_funding["round"]))) else "",
            "amount": amount,
            "currency": currentmap[int(source_funding["currency"])] if (source_funding["currency"] is not None and
                                                                        currentmap.has_key(
                                                                            int(source_funding["currency"]))) else "",
            "investor": ",".join(investors)

        }
        rds.update(fi)
        if source_company["companyId"] is None:
            rds["name"] = source_company["name"]
            rds["code"] = "None"

        else:
            company = conn.get("select * from company where id=%s", source_company["companyId"])
            rds["name"] = company["name"]
            rds["code"] = company["code"]
        if source_company["source"] == 13022:
            # rd["36氪"].append(rds)
            rds["source"] = "36氪"
        else:
            # rd["IT桔子"].append(rds)
            rds["source"] = "IT桔子"
        rd.append(rds)

    conn.close()
    return rd


def run2(conn, mongo, startDate, endDate, param):
    # startDate = '2018-4-1'
    # endDate = '2018-7-1'
    sql = '''
    select distinct f.id fid,c.corporateId
       ,case when f.source=69002 then f.gsDetectdate else f.publishDate end publishDate
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
         and (r.active = 'Y' or r.active is null)
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
        and
        (DATE_FORMAT( f.modifyTime, '%%Y'  ) >= %s or DATE_FORMAT( f.createTime, '%%Y'  ) >= %s  )
    '''

    if param.has_key('location'):
        location = '国内' if param['location'] == 'CN' else '国外'
        sql += "and case when co.locationId>370 then '国外' else '国内' end='%s'" % location
    if param.has_key('round'):
        sql += 'and f.round in (%s)' % ','.join(['"%s"' % t for t in param['round']])
    if param.has_key('tag') and param['tag'].strip() != '':
        tag = param['tag'].split('、')

        sql += '''and c.id in (
        select distinct c.id
        from company c 
         join company_tag_rel r on r.companyId=c.id  and (r.active = 'Y' or r.active is null)
         join tag t on r.tagId=t.id and (t.active = 'Y' or t.active is null)
         where t.name in (%s)
        )''' % ','.join(['"%s"' % t for t in tag])
    if param.has_key('investor') and param['investor'].strip() != '':
        investorId = param['investor'].split('、')
        sql += '''and 
            f.id in (select distinct f.id
            from funding  f
             left join funding_investor_rel r on r.fundingid=f.id
             left join investor i on r.investorId=i.id
             where  (f.active = 'Y' or f.active is null) 
            and r.investorId in (%s)
            ) ''' % ','.join(investorId)

    results = conn.query(sql, startDate[:4], startDate[:4])

    df = pd.DataFrame(results)
    fids = [i['fid'] for i in results]

    collection = mongo.company.funding_news
    results2 = list(collection.find({'funding_id': {'$in': fids}}))

    if len(results2) > 0:
        df2 = pd.DataFrame(results2)
        dfMerge = pd.merge(df, df2, how='left', left_on='fid', right_on='funding_id')
    else:
        dfMerge = df
        dfMerge['date'] = None

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

    dfMerge2 = illegal_df(dfMerge2)

    # dfMerge2.to_excel('funding_news_report.xlsx', sheet_name=u'明细', index=0,columns=columns, encoding="utf-8")

    return dfMerge2, columns

# run2(conn, mongo, '2018-1-1', '2018-08-12', {"startDate": "2018-08-06", "endDate": "2018-08-12", "location": "CN"})
# run2(conn, mongo, '2018-7-1', '2018-08-12', {"investor": "117、139", "startDate": "2018-08-14", "endDate": "2018-08-14"})
# run2(conn, mongo, '2018-7-1', '2018-08-12',{"investor": "117、139", 'tag': u'区块链、人工智能', "startDate": "2018-08-14", "endDate": "2018-08-14"})
# run2(conn, mongo, '2018-7-1', '2018-08-12',{"investor": "117、139", "location": "CN", 'tag': u'区块链、人工智能', "startDate": "2018-08-14", "endDate": "2018-08-14"})
# run2(conn, mongo, '2018-8-1', '2018-08-12',{"round": ['1010','1011'], " qlocation": "CN", "startDate": "2018-08-14", "endDate": "2018-08-14"})
