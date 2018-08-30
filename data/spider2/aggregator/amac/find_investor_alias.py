# -*- coding: utf-8 -*-
import os, sys, re, json, time
import datetime
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import amac_util

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper
import db, traceback
from bson import ObjectId
from math import log

# logger
loghelper.init_logger("find_investor_alias", stream=True)
logger = loghelper.get_logger("find_investor_alias")


def add_alias_candidate(investorId, name, comment):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()

    alias = conn.get("select * from investor_alias_candidate where type=12010 and name=%s and investorId=%s "
                     "limit 1", name, investorId)

    if alias is None:
        sql1 = "insert investor_alias_candidate(investorId,name,type,comment,createTime) " \
               "values(%s,%s,%s,%s,now())"
        iacId = conn.insert(sql1, investorId, name, 12010, comment)

        if conn.get('select * from famous_investor where investorId=%s limit 1', investorId) is not None:
            mongo.task.investor.insert_one({
                "processStatus": 0,
                "investorId": int(investorId),
                "taskDate": datetime.datetime.now().strftime("%Y%m%d"),
                "createTime": datetime.datetime.now(),
                "modifyTime": datetime.datetime.now(),
                "type": 'name_candidate',
                "relateId": iacId,
                "comments": comment
            })

    mongo.close()
    conn.close()


def method1(investorId, investorName):
    sql = '''
    select iaa.amacId
    from investor_alias  ia
    join investor_alias_amac iaa on iaa.investorAliasId=ia.id
    where (ia.active = 'Y' or ia.active is null) and (ia.verify != 'N' or ia.verify is null)
    and (iaa.active = 'Y' or iaa.active is null)
    and iaa.amacType='M'
    and  ia.investorID=%s
    '''
    conn = db.connect_torndb_proxy()
    result = conn.query(sql, investorId)
    conn.close()

    mongo = db.connect_mongo()
    collection_amac = mongo.amac.manager
    collection_gongshang = mongo.info.gongshang

    amacIds = [ObjectId(i['amacId']) for i in result]
    managers = list(collection_amac.find({'_id': {'$in': amacIds}}, {'managerName': 1}))
    managerNames = [i['managerName'] for i in managers]
    gongshangs = list(collection_gongshang.find({'name': {'$in': managerNames}}))
    mongo.close()
    for g in gongshangs:
        if g.has_key('invests'):
            for invest in g['invests']:
                try:
                    investName = invest['name'].replace("(", "（").replace(")", "）")
                except:
                    continue

                conn = db.connect_torndb_proxy()
                q = conn.query(
                    '''select * from investor_alias ia join investor i on i.id=ia.investorid 
                     where (ia.active = 'Y' or ia.active is null)
                     and (i.active = 'Y' or i.active is null) and ia.name=%s''',
                    investName)
                conn.close()
                if len(q) == 0:
                    logger.info('insert %s into investorid:%s |method:-661 |managerName:%s', investName, investorId,
                                g['name'])
                    comment = u'%s的管理公司：%s，对外投资有该公司' % (investorName, g['name'])
                    add_alias_candidate(investorId, investName, comment)


