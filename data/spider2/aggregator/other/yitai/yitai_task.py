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
from kafka import (KafkaClient, KafkaConsumer, SimpleProducer)
from bson.objectid import ObjectId

# kafka
kafkaProducer = None

# logger
loghelper.init_logger("yitai_task", stream=True)
logger = loghelper.get_logger("yitai_task")

mongo = db.connect_mongo()
collection = mongo['open-maintain'].task
collectionUser = mongo['open-maintain'].user
conn = db.connect_torndb()

# kafka
kafkaConsumer = None
kafkaProducer = None


def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("open_maintain", group_id="maintain",
                                  bootstrap_servers=[url],
                                  auto_offset_reset='smallest')


def assignTask(companyId, section, assignee, flow='Y',memo=''):
    mongo = db.connect_mongo()
    collection = mongo['open-maintain'].task
    contentMap = {u'funding': u'融资', u'memberAndRecruitment': u'成员/招聘', u'artifact': u'产品',
                  u'industryAndComps': u'行业/竞品', u'tag': u'标签', u'news': u'新闻', u'basic': u'基本信息'}

    if collection.find_one({'companyId': companyId, 'section': section}) is not None:
        logger.info('already exists company:%s |section:%s', companyId, section)
    else:
        logger.info('inserting company:%s |section:%s', companyId, section)

        collection.insert_one({"companyId": companyId,
                               "section": section,
                               "content": contentMap[section],
                               "createTime": datetime.datetime.now(),
                               "processStatus": 0,
                               "auditStatus": 0,
                               "taskUser": assignee,
                               "rejectCount": 0,
                               "flow": flow,
                               "memo": memo
                               }
                              )
    mongo.close()


def assign_company(companyId, section):
    mongo = db.connect_mongo()
    collection = mongo['open-maintain'].task
    collectionUserTask = mongo['open-maintain'].user_task_type
    collectionUser = mongo['open-maintain'].user
    uids = [c['userId'] for c in list(collectionUserTask.find({'section': section}))]
    uids = [c['userId'] for c in list(collectionUser.find({"orgId" : 2})) if c['userId'] in uids]
    # 分给当前任务量最少的人
    taskCnt = list(collection.aggregate(
        [{'$match': {'createTime': {'$gt': datetime.datetime(2018, 1, 16)}, 'section': section,
                     'taskUser': {'$in': uids}}},
         {'$group': {'_id': '$taskUser', 'cnt': {'$sum': 1}}},
         {'$sort': {'cnt': 1}}]))

    # 如果第一批没有分完（不是每个人都分到任务）
    if len(taskCnt) < len(uids):
        taskUser = [i['_id'] for i in taskCnt]
        for uid in uids:
            if uid not in taskUser:
                assignee = uid
                break
    # 根据权重，计算 cnt2=cnt/weight
    else:
        # 如果没有 weight，默认为1
        # weightMap = {c['userId']: c.get('weight', 1) for c in list(collectionUserTask.find({'section': section}))}
        # assignee, minCnt2 = None, float(99999999)
        # for cnt in taskCnt:
        #     userId = cnt['_id']
        #     cnt2 = float(cnt['cnt']) / weightMap[userId]
        #     if cnt2 < minCnt2:
        #         assignee = userId
        #         minCnt2 = cnt2
        assignee = taskCnt[0]['_id']

    assignTask(companyId, section, assignee,memo='2017融资任务')
    mongo.close()

    # db.task.aggregate([{$match:{'createTime':{'$gt':ISODate("2018-01-01T19:59:53.416Z")},section:'basic'}},{$group:{_id: '$taskUser', cnt: {$sum:1}}}])
    # db.task.find({"createTime": {'$gt': ISODate("2017-12-18T9:43:08.518Z")}, section: 'basic'}).count()
    # db.task.remove({"createTime": {'$gt': ISODate("2018-01-01T9:43:08.518Z")}, section: 'basic'})

    # db.task.aggregate([{$group:{_id: {section: '$section', processStatus: '$processStatus'}, cnt: {$sum:1}}}, {$sort:{_id: 1}}])


