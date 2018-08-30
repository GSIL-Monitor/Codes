# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util2'))
# import parser_mongo_util

import pandas as pd

# logger
loghelper.init_logger("amac_fund_parser", stream=True)
logger = loghelper.get_logger("amac_fund_parser")

SOURCE = 13631  # amac fund
TYPE = 36001  # 公司信息


def run():
    # 1.investName and id  df1    investorName  investorId
    # 1.第三方的 df2       investorName               investorAlias
    # 2.我们的 inventor where invetorid in 1 df3       investorId                    name
    # 3.outer join
    # 4.merge amac

    investorList = []
    sourceList = []

    with open('sourceCode1') as f:
        for row in f.read().split('\n'):
            row = row.decode('utf-8')
            if row.find('#') >= 0:
                s = row.split('#')
                investorName = s[1]

                for id in s[2:]:
                    investorList.append([investorName, int(id)])
            elif row != '':
                sourceList.append([investorName, row.strip()])

    df1 = pd.DataFrame(investorList, columns=['investorName', 'investorId'])
    df2 = pd.DataFrame(sourceList, columns=['investorName', 'investorAlias'])

    investorIds = df1.investorId.tolist()
    conn = db.connect_torndb()
    result = conn.query(
        '''select ia.investorId,ia.name investorAlias ,i.name investorName
        from investor_alias ia 
        join investor i on ia.investorId=i.id
         where i.id in %s and ia.type=12010 and (ia.active is null or ia.active ='y') ''',
        investorIds)
    conn.close()
    df3 = pd.DataFrame(result)

    dfMerge = pd.merge(df1, df2, how='left', on='investorName')
    dfMerge = pd.merge(dfMerge, df3, how='outer', on='investorAlias', suffixes=('', '_xiniu'))

    dfMerge['investorNameMerge'] = dfMerge.apply(
        lambda x: x.investorName if pd.isnull(x.investorName_xiniu) else x.investorName_xiniu, axis=1)
    dfMerge['investorIdMerge'] = dfMerge.apply(
        lambda x: x.investorId if pd.isnull(x.investorId_xiniu) else x.investorId_xiniu, axis=1)

    # dfMerge['investorAliasMerge']=dfMerge.apply(lambda x:x.investorAlias if pd.isnull(x.investorAlias_xiniu) else x.investorAlias_xiniu,axis=1)


    investorAlias = dfMerge.investorAlias.tolist()
    mongo = db.connect_mongo()
    collection = mongo.amac.manager
    results = list(collection.find({'managerName': {'$in': investorAlias}}, {'managerName': 1}))
    dfManager = pd.DataFrame(results)

    collection = mongo.amac.fund
    results = list(collection.find({'fundName': {'$in': investorAlias}}, {'fundName': 1}))
    dfFund = pd.DataFrame(results)

    dfMerge = pd.merge(dfMerge, dfManager, how='left', left_on='investorAlias', right_on='managerName',
                       suffixes=('', '_amac_m'))
    dfMerge = pd.merge(dfMerge, dfFund, how='left', left_on='investorAlias', right_on='fundName',
                       suffixes=('', '_amac_f'))

    dfMerge = dfMerge.drop(['_id', '_id_amac_f'], axis=1)
    dfMerge['isXiniu'] = dfMerge.apply(lambda x: 'F' if pd.isnull(x.investorName_xiniu) else 'T', axis=1)
    dfMerge['isThird'] = dfMerge.apply(lambda x: 'F' if pd.isnull(x.investorName) else 'T', axis=1)

    def setType(x):
        if x.isXiniu == 'T' and x.isThird == 'T':
            return 'Both'
        elif x.isXiniu == 'F' and x.isThird == 'T':
            return 'Third'
        elif x.isXiniu == 'T' and x.isThird == 'F':
            return 'Xiniu'

    dfMerge['type'] = dfMerge.apply(setType, axis=1)

    def amacType(x):
        if pd.notnull(x.managerName) and pd.notnull(x.fundName):
            return 'D'
        elif pd.notnull(x.managerName) and pd.isnull(x.fundName):
            return 'M'
        elif pd.isnull(x.managerName) and pd.notnull(x.fundName):
            return 'F'

    dfMerge['amacType'] = dfMerge.apply(amacType, axis=1)

    dfMerge.to_excel('export.xlsx', index=0,
                     columns=["investorNameMerge", "investorIdMerge", "investorAlias", "managerName", "fundName",
                              "isXiniu", "isThird", "type", "amacType"])

    # scp root@xiniudata-task-02:/data/task-201606/spider2/aggregator/amac/export.xlsx  /Users/ryu/Documents/git/work/未命名文件夹/funding