def method2(investorId, investorName, Allgongshangs, lengthAll):
    portfolios = get_investor_porfolio(investorId)
    corIds = [i['corporateId'] for i in portfolios]
    if len(corIds) == 0: return

    # fundedCompany = get_all_funded_company()
    # AllcorIds = [i['corporateId'] for i in fundedCompany]

    fullNames = get_companyFullNames(corIds)
    # AllfullNames = get_companyFullNames(AllcorIds)

    gongshangs, AllInvestors = get_investors_by_name(fullNames)
    # Allgongshangs, AllInvestors2 = get_investors_by_name(AllfullNames)

    for i in AllInvestors:
        # 自然人
        if len(i) < 5: continue
        if i.find(u'投资') < 0 and i.find(u'基金') < 0: continue

        tf = 0
        idfDenominator = 0

        #  每个和真格有关的公司
        commentList = []
        for company in gongshangs:
            if i in company['invstorNames']:
                tf += 1
                commentList.append(company['name'])

        for company2 in Allgongshangs:
            if i in company2['invstorNames']:
                idfDenominator += 1

        if idfDenominator == 0: logger.info('zero check:i:%s|investor:', i, investorId)
        try:
            idf = log(lengthAll / idfDenominator)
        except:
            traceback.print_exc()
            continue
        tf_idf = tf * idf

        if tf_idf >= 20:
            conn = db.connect_torndb_proxy()
            q = conn.query(
                '''select * from investor_alias ia join investor i on i.id=ia.investorid 
                 where (ia.active = 'Y' or ia.active is null)
                 and (i.active = 'Y' or i.active is null) and ia.name=%s''',
                i)
            conn.close()
            if len(q) == 0:
                logger.info('insert %s into investorid:%s |method:-662 |tf:%s idf:%s tf_idf:%s', i, investorId, tf,
                            round(idf, 1), round(tf_idf, 1))
                comment = u'投过%s的 portfolio：%s |tf:%s idf:%s tf_idf:%s' % (investorName, '，'.join(commentList[:5]), tf,
                                                                           round(idf, 1), round(tf_idf, 1))
                add_alias_candidate(investorId, i, comment)


def get_investor_porfolio(investorId):
    conn = db.connect_torndb_proxy()
    sql = '''
    select distinct c.id,c.name,c.code,c.corporateId
    from funding_investor_rel fi 
    join funding f on f.id=fi.fundingId
    join company c on f.corporateId=c.corporateId
    where (f.active = 'Y' or f.active is null)
    and (fi.active = 'Y' or fi.active is null)
    and (c.active = 'Y' or c.active is null)
    and fi.investorId=%s
    '''
    result = conn.query(sql, investorId)
    conn.close()
    return result


def get_all_funded_company():
    conn = db.connect_torndb_proxy()
    sql = '''
    select distinct c.id,c.name,c.code,c.corporateId
    from funding f 
    join company c on f.corporateId=c.corporateId
    where (f.active = 'Y' or f.active is null)
    and (c.active = 'Y' or c.active is null)
    '''
    result = conn.query(sql)
    conn.close()
    return result


def get_companyFullNames(corIds):
    conn = db.connect_torndb_proxy()
    index = 0
    finalFullNames = []
    while True:
        if index >= len(corIds): break
        corId = corIds[index:index + 1000]
        index += 1000
        sql = '''
        select name
        from corporate_alias
        where (active = 'Y' or active is null)
        and corporateId in %s
        '''
        result = conn.query(sql, corId)
        fullNames = [i['name'] for i in result]
        finalFullNames += fullNames

    conn.close()
    return list(set(finalFullNames))


def get_investors_by_name(names):
    mongo = db.connect_mongo()
    collection = mongo.info.gongshang
    gongshangs = list(collection.find({'name': {'$in': names}}, {'investors': 1, 'name': 1}))
    AllInvestors = {}
    for g in gongshangs:
        investorNames = []
        if g.has_key('investors'):
            for i in g['investors']:
                if i['name'] is None:
                    logger.info('investorName is None %s', g['name'])
                    continue
                try:
                    AllInvestors[i['name']] = i['type']
                except:
                    AllInvestors[i['name']] = 'unknown'
                    # logger.info('%s cant get type ',g['name'])
                investorNames.append(i['name'])
            g['invstorNames'] = investorNames
        else:
            g['invstorNames'] = []
    mongo.close()
    return gongshangs, AllInvestors


if __name__ == '__main__':
    if len(sys.argv) > 1:
        investorId = sys.argv[1]
        conn = db.connect_torndb_proxy()
        investorName = conn.get('select * from investor where id=%s', investorId)['name']
        conn.close()

        method1(investorId, investorName)
        method2(investorId, investorName)