def exchange_task(coid):
    # 改成没处理过的
    xiniuTask = list(mongo.task.homework_company.find({"assignee": {'$ne': -544}, 'processStatus': 0}))[:1000]

    for xt in xiniuTask:
        conn = db.connect_torndb()
        results = conn.query('select * from company where corporateid=%s and (active!="N" or active is null)',
                             xt['corporateIds'][0])
        # print len(results)
        conn.close()
        if len(results) == 1:
            logger.info('exchange from xiniu:%s to yitai:%s', xt['corporateIds'][0], coid)
            mongo.task.homework_company.update_one({'_id': xt['_id']}, {'$set': {'corporateIds': [coid]}})
            return results[0]['id']


def assign_basic():
    for task in list(mongo.task.homework_company.find(
            {'createTime': {'$gt': datetime.datetime(2018, 1, 15)}, "assignee": -544})):
        coid = task['corporateIds'][0]
        conn = db.connect_torndb()
        results = conn.query('select * from company where corporateid=%s and (active!="N" or active is null)', coid)
        conn.close()
        # 如果有多产品线，替换已有的烯牛任务
        if len(results) > 1:
            logger.info('corporate:%s has more than one cid, exchange', coid)
            cid = exchange_task(coid)
        elif len(results) == 1:
            cid = results[0]['id']
        if cid is None:
            print 'cid of coid:%s is None ' % coid
            break
        assign_company(cid, 'basic')

    def assign_test():
        conn = db.connect_torndb()
        cids = conn.query(
            'select distinct companyId from topic_company  where topicid=52 and (active is null or active="Y")')
        for c in cids:
            assign_company(c['companyId'], 'basic')


# from dev to formal
def trans_data():
    # task02
    li = []
    # for t in list(mongo.task.homework_company.find({"assignee": {'$ne': -544}, 'processStatus': 0}))[:100]:
    for t in list(mongo.task.homework_company.find({"assignee": -544, 'processStatus': 0}))[:100]:
        li.append(t['corporateIds'][0])

    # dev
    li = [65565L, 76L, 98594L, 131456L, 456L, 33236L, 229845L, 131583L, 251307L, 131673L, 295646L, 295657L, 295661L,
          775L,
          856L, 131938L, 99208L, 300558L, 33978L, 1433L, 251484L, 34400L, 263889L, 231152L, 165751L, 295232L, 231308L,
          246101L, 2086L, 2152L, 2180L, 2217L, 198896L, 2428L, 35314L, 2548L, 199306L, 2785L, 246233L, 133929L, 166832L,
          199623L, 265186L, 3073L, 68613L, 134152L, 273590L, 200104L, 200166L, 36367L, 265907L, 102122L, 200496L,
          266139L,
          266143L, 69649L, 200758L, 4226L, 109963L, 4518L, 4580L, 70160L, 201359L, 103184L, 299793L, 299859L, 70535L,
          5108L,
          201721L, 201814L, 5394L, 71022L, 103799L, 267790L, 267870L, 169634L, 202469L, 71567L, 6476L, 72260L, 304032L,
          6887L, 138102L, 203878L, 72858L, 7450L, 72994L, 138541L, 8024L, 40831L, 270288L, 270335L, 270347L, 8326L,
          106730L,
          107294L, 258183L, 116192L, 205706L, 304030L]
    # -544
    li = [131078L, 65578L, 131123L, 98363L, 262208L, 98375L, 74L, 90L, 49167L, 99L, 196708L, 107L, 262255L, 98431L,
          133L,
          196744L, 229514L, 196751L, 262288L, 131219L, 131226L, 131228L, 180L, 196805L, 196809L, 196810L, 98514L,
          32989L,
          196835L, 131302L, 229609L, 196843L, 196847L, 98554L, 169343L, 33021L, 255L, 196867L, 229640L, 262412L, 33037L,
          65806L, 262419L, 262420L, 33050L, 229660L, 262429L, 262433L, 303L, 33075L, 196916L, 196917L, 310L, 313L,
          33083L,
          196928L, 196934L, 196949L, 229725L, 353L, 196962L, 65894L, 33133L, 65910L, 33144L, 33148L, 196996L, 393L,
          65935L,
          229779L, 65946L, 164254L, 164255L, 33184L, 131489L, 295331L, 164261L, 295334L, 277161L, 197038L, 197040L,
          197041L,
          197042L, 197043L, 131509L, 295356L, 65981L, 131519L, 449L, 452L, 295366L, 197067L, 197068L, 197069L, 197070L,
          197071L, 229842L, 229851L, 262623L, 197089L]
    for coid in li:
        mongo.task.homework_company.insert_one({"assignee": -544,
                                                'corporateIds': [coid],
                                                "processStatus": 0,
                                                "taskType": 1,
                                                "createTime": datetime.datetime.now(),
                                                })


