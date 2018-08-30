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

# logger
loghelper.init_logger("mt_assign", stream=True)
logger = loghelper.get_logger("mt_assign")

mongo = db.connect_mongo()
collection = mongo['open-maintain'].task
collectionUser = mongo['open-maintain'].user
conn = db.connect_torndb()


def start_run():
    mongo = db.connect_mongo()
    while True:
        items = list(
            mongo['open-maintain'].task.find({'taskUser': -666}).sort("priority", pymongo.ASCENDING).limit(1000))
        for item in items:
            # item=mongo['open-maintain'].task.find_one({'_id': ObjectId("5a704a70346dbf3ed9318c9e")})
            # item = {'section': 'funding', 'companyId': 258602}
            # 找出在岗的，该模块的，相应业务线的，未处理任务不满的用户
            if item['section'] in ['tag', 'industryAndComps']:
                tags = conn.query('''select distinct t.id from company_tag_rel r join company c on r.companyId=c.id 
                                              join tag t on t.id=r.tagid
                                              where r.companyId=%s   and t.sectortype=1  and
                                              (r.active is null or r.active='Y') and (t.active is null or t.active='Y')''',
                                  item['companyId'])
                tagids = [i['id'] for i in tags]
                # 相应业务线
                candidates = list(
                    mongo['open-maintain'].user.find(
                        {'online': 'Y', 'active': 'Y', 'sectors': {'$in': tagids}, 'orgId': 1}))
            else:
                candidates = list(mongo['open-maintain'].user.find({'online': 'Y', 'active': 'Y', 'orgId': 1}))
            cansection = [i['userId'] for i in
                          list(mongo['open-maintain'].user_task_type.find({'section': item['section']}))]
            candidates = [i['userId'] for i in candidates if i['userId'] in cansection]

            # 分给当前任务量最少的人
            taskCnt = list(mongo['open-maintain'].task.aggregate(
                [{'$match': {'section': item['section'], 'processStatus': 0, 'active': "Y",
                             'taskUser': {'$in': candidates}}},
                 {'$group': {'_id': '$taskUser', 'cnt': {'$sum': 1}}},
                 {'$sort': {'cnt': 1}}]))

            # 优先分给同一个人
            parenttask = mongo['open-maintain'].task.find_one({'_id': ObjectId(item['parentTaskId'])})
            if parenttask is not None:
                lastuser = parenttask.get('taskUser', -999)
                if lastuser in candidates:
                    taskCnt2 = []
                    for tcnt in taskCnt:
                        if tcnt['_id'] == lastuser:
                            taskCnt2.append(tcnt)
                            break
                    for tcnt in taskCnt:
                        if tcnt['_id'] != lastuser:
                            taskCnt2.append(tcnt)
                    taskCnt = taskCnt2

            assignee = None
            # print '22', len(taskCnt), len(candidates)
            if len(taskCnt) < len(candidates):
                taskUser = [i['_id'] for i in taskCnt]
                for uid in candidates:
                    if uid not in taskUser:
                        assignee = uid
                        break
            else:
                for candidate in taskCnt:
                    if candidate['cnt'] == 50:
                        lowertask = list(mongo['open-maintain'].task.find(
                            {'taskUser': candidate['_id'], 'flow': 'Y', 'priority': {'$gt': item['priority']}}).sort(
                            "priority",pymongo.DESCENDING))
                        if len(lowertask) == 0:
                            logger.info('cant deassignne for user:%s', candidate['_id'])
                            # next candidate
                            continue
                        else:
                            logger.info('deassign task:%s of user:%s', lowertask[0]['_id'], candidate['_id'])
                            mongo['open-maintain'].task.update_one({'_id': lowertask[0]['_id']},
                                                                   {'$set': {'taskUser': -666}})
                            assignee = candidate['_id']
                            break
                    elif candidate['cnt'] > 50:
                        logger.info('more than 50, cant deassignne for user:%s', candidate['_id'])
                        break
                    else:
                        assignee = candidate['_id']
                        break

            if assignee is not None:
                logger.info('assign task:%s to userId:%s', item['_id'], assignee)
                mongo['open-maintain'].task.update_one({'_id': item['_id']}, {'$set': {'taskUser': assignee}})
            else:
                logger.info('cannot find anyone to take task:%s', item['_id'])
                # exit()

        time.sleep(5)


# db.task.aggregate([{$match:{active:'Y',processStatus:0}},{$group:{_id: {'id':'$taskUser','section':'$section'}, cnt: {$sum:1}}},{$sort:{cnt:-1}}])
# db.task.aggregate([{$match:{active:'Y',processStatus:0,taskUser:{$ne:-666}}},{$group:{_id: {'id':'$taskUser','section':'$section'}, cnt: {$sum:1}}},{$sort:{cnt:-1}}])

if __name__ == "__main__":
    while True:
        try:
            start_run()
        except Exception, e:
            logger.exception(e)
            # traceback.print_exc()
            time.sleep(1)
            start_run()
