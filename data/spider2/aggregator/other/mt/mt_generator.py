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
loghelper.init_logger("mt_generator", stream=True)
logger = loghelper.get_logger("mt_generator")

mongo = db.connect_mongo()
collection = mongo['open-maintain'].task
collectionUser = mongo['open-maintain'].user
collection_task_serial = mongo['open-maintain'].task_serial
conn = db.connect_torndb()


def assignTask(companyId, section, assignee, origin, priority, taskSerialId=None, parentTaskId=None, flow='Y', memo=None):
    mongo = db.connect_mongo()
    collection = mongo['open-maintain'].task
    contentMap = {u'funding': u'融资', u'memberAndRecruitment': u'成员/招聘', u'artifact': u'产品',
                  u'industryAndComps': u'行业/竞品', u'tag': u'标签', u'news': u'新闻', u'basic': u'基本信息'}

    if section == 'finish':
        logger.info('company:%s finished,set to active', companyId)
        conn.update('''update company set active='Y' where id=%s''', companyId)
        return

    if collection.find_one(
            {'companyId': companyId, 'section': section, 'active': 'Y', "processStatus": {'$in': [0, -1]}}) is not None:
        logger.info('already exists company:%s |section:%s', companyId, section)
    else:
        logger.info('inserting company:%s |section:%s', companyId, section)
        time = datetime.datetime.utcnow()
        if taskSerialId is None:
            task_serial = collection_task_serial.find_one({'relateId': companyId, 'active': 'Y', 'status':{'$in':[0, 1]}})
            if task_serial is  None:
                task_serial = {
                                  "relateId": companyId ,
                                  "taskType": "company",
                                  "active": "Y",
                                  "flow":flow,
                                  "origin":origin,
                                  "priority": priority,
                                  "status":0,
                                  "createTime": time,
                                  "createUser": 139
                }

                taskSerialId = str(collection_task_serial.insert_one(task_serial))
            else:
                taskSerialId = str(task_serial["_id"])

        taskMap = {"companyId": companyId,
                   "taskType": 'company',
                   "section": section,
                   "content": contentMap[section],
                   "createTime": datetime.datetime.utcnow(),
                   "processStatus": 0,
                   "auditStatus": 0,
                   "taskUser": assignee,
                   "rejectCount": 0,
                   "flow": flow,
                   'active': 'Y',
                   'origin': origin,
                   'parentTaskId': parentTaskId,
                   'flowProcess': 0,
                   'priority': priority,
                   'taskSerialId': taskSerialId,
                   }
        if memo is not None: taskMap['taskMemo'] = memo #可能以后要传
        taskid = str(collection.insert_one(taskMap).inserted_id)


        return taskid


def preAssignTask(skipVerified, companyId, section, assignee, origin, priority, taskSerialId, parentTaskId=None,
                  flow='Y', memo=None):
    logger.info('preassign task cid:%s|section:%s', companyId, section)
    flag = True
    if skipVerified == 'Y':
        verified = section_verified(companyId, section)
        # if verified == False:
        if verified is None or verified != False:#//section 都verify过
            logger.info('skip task here3 cid:%s|section:%s', companyId, section)
            flag = False
            if section == 'basic':
                logger.info('preassign task11 cid:%s|section:%s', companyId, section)
                preAssignTask(skipVerified, companyId, 'funding', assignee, origin, priority, taskSerialId,
                              parentTaskId=None,
                              flow='Y', memo=memo)

    if flag: assignTask(companyId, section, assignee, origin, priority, taskSerialId, parentTaskId=parentTaskId,
                        flow=flow, memo=memo)

    if section != 'basic':
        sectionMap = {'funding': 'artifact', 'memberAndRecruitment': 'tag', 'artifact': 'news',
                      'tag': 'industryAndComps',
                      'basic': 'funding', 'news': 'memberAndRecruitment', 'industryAndComps': 'finish'}
        while section != 'finish':
            nextsection = sectionMap.get(section)
            section = nextsection
            if skipVerified == 'Y':
                verified = section_verified(companyId, section)
                if verified is None or verified != False: continue
            if section == 'finish': break
            logger.info('assign task here1 cid:%s|section:%s', companyId, section)

            newtaskid = assignTask(companyId, section, assignee, origin, priority, taskSerialId,
                                   parentTaskId=parentTaskId,
                                   flow=flow,
                                   memo=memo)
            parentTaskId = newtaskid if newtaskid is not None else parentTaskId