def set_weight():
    raw = '''jinjiaxin@ethercap.com	335
chenshuang@ethercap.com	290
manzhihuan@ethercap.com	290
wangyuexin@ethercap.com	290
zhanglichen@ethercap.com	145
zhaoxiaocheng@ethercap.com	290
dongminghao@ethercap.com	145
sushenqi@ethercap.com	290
haorui@ethercap.com	290
xiajinhong@ethercap.com	290'''
    mongo = db.connect_mongo()
    collectionUser = mongo['open-maintain'].user
    collectionUserTask = mongo['open-maintain'].user_task_type
    for row in raw.split('\n'):
        item = row.split('\t')
        email, weight = item[0].strip(), int(item[1].strip())
        print email, weight
        userId = collectionUser.find_one({'email': email})['userId']
        if collectionUserTask.find_one({'userId': userId})['section'] != 'funding':
            print '%s not funding' % email
            break
        collectionUserTask.update_one({'userId': userId}, {'$set': {'weight': weight}})


def resign_funding_task():
    # 已分配的 funding 任务重新按比例分配
    mongo = db.connect_mongo()
    collectionUser = mongo['open-maintain'].user
    collection = mongo['open-maintain'].task
    unfinishedTask = list(collection.find({'section': 'funding', 'processStatus': 0}))
    cids = [i['companyId'] for i in unfinishedTask]

    def resign_company(companyId, section):
        mongo = db.connect_mongo()
        collection = mongo['open-maintain'].task
        collectionUserTask = mongo['open-maintain'].user_task_type
        uids = [c['userId'] for c in list(collectionUserTask.find({'section': section}))]
        # 分给当前任务量最少的人
        taskCnt = list(collection.aggregate(
            [{'$match': {'section': section, 'processStatus': 0, 'taskUser': {'$in': uids}}},
             {'$group': {'_id': '$taskUser', 'cnt': {'$sum': 1}}},
             {'$sort': {'cnt': 1}}]))

        # 如果第一批没有分完（不是每个人都分到任务）
        if len(taskCnt) < len(uids):
            taskUser = [i['_id'] for i in taskCnt]
            for uid in uids:
                if uid not in taskUser:
                    assignee = uid
                    break
        # 根据权重，计算 cnt2=cnt/weight
        else:
            # 如果没有 weight，默认为1
            weightMap = {c['userId']: c.get('weight', 1) for c in list(collectionUserTask.find({'section': section}))}
            assignee, minCnt2 = None, float(99999999)
            for cnt in taskCnt:
                userId = cnt['_id']
                cnt2 = float(cnt['cnt']) / weightMap[userId]
                if cnt2 < minCnt2:
                    assignee = userId
                    minCnt2 = cnt2
                    # assignee = taskCnt[0]['_id']

        assignTask(companyId, section, assignee)
        mongo.close()

    for cid in cids:
        resign_company(cid, 'funding')


def bug_fix():
    mongo = db.connect_mongo()
    collection = mongo.task.homework_company
    repeat = list(
        collection.aggregate([{'$group': {'_id': {'corporateIds': '$corporateIds'}, 'cnt': {'$sum': 1}}}, {'$sort': {
            '_id': 1}}, {'$match': {'cnt': {'$gt': 1}}}]))  # 有重复的任务

    cnt = 0
    fullCorids = [i for i in tasksMap]
    nowTask = [i['corporateIds'][0] for i in list(collection.find({}))]
    lostCorids = [i for i in fullCorids if i not in nowTask]

    for i in repeat:
        cnt += i['cnt']
        coid = i['_id']['corporateIds'][0]
        thisIdTask = list(
            collection.find({'corporateIds': coid}).sort("processStatus", pymongo.DESCENDING))  # process=1的排在前面
        if len(lostCorids) == 0: break
        for t in thisIdTask[1:]:
            taskid = t['_id']
            if t['processStatus'] != 0:
                logger.info('processed taskId:%s', taskid)
                continue
            lostid = lostCorids.pop(0)
            collection.update_one({'_id': taskid}, {'$set': {'corporateIds': [lostid]}})