def insert():
    investorIds = [109, 142, 211, 9221, 114, 170, 141, 514, 267, 2239, 2037, 263, 6301, 282, 115, 199, 1246, 387, 210,
                   7348,
                   2669, 314, 398, 13391, 151, 391, 302, 134, 300, 280, 679, 167, 719, 2154, 357, 6316, 348, 149, 182,
                   1558, 380, 154, 229, 546, 2911, 132, 1790, 3348, 4546, 2263, 251, 358, 671, 129, 13697, 118, 253,
                   133, 12353, 1987, 125, 2398, 1960, 224, 265, 9602, 152, 201, 1443, 108, 2304, 4995, 4964, 493, 234,
                   2022, 111, 1788, 186, 189, 131, 4587, 7356, 1575, 110, 575, 1908, 326, 4989, 250, 166]

    def insert_each(investorId):
        conn = db.connect_torndb()
        sql = "insert famous_investor (investorId,createUser,createTime,modifyTime) \
                       values(%s,-1,now(),now())"
        job_id = conn.insert(sql, investorId)
        conn.close()

    for id in investorIds:
        insert_each(id)


def insert_alias():
    def insert_each(investorId, investorAlias):
        conn = db.connect_torndb()
        sql = "select * from  investor_alias where investorId=%s and name=%s "
        r = conn.query(sql, investorId, investorAlias)
        if len(r) == 0:
            sql1 = "insert investor_alias(investorId,name,type,createTime,modifyTime,createUser) " \
                   "values(%s,%s,12010,now(),now(),-537)"
            id = conn.insert(sql1, investorId, investorAlias)
            print 'inserting %s' % investorAlias
        else:
            print r
            print 'already exists %s' % (investorAlias)
            id = None
        conn.close()
        return id

    dfThird = dfMerge[dfMerge.type == 'Third']
    insert_each(250, '天津常春藤投资管理中心（有限合伙）')
    for ix, row in dfThird.iterrows():
        print int(row.investorIdMerge), row.investorAlias
        if pd.isnull(row.investorAlias): continue
        id = insert_each(int(row.investorIdMerge), row.investorAlias)


def amacType():
    import amac_util

    investorIds = [109, 142, 211, 9221, 114, 170, 141, 514, 267, 2239, 2037, 263, 6301, 282, 115, 199, 1246, 387, 210,
                   7348,
                   2669, 314, 398, 13391, 151, 391, 302, 134, 300, 280, 679, 167, 719, 2154, 357, 6316, 348, 149, 182,
                   1558, 380, 154, 229, 546, 2911, 132, 1790, 3348, 4546, 2263, 251, 358, 671, 129, 13697, 118, 253,
                   133, 12353, 1987, 125, 2398, 1960, 224, 265, 9602, 152, 201, 1443, 108, 2304, 4995, 4964, 493, 234,
                   2022, 111, 1788, 186, 189, 131, 4587, 7356, 1575, 110, 575, 1908, 326, 4989, 250, 166]
    for i in investorIds:
        print i
        amac_util.check_amacType(i)


if __name__ == "__main__":
    run()