def section_verified(companyId, section=''):
    # 判断 section 有没有 verify 过，没有返回False
    # 基本信息，融资，产品，新闻，成员 / 招聘，标签，行业 / 竞品
    '''公司各步骤的验证逻辑： verify='Y' & active='Y'
基本信息： company
融资： funding 每一条
产品： artifact 每一条
新闻： 暂时没有
成员： company_member_rel 每一条
招聘： company_recruitment_rel 每一条
标签： company_tag_rel 每一条v
行业/竞品： 暂时没有'''
    sectionMap = {'funding': 'artifact', 'memberAndRecruitment': 'tag', 'artifact': 'news',
                  'tag': 'industryAndComps',
                  'basic': 'funding', 'news': 'memberAndRecruitment', 'industryAndComps': 'finish'}

    if section == 'basic':
        comp = conn.query("select * from company where "
                          " verify is null and id=%s", companyId)
        if len(comp) > 0: return False
    elif section == 'funding':
        fundings = conn.query("select * from funding f left join company c on f.companyId=c.id "
                              "where f.companyId=%s  and "
                              "(f.active is null or f.active='Y') and f.verify is null", companyId)
        if len(fundings) > 0: return False
    elif section == 'artifact':
        artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                               "and verify is null", companyId)
        if len(artifacts) > 0: return False
    elif section == 'news':
        if mongo.article.news.find_one(
                {'type': {'$ne': 61000}, 'companyIds': companyId}) is not None:
            return False
    elif section == 'memberAndRecruitment':
        members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                             "where cmr.companyId=%s and m.verify is null and "
                             "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                             "(cmr.active is null or cmr.active='Y')", companyId)
        comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                             "(active is null or active='Y') and verify is null", companyId)
        if len(members) > 0 or len(comrecs) > 0: return False
    elif section == 'tag':
        tags = conn.query('''select * from company_tag_rel r join company c on r.companyId=c.id 
                          join tag t on t.id=r.tagid
                          where r.companyId=%s   and 
                          (r.active is null or r.active='Y') and (t.active is null or t.active='Y') and (r.verify is null or r.verify!='Y')''',
                          companyId)
        if len(tags) > 0: return False
        # 这家公司没有 tag
        tags = conn.query('''select * from company_tag_rel r join company c on r.companyId=c.id 
                          join tag t on t.id=r.tagid
                          where r.companyId=%s   and 
                          (r.active is null or r.active='Y') and (t.active is null or t.active='Y')''',
                          companyId)
        if len(tags) == 0: return False
    elif section == 'industryAndComps':
        return False
    elif section == 'finish':
        return False


def find_tobeverify_section(companyId, section=''):
    # section：当前完成的 section
    # 基本信息，融资，产品，新闻，成员 / 招聘，标签，行业 / 竞品
    '''公司各步骤的验证逻辑： verify='Y' & active='Y'
基本信息： company
融资： funding 每一条
产品： artifact 每一条
新闻： 暂时没有
成员： company_member_rel 每一条
招聘： company_recruitment_rel 每一条
标签： company_tag_rel 每一条v
行业/竞品： 暂时没有'''

    comp = conn.query("select * from company where "
                      " verify is null and id=%s", companyId)
    if len(comp) > 0: return 'basic'

    fundings = conn.query("select * from funding f left join company c on f.companyId=c.id "
                          "where f.companyId=%s  and "
                          "(f.active is null or f.active='Y') and f.verify is null", companyId)
    if len(fundings) > 0: return 'funding'

    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                           "and verify is null", companyId)
    if len(artifacts) > 0: return 'artifact'

    if section in ['', 'basic', 'funding', 'artifact']:
        if mongo.article.news.find_one(
                {'type': {'$ne': 61000}, 'companyIds': companyId}) is not None:
            return 'news'

    members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                         "where cmr.companyId=%s and m.verify is null and "
                         "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                         "(cmr.active is null or cmr.active='Y')", companyId)
    comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                         "(active is null or active='Y') and verify is null", companyId)
    if len(members) > 0 or len(comrecs) > 0: return 'memberAndRecruitment'

    tags = conn.query('''select * from company_tag_rel r join company c on r.companyId=c.id 
                      join tag t on t.id=r.tagid
                      where r.companyId=%s   and 
                      (r.active is null or r.active='Y') and (t.active is null or t.active='Y') and r.verify is null''',
                      companyId)
    if len(tags) > 0: return 'tag'

    # 基本信息，融资，产品，新闻，成员 / 招聘，标签，行业 / 竞品
    sectionMap = {'funding': 'artifact', 'memberAndRecruitment': 'tag', 'artifact': 'news', 'tag': ' industryAndComps',
                  'basic': 'funding', 'news': 'memberAndRecruitment'}

    if section == 'industryAndComps':
        return 'finish'
    else:
        return 'industryAndComps'