def tag_task():
    string = u'''victor 215 智能硬件#企业服务#传统行业#房地产#工具类
avery 214 旅游#金融#教育
arthur 221 大数据#社交#先进制造#VRAR
marchy 2706 消费#生活服务#汽车交通#物流仓储
sweety 1091 医疗#人工智能#农业#文化娱乐
晓婷 219 物联网#机器人#体育'''
    tagMap = {}
    for row in string.split('\n'):
        lis = row.split()
        user, tags = lis[1].strip(), lis[-1].strip()
        # if user!='2706':continue
        for tag in tags.split('#')[:1]:
            tagMap[tag] = user

    mongo = db.connect_mongo()
    collection = mongo['open-maintain'].task
    collectionUser = mongo['open-maintain'].user
    conn = db.connect_torndb()

    allcoids = [task['corporateIds'][0] for task in list(mongo.task.homework_company.find(
        {'createTime': {'$lt': datetime.datetime(2017, 12, 20)}, "assignee": {'$ne': -544}}))]

    for tag in tagMap:
        # results = conn.query('select * from company where corporateid=%s and (active="Y" or active is null)', coid)
        # cids = [i['id'] for i in results]

        results = conn.query('''select distinct c.corporateid coid,c.id cid
        from company c
        left join company_tag_rel r on r.companyId=c.id and (r.active = 'Y' or r.active is null)
        left join tag t on r.tagId=t.id and (t.active = 'Y' or t.active is null)
        where t.name=%s and c.corporateid in %s
        ''', tag, allcoids)
        conn.close()

        cnt = 0

        for r in results[:100]:
            if cnt == 50: break
            if collection.find_one({'companyId': r['cid'], 'section': 'tag'}) is not None:
                logger.info('already exists company:%s |section:%s', r['cid'], 'tag')
                continue
            # logger.info('insert  company:%s |section:%s |user:%s', r['cid'], 'tag',tagMap[tag])
            assignTask(r['cid'], 'tag', int(tagMap[tag]), 'N')
            cnt += 1

    string = u'''victor 215 智能硬件#企业服务#传统行业#房地产#工具类
avery 214 旅游#金融#教育
arthur 221 大数据#社交#先进制造#VRAR
marchy 2706 消费#生活服务#汽车交通#物流仓储
sweety 1091 医疗#人工智能#农业#文化娱乐
晓婷 219 物联网#机器人#体育'''
    # db.task.aggregate([{$match:{taskUser:{$in:[215,214,221,2706,1091,219]},'createTime':{'$gt':ISODate("2018-01-01T19:59:53.416Z")},section:'tag'}},{$group:{_id: '$taskUser', cnt: {$sum:1}}}])
    for row in string.split('\n'):
        lis = row.split()
        user, tags = lis[1].strip(), lis[-1].strip()
        result=list(collection.find({'taskUser':user,'section':'tag'}))
        if len(result)!=50:
            print 'here'
        else:
            collection.update_many({'taskUser':user,'section':'tag'},{'$set':{'taskUser':int(user)}})



if __name__ == "__main__":

    init_kafka()
    while True:
        try:
            logger.info("start")
            # logger.info(kafkaConsumer)
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    # msg: type:XXXX, name :xxxx
                    logger.info(json.dumps(msg, ensure_ascii=False, cls=util.CJsonEncoder))

                    # {u'posting_time': 1513233018091, u'from': u'atom', u'task_id': u'5a31e118346dbf6bd34caf58'}
                    taskid = msg['task_id']
                    mongo = db.connect_mongo()
                    collection = mongo['open-maintain'].task
                    task = collection.find_one({'_id': ObjectId(taskid)})
                    mongo.close()

                    sectionMap = {'funding': 'tag', 'memberAndRecruitment': 'artifact', 'artifact': 'news',
                                  'tag': 'memberAndRecruitment', 'basic': 'funding', 'news': 'industryAndComps'}

                    if task.get('flow') == 'N':
                        logger.info("don't flow %s|%s", task['companyId'], task['section'])
                        kafkaConsumer.commit()
                    else:
                        if sectionMap.has_key(task['section']):
                            section = sectionMap[task['section']]
                            if section == 'news':
                                if mongo.article.news.find_one(
                                        {'type': {'$ne': 61000}, 'companyIds': task['companyId']}) is None:
                                    section = sectionMap['news']

                            assign_company(task['companyId'], section)
                            kafkaConsumer.commit()
                        else:
                            logger.info('wrong section:%s', task['section'])


                except Exception, e:
                    traceback.print_exc()
                    # break
        except KeyboardInterrupt:
            logger.info("break1")
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()
