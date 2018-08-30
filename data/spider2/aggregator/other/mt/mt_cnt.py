# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, name_helper, url_helper
import json, config, traceback, time, util
from bson.objectid import ObjectId
import random

# logger
loghelper.init_logger("mt_cnt", stream=True)
logger = loghelper.get_logger("mt_cnt")

mongo = db.connect_mongo()
collection = mongo['open-maintain'].task
collectionUser = mongo['open-maintain'].user
conn = db.connect_torndb()


def start_run():
    while True:
        taskCnt = list(mongo['open-maintain'].task.aggregate(
            [{'$match': {'taskUser': -666, 'active': "Y"}},
             {'$group': {'_id': '$origin', 'cnt': {'$sum': 1}}},
             {'$sort': {'cnt': 1}}]))

        for i in taskCnt:
            origin = i['_id']
            taskCnt2 = list(mongo['open-maintain'].task.find({'taskUser': -666, 'active': "Y", 'origin': origin}))
            cids = [t['companyId'] for t in taskCnt2]
            cids = set(cids)

            cntMap = {'origin': origin,
                      'unassigned_task': i['cnt'],
                      'unassigned_company': len(cids),
                      "createTime": datetime.datetime.utcnow(),
                      }
            # print cntMap

            mongo['open-maintain'].taskcnt.insert(cntMap)
            logger.info('saving origin:%s|cnt:%s', origin,i['_id'])

        time.sleep(10*60)

def stat():
    import datetime
    import pandas as pd
    collection = mongo['open-maintain'].task
    collectionuser = mongo['open-maintain'].user
    today = datetime.datetime.now()
    today = datetime.datetime(today.year, today.month, today.day)

    result = list(collection.find({'createTime': {'$gt': today},'taskUser':{'$ne':-666}}))
    df = pd.DataFrame(result)
    # df.drop(['_id'],axis=1).to_excel('export.xlsx', index=0)
    dfuser = pd.DataFrame(list(collectionuser.find({}, {'username': 1, 'userId': 1})))
    df = pd.merge(df, dfuser, left_on='taskUser', right_on='userId', how='left')

    # df2 = df.pivot_table(index=['companyId'], columns=['section'], values=['processStatus'], aggfunc=max, fill_value='')
    df2 = df.pivot_table(index=['companyId','origin'], columns=['section'], values=['processStatus', 'username'], aggfunc=max,fill_value='')
    # df2=df.pivot_table(index=['companyId','section'], values=['processStatus','taskUser'], aggfunc=max,fill_value='')

    def getmerge(x):
        if min(x['processStatus']) == 1:
            return u'全部完成'
        elif min(x['processStatus']) in [0,-1]:
            return u'已分配未完成'
        else:
            return u'未分配'

    # df2['merge'] = df2.apply(lambda x: u'全部完成' if min(x['processStatus']) == 1 else u'未完成', axis=1)
    df2['merge'] = df2.apply(getmerge, axis=1)
    df2['merge2'] = df2.apply(lambda x:min(x['processStatus']), axis=1)
    # df2.to_excel('export.xlsx', index=1)
    # df2.head(1).to_json(orient='table')

    li=[]
    processMap={0:'未处理',1:'已处理',-1:'处理不了'}
    for ix, row in df2.iterrows():
        # print ix, row
        # print row['merge']['section']
        cntMap = {
            'companyId': ix[0],
            'origin': ix[1],
            'status': row['merge'][0],
        }
        # for section in collection.distinct('section'):
        for section in ['basic','funding','artifact','news','memberAndRecruitment','tag','industryAndComps']:
            # cntMap[section]={'processStatus':row['processStatus'][section],
            #                  'username':row['username'][section]
            #                  }
            if row['processStatus'][section] =='':continue
            processresult=processMap.get(row['processStatus'][section])
            if row['username'][section] !='':cntMap[section] = '%s/%s'%(row['username'][section],processresult)
        # mongo['open-maintain'].taskstat.insert(cntMap)
        li.append(cntMap)
    df3=pd.DataFrame(li)
    # df3=df3.drop(['_id'],axis=1)
    df3.to_excel('export.xlsx', index=0,columns=[u'companyId', u'origin', u'basic', u'funding', u'artifact', u'news', u'memberAndRecruitment', u'tag', u'industryAndComps', u'status'])


if __name__ == "__main__":
    while True:
        try:
            start_run()
        except Exception, e:
            logger.exception(e)
            # traceback.print_exc()
            time.sleep(1)
            start_run()