def start_run():
    # 提取task.company中mtProcessStatus不存在的记录
    mongo = db.connect_mongo()
    collectionDefine = mongo['open-maintain'].task_origin_def
    while True:
        # items = list(mongo.task.company.find(
        #     {"processStatus": 0,
        #      'types': {'$in': ['news_regular']},
        #      'mtProcessStatus': {"$ne": 1}}).limit(1000))
        items = list(mongo.task.company.find(
            {'createTime': {'$gt': datetime.datetime(2018, 2, 2)}, "processStatus": 0,
             'mtProcessStatus': {"$ne": 1}}).limit(1000))
        # len(items)
        cnt = 0
        for i in items:
            company = conn.query(
                '''select id,code,active from company where id= %s and (active is null or active !='N')''',
                i['companyId'])
            if len(company) == 0:
                logger.info('company :%s delete', i['companyId'])
                continue
            cnt += 1

            logger.info('start process task company cid:%s|companttaskid:%s', i['companyId'], i['_id'])

            # 获取 priority 最大的来源
            maxPriority = 999
            # skipVerified = 'Y'
            for type in i['types']:
                origindefine = collectionDefine.find_one({'origin': type})
                priority = origindefine['priority']
                if priority < maxPriority:
                    maxPriority = priority
                    skipVerified = origindefine['skipVerified']
                    maxorigin = type

            # 多类型的情况,最后是要去掉,测试用
            if maxPriority <= 2:
                logger.info('high priority continue') # why?
                continue

            oldtask = mongo['open-maintain'].task.find_one(
                {'companyId': i['companyId'], 'processStatus': 0, 'active': 'Y'})

            # task_serial  oldNone  task_serial 直接生成,否则 用任务的
            if oldtask is None:
                # if skipVerified == 'N':
                #     logger.info('assign task cid:%s|section:%s', i['companyId'], 'basic')
                #     section='basic'
                # else:
                #     # 按顺序找到第一个需verify的模块，生成相应任务
                #     section = find_tobeverify_section(i['companyId'])
                #     logger.info('assign task cid:%s|section:%s', i['companyId'], section)
                #     assignTask(i['companyId'], section, -666, origin=maxorigin, taskSerialNo,priority=maxPriority, memo='')
                section = 'basic'
                logger.info('assign task cid:%s|section:%s', i['companyId'], 'basic')

                preAssignTask(skipVerified, i['companyId'], section, -666, origin=maxorigin, priority=maxPriority,
                              taskSerialNo='-1')
            else:  # 调整mt任务来源为优先级最大的
                oldpriority = collectionDefine.find_one({'origin': oldtask['origin']})
                if maxPriority < oldpriority:
                    logger.info('update task cid:%s|origin:%s', i['companyId'], maxorigin)
                    mongo['open-maintain'].task.update_many(
                        {'companyId': i['companyId'], 'processStatus': 0, 'active': 'Y'},
                        {'$set': {'origin': maxorigin, 'priority': maxPriority}})

            logger.info('processed task company cid:%s|taskid:%s', i['companyId'], i['_id'])
            mongo.task.company.update_one({'_id': i['_id']}, {'$set': {'mtProcessStatus': 1}})

        # if len(items) == 0:time.sleep(1)
        time.sleep(60)


def test_dev():
    cids = conn.query(
        'select distinct companyId from topic_company  where topicid=26 and (active is null or active="Y") limit 50')

    alltypes = mongo['open-maintain'].task_origin_def.distinct('origin')
    alltypes = ['company_create']

    index = 0
    # todo 测试多 types
    for c in cids:
        mongo.task.company.insert({
            'companyId': c['companyId'],
            "types": [alltypes[index]],
            'mark': 'mt_test',
            'createTime': datetime.datetime.utcnow(),
            'processStatus': 0,
        })
        index += 1
        if index >= len(alltypes): index = 0

    # mongo.task.company.insert({
    #     'companyId': 20202,
    #     "types": ['news_funding', 'company_fa', 'visit_openapi'],
    #     'mark': 'mt_test',
    #     'createTime': datetime.datetime.utcnow(),
    # })


if __name__ == "__main__":
    while True:
        try:
            start_run()
        except Exception, e:
            logger.exception(e)
            # traceback.print_exc()
            time.sleep(1)
            start_run()
