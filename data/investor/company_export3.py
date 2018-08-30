# -*- coding: utf-8 -*-
# tag 任务
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db, datetime

# logger
loghelper.init_logger("export_audit", stream=True)
logger = loghelper.get_logger("export_audit")

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

companyStatusMap = {
    2010: '正常',
    2015: '融资中',
    2020: '已关闭',
    2025: '停止更新',
    0: '正常',
}


def getinfo(companyId, corporateId):
    info = ""
    verfyinfo = ""
    conn = db.connect_torndb()
    cor = conn.query("select * from corporate where (active is null or active='Y')"
                     " and verify is null and id=%s", corporateId)
    if len(cor) > 0: verfyinfo += "corporate "
    comp = conn.query("select * from company where (active is null or active='Y')"
                      " and verify is null and id=%s", companyId)
    if len(comp) > 0: verfyinfo += "基本信息 "
    fundings = conn.query("select * from funding f left join corporate c on f.corporateId=c.id "
                          "where f.corporateId=%s and (c.active is null or c.active='Y')  and "
                          "(f.active is null or f.active='Y') and f.verify is null", corporateId)
    if len(fundings) > 0: verfyinfo += "融资 "
    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                           "and verify is null", companyId)
    if len(artifacts) > 0: verfyinfo += "产品 "
    members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                         "where cmr.companyId=%s and m.verify is null and "
                         "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                         "(cmr.active is null or cmr.active='Y')", companyId)
    if len(members) > 0: verfyinfo += "团队 "
    comaliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')"
                            " and verify is null and type=12020", companyId)
    if len(comaliases) > 0: verfyinfo += "产品线短名 "
    corpaliaes = conn.query("select * from corporate_alias where (active is null or active='Y') "
                            "and verify is null  and corporateId=%s", corporateId)
    if len(corpaliaes) > 0: verfyinfo += "corporate公司名 "
    comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                         "(active is null or active='Y') and verify is null", companyId)
    if len(comrecs) > 0:  verfyinfo += "招聘 "

    conn.close()
    if len(verfyinfo) > 0:
        info = verfyinfo + "未verify"
    else:
        info = "都verify"
    logger.info("company: %s->%s", companyId, info)
    return info


def asign(tasksMap):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection = mongo.task.homework_company

    # remove duplicate tasks
    coids = [coid for coid in tasksMap]
    dupCoids = list(collection.find({'corporateIds': {'$in': coids}}))
    dupCoids = [i['corporateIds'][0] for i in dupCoids]

    for coid in dupCoids:
        try:
            del tasksMap[coid]
        except:
            pass

    sql = '''select u.id userId,u.username,u.active from user u
    join  user_organization_rel uo on u.id=uo.userid 
    where uo.organizationid=51 and u.active='Y'
    and u.id not in (226, 1140, 4066)   
    and u.username not in ("汪甜","秦成","焦俊鹏","魏广肖","刘兵")'''
    uids = [c.userId for c in conn.query(sql)]

    # split yitai and xiniu
    # len([i for i in tasksMap if tasksMap[i]['yitai']==True])
    tasksYitai = [i for i in tasksMap if tasksMap[i]['yitai'] == True][:int(len(tasksMap) / 2)]

    i = 0
    for coid in tasksMap:
        if collection.find_one({'corporateIds': coid}) is not None:
            logger.info('already exists corporate:%s', coid)
        else:
            logger.info('inserting corporate:%s', coid)
            if coid in tasksYitai:
                assignee = -544
            else:
                assignee = uids[i]
                i += 1
                if i >= len(uids):
                    i = 0

            collection.insert_one({"corporateIds": [coid],
                                   "taskType": 1,
                                   "createTime": datetime.datetime.now(),
                                   "processStatus": 0,
                                   "auditStatus": 0,
                                   "assignee": assignee,
                                   "memo": tasksMap[coid]['vinfo']})

            # db.homework_company.aggregate([{'$match':{"createTime": {'$gt':ISODate("2017-12-25T0:44:24.994Z")}}},{$group:{_id:'$assignee',cnt:{$sum:1}}}])


def resign_sb(userIds, rest):
    # 2017-1-4 14:30 分的
    # arthur、avery、Marchy、Victor、小婷
    userIds = [214, 215, 219, 221, 2706]
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection = mongo.task.homework_company

    sql = '''select u.id userId,u.username,u.active from user u
     join  user_organization_rel uo on u.id=uo.userid 
     where uo.organizationid=51 and u.active='Y'
     and u.id not in (226, 1140, 4066)   
     and u.username not in ("汪甜","秦成","焦俊鹏","魏广肖","刘兵")'''

    uids = [c.userId for c in conn.query(sql) if c.userId not in userIds]
    i = 0
    for userId in userIds:
        userTask = list(collection.find({'assignee': userId, 'processStatus': 0}))

        for t in userTask[:len(userTask) - rest]:
            coid = t['corporateIds'][0]
            logger.info('updating corporate:%s of user:%s', coid, userId)
            assignee = uids[i]
            i += 1
            if i >= len(uids):
                i = 0

            collection.update_one({'_id': t['_id']},
                                  {'$set':
                                       {"modifyTime": datetime.datetime.now(),
                                        "assignee": assignee,
                                        }})


def stat():
    import datetime
    import pandas as pd
    mongo = db.connect_mongo()
    conn = db.connect_torndb()

    df1 = pd.DataFrame(list(mongo.task.homework_company.aggregate(
        [{'$match': {"createTime": {'$gt': datetime.datetime(2016, 12, 25)}}}, {'$group': {
            '_id': '$assignee', 'cnt': {'$sum': 1}}}])))
    df2 = pd.DataFrame(list(mongo.task.homework_company.aggregate(
        [{'$match': {"createTime": {'$gt': datetime.datetime(2017, 12, 25)}}}, {'$group': {
            '_id': '$assignee', 'cnt': {'$sum': 1}}}])))

    sql = '''select u.id userId,u.username from user u
     join  user_organization_rel uo on u.id=uo.userid 
     where uo.organizationid=51 and u.active='Y'
     '''
    df3 = pd.DataFrame(conn.query(sql))

    df4 = pd.merge(df1, df2, on='_id', how='outer')
    df4 = pd.merge(df4, df3, left_on='_id', right_on='userId', how='left')
    df4.to_excel('export.xlsx', index=0)


def grouptask():
    tasksCom=[i['companyId'] for i in list(collecionpretask.find())]


    string = u'''avery，小娇：旅游，金融，教育
arthur，梦梦：大数据，社交，先进制造，VRAR
victor，张力：传统行业，工具类，智能硬件，企业服务，房地产
汪甜，广肖，刘兵：医疗，人工智能，文化娱乐，农业
晓婷：物联网，机器人，体育
marchy，bamy，继松：物流，汽车交通，生活服务，消费'''
    tagMap = {}
    for row in string.split('\n'):
        lis = row.split('：')
        user, tags = lis[0].split('，')[0], lis[-1].strip()
        for tag in tags.split('，'):
            tagMap[tag] = user

    tags = [i.strip() for i in tagMap]
    # {'房地产':victor}

    conn = db.connect_torndb()
    company_tags = conn.query('''
     select distinct r.companyId cid,t.name tagName
     from company_tag_rel r 
     join tag t on t.id=r.tagId
     where (r.active is null or r.active='Y') 
     and (t.active is null or t.active='Y')
     and r.companyId in %s
     and t.name in %s
     order by r.confidence desc
     ''', tasksCom, tags)

    # 没有一级 tag 的怎么分 ？
    import pandas as pd
    import random
    df = pd.DataFrame(company_tags)
    cnt = df.cid.value_counts()

    df['assinee'] = df.apply(lambda x: tagMap.get(x.tagName), axis=1)

    taskFinalMap = {}
    cnt[cnt == 1].count()
    cnt1 = cnt[cnt == 1].to_frame()
    for index, row in cnt1.iterrows():
        cid = int(index)
        tag = df[df.cid == cid].ix[:, 'tagName'].reset_index(drop=True)[0]
        assinee = tagMap[tag]
        if not taskFinalMap.has_key(assinee): taskFinalMap[assinee] = []
        taskFinalMap[assinee] = taskFinalMap[assinee] + [cid]

    cnt2 = cnt[cnt > 1].to_frame()
    for index, row in cnt2.iterrows():
        cid = int(index)
        cid= 24157
        print 'cid:',cid
        candidates = df[df.cid == cid].ix[:, 'assinee'].reset_index(drop=True)
        candidates = list(set(list(candidates)))

        allcnt = 0
        rangeMap = {}
        # {'victor':100,'avery':110}
        for candidate in candidates:
            allcnt += len(taskFinalMap[candidate])

        allcnt2 = 0
        for candidate in candidates:
            print candidate
            rangeMap[candidate] = allcnt - len(taskFinalMap[candidate]) + allcnt2
            allcnt2 += allcnt - len(taskFinalMap[candidate])
            allcnt += 1

        randomcnt = random.uniform(0, allcnt2)
        print randomcnt
        print rangeMap

        for candidate in candidates:
            if randomcnt <= rangeMap[candidate]:
                assinee = candidate
                break

        print assinee
        if not taskFinalMap.has_key(assinee): taskFinalMap[assinee] = []
        taskFinalMap[assinee] = taskFinalMap[assinee] + [cid]

    cnt3 = 0
    for i in taskFinalMap:
        print i, len(taskFinalMap[i])
        cnt3 += len(taskFinalMap[i])
    cnt3

    mongo = db.connect_mongo()
    collecionpretask = mongo['open-maintain'].pretask
    for i in taskFinalMap:
        for cid in taskFinalMap[i]:
            if collecionpretask.find_one({'companyId': cid}) is None:
                logger.info('inserting companyId:%s', cid)
                collecionpretask.insert_one({'leader': i,
                                             'companyId': cid,
                                             })
            else:
                logger.info('already exists companyId:%s', cid)

            #     string = u'''avery，小娇：旅游，金融，教育
            # arthur，梦梦：大数据，社交，先进制造，VRAR
            # victor，张力：传统行业，工具类，智能硬件，企业服务，房地产
            # 汪甜，广肖，刘兵：医疗，人工智能，文化娱乐，农业
            # 晓婷：物联网，机器人，体育
            # marchy，bamy，继松：物流，汽车交通，生活服务，消费'''
            #     tagMap = {}
            #     for row in string.split('\n'):
            #         lis = row.split('：')
            #         leader, tags = lis[0].split('，')[0], lis[-1].strip()
            #         alluser = lis[0].split('，')
            #         for tag in tags.split('，')[:1]:
            #             coids = list(collecionpretask.find({'leader': leader}))
            #             coids = [i['companyId'] for i in coids]
            #             companys = conn.query('''
            #                  select distinct r.companyId cid
            #                  from company_tag_rel r
            #                  join tag t on t.id=r.tagId
            #                  where (r.active is null or r.active='Y')
            #                  and (t.active is null or t.active='Y')
            #                  and r.companyId in %s
            #                  and t.name = %s
            #                  order by r.confidence desc
            #                  ''', coids, tag)
            #
            #             for c in companys:
            #                 colleciontask = mongo['open-maintain'].task
            #                 if colleciontask.find_one({'companyId': c['cid']}) is None:
            #                     logger.info('already exists companyId:%s', c['cid'])
            #                 else:
            #                     logger.info('insert companyId:%s', c['cid'])

    def assign_tag():
        mongo = db.connect_mongo()
        conn = db.connect_torndb()

        colleciontask = mongo['open-maintain'].task
        collecionpretask = mongo['open-maintain'].pretask

        # for leader in collecionpretask.distinct('leader'):

        string = u'''avery	214
        小娇	10159
        arthur	221
        梦梦	3477
        victor	215
        张力	10424
        汪甜	1091
        广肖	6936
        刘兵	6868
        晓婷	219
        marchy	2706
        bamy	220
        继松	223'''
        idMap = {}
        for row in string.split('\n'):
            lis = row.split('\t')
            idMap[lis[0].strip()] = int(lis[1])

        string = u'''avery，小娇：旅游，金融，教育
        arthur，梦梦：大数据，社交，先进制造，VRAR
        victor，张力：传统行业，工具类，智能硬件，企业服务，房地产
        汪甜，广肖，刘兵：医疗，人工智能，文化娱乐，农业
        晓婷：物联网，机器人，体育
        marchy，bamy，继松：物流，汽车交通，生活服务，消费'''
        for row in string.split('\n'):
            lis = row.split('：')
            leader, tags = lis[0].split('，')[0], lis[-1].strip().split('，')
            alluser = lis[0].split('，')
            # thistag = tags[0].strip()

            for thistag in tags[:]:
                logger.info('leader:%s ,user:%s , tag:%s' % (leader, ','.join(alluser), thistag))

                thisgrouptask = list(collecionpretask.find({'leader': leader}))
                company_tags = conn.query('''
                select distinct r.companyId from company_tag_rel r 
                join tag t on t.id=r.tagId
                where (r.active is null or r.active='Y') 
                and (t.active is null or t.active='Y')
                and t.name=%s
                ''', thistag)
                thistagcompany = [i['companyId'] for i in company_tags]  # 有这个 tag 的公司
                finalgrouptask = [i['companyId'] for i in thisgrouptask if i['companyId'] in thistagcompany]

                alluserid = [idMap[i] for i in alluser]
                idindex = 0
                for cid in finalgrouptask:
                    collection = mongo['open-maintain'].task
                    if collection.find_one({'companyId': cid, 'section': 'tag'}) is not None:
                        logger.info('already exists company:%s |section:%s', cid, 'tag')
                        continue

                    assinee = alluserid[idindex]
                    idindex += 1
                    if idindex >= len(alluserid):
                        idindex = 0
                    assignTask(cid, 'tag', assinee, 'N', u'第二批 tag 任务')

    big = list(collecionpretask.find({'leader': 'avery'}))
    little = list(colleciontask.find({'taskUser': {'$in': [214, 10159]}}))
    little = [i['companyId'] for i in little]
    lost = [i['companyId'] for i in big if i['companyId'] not in little]

def debug():
    big = list(collecionpretask.find({}))
    # little = list(colleciontask.find({'$or':[{"memo" : "第二批 tag 任务"},{"memo" : "第一批 tag 任务"}]}))
    little = list(colleciontask.find({'section':'tag','taskUser':{'$ne':None}}))
    little = [i['companyId'] for i in little]
    lost = [i['companyId'] for i in big if i['companyId'] not in little]

    for cid in lost:
        candidates = df[df.cid == cid].ix[:, 'assinee'].reset_index(drop=True)
        candidates = list(set(list(candidates)))
        print 'cid:',cid

        allcnt = 0
        rangeMap = {}
        # {'victor':100,'avery':110}
        for candidate in candidates:
            allcnt += len(taskFinalMap[candidate])

        allcnt2 = 0
        for candidate in candidates:
            print candidate
            rangeMap[candidate] = allcnt - len(taskFinalMap[candidate]) + allcnt2
            allcnt2 += allcnt - len(taskFinalMap[candidate])

        randomcnt = random.uniform(0, allcnt2)
        print randomcnt
        print rangeMap
        for candidate in candidates:
            if randomcnt <= rangeMap[candidate]:
                assinee = candidate
                break

        print assinee
        # continue


        mongo = db.connect_mongo()
        collecionpretask = mongo['open-maintain'].pretask2

        if collecionpretask.find_one({'companyId': cid}) is None:
            logger.info('inserting companyId:%s', cid)
            collecionpretask.insert_one({'leader': assinee,
                                         'companyId': cid,
                                         'memo': u'第三批 tag 任务'
                                         })
        else:
            logger.info('already exists companyId:%s', cid)





        # taskFinalMap[assinee] = taskFinalMap[assinee] + [cid]


    def assign_tag():
        mongo = db.connect_mongo()
        conn = db.connect_torndb()

        colleciontask = mongo['open-maintain'].task
        collecionpretask = mongo['open-maintain'].pretask2

        # for leader in collecionpretask.distinct('leader'):

        string = u'''avery	214
        小娇	10159
        arthur	221
        梦梦	3477
        victor	215
        张力	10424
        汪甜	1091
        广肖	6936
        刘兵	6868
        晓婷	219
        marchy	2706
        bamy	220
        继松	223'''
        idMap = {}
        for row in string.split('\n'):
            lis = row.split('\t')
            idMap[lis[0].strip()] = int(lis[1])

        string = u'''avery，小娇：旅游，金融，教育
        arthur，梦梦：大数据，社交，先进制造，VRAR
        victor，张力：传统行业，工具类，智能硬件，企业服务，房地产
        汪甜，广肖，刘兵：医疗，人工智能，文化娱乐，农业
        晓婷：物联网，机器人，体育
        marchy，bamy，继松：物流，汽车交通，生活服务，消费'''
        for row in string.split('\n'):
            lis = row.split('：')
            leader, tags = lis[0].split('，')[0], lis[-1].strip().split('，')
            alluser = lis[0].split('，')
            # thistag = tags[0].strip()

            for thistag in tags[:]:
                logger.info('leader:%s ,user:%s , tag:%s' % (leader, ','.join(alluser), thistag))

                thisgrouptask = list(collecionpretask.find({'leader': leader}))
                company_tags = conn.query('''
                select distinct r.companyId from company_tag_rel r 
                join tag t on t.id=r.tagId
                where (r.active is null or r.active='Y') 
                and (t.active is null or t.active='Y')
                and t.name=%s
                ''', thistag)
                thistagcompany = [i['companyId'] for i in company_tags]  # 有这个 tag 的公司
                finalgrouptask = [i['companyId'] for i in thisgrouptask if i['companyId'] in thistagcompany]

                alluserid = [idMap[i] for i in alluser]
                idindex = 0
                for cid in finalgrouptask:
                    collection = mongo['open-maintain'].task
                    if collection.find_one({'companyId': cid, 'section': 'tag'}) is not None:
                        logger.info('already exists company:%s |section:%s', cid, 'tag')
                        continue

                    assinee = alluserid[idindex]
                    idindex += 1
                    if idindex >= len(alluserid):
                        idindex = 0
                    assignTask(cid, 'tag', assinee, 'N', u'第三批 tag 任务')




def tag_stat():
    #  db.task.aggregate([{$match:{"memo" : "第二批 tag 任务",section:'tag'}},{$group:{_id: '$taskUser', cnt: {$sum:1}}}])

    import datetime
    import pandas as pd
    mongo = db.connect_mongo()
    conn = db.connect_torndb()

    df1 = pd.DataFrame(list(mongo['open-maintain'].task.aggregate(
        [{'$match': {'$or':[{"memo" : "第三批 tag 任务"},{"memo" : "第二批 tag 任务"},{"memo" : "第一批 tag 任务"}]}}, {'$group': {
            '_id': '$taskUser', '任务量': {'$sum': 1}}}])))

    string = u'''李锦香，焦俊鹏：旅游，金融，教育
    杜强，王梦梦：大数据，社交，先进制造，VRAR
    周煜东，张力：传统行业，工具类，智能硬件，企业服务，房地产
    汪甜，魏广肖，刘兵：医疗，人工智能，文化娱乐，农业
    潘晓婷：物联网，机器人，体育
    马永琦，徐俊磊，王继松：物流，汽车交通，生活服务，消费'''
    grouplist = []
    for row in string.split('\n'):
        lis = row.split('：')
        leader, tags = lis[0].split('，')[0], lis[-1].strip().split('，')
        alluser = lis[0].split('，')
        for u in alluser:
            grouplist.append({'leader': leader, 'username': u, u'行业': tags[0]})

    df2 = pd.DataFrame(grouplist)

    sql = '''select u.id userId,u.username from user u
     join  user_organization_rel uo on u.id=uo.userid 
     where uo.organizationid=51 and u.active='Y'
     '''
    df3 = pd.DataFrame(conn.query(sql))

    df4 = pd.merge(df1, df3, left_on='_id', right_on='userId', how='left')
    df4 = pd.merge(df4, df2, on='username', how='left')
    df4 = df4.ix[:, ['leader', u'行业', 'username', u'任务量']].sort_values('leader').set_index(
        ['leader', 'username'])

    df4.to_excel('export.xlsx', index=1)


def assignTask(companyId, section, assignee, flow='Y', memo=''):
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


if __name__ == '__main__':
    logger.info("Begin...")
    year = 2013
    endYear = 2015
    num = 0
    num2 = 0
    conn = db.connect_torndb()
    icompanies = conn.query("select * from company where (active is null or active !='N')")
    results = []
    tasksMap = {}
    tasksCom = []
    for company in icompanies:
        if company["id"] is None or company["corporateId"] is None: continue
        corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
        if corporate["locationId"] is not None and corporate["locationId"] > 370: continue

        company["xiniuInvestor"] = "N"
        company["itjuziInvestor"] = "N"
        company["kr36Investor"] = "N"

        fundings = conn.query("select * from funding where (active is null or active='Y')"
                                " and "
                               "((publishDate is not null and publishDate>='%s-01-01')"
                               " or "
                               "(publishDate is null and fundingDate>='%s-01-01'))"
                               "and ((publishDate is not null and publishDate<'%s-01-01')"
                               " or "
                               "(publishDate is null and fundingDate<'%s-01-01'))"
                              " and corporateId=%s", year,year,endYear,endYear, company["corporateId"])
        if len(fundings) == 1 and fundings[0]["round"] is not None and fundings[0]["round"] in [1105,
                                                                                                1110]: continue

        if len(fundings) >= 1: company["xiniuInvestor"] = "Y"

        for sname in ["itjuziInvestor", "kr36Investor"]:
            sfundings = []
            if sname == "kr36Investor":
                source = 13022
            else:
                source = 13030

            scs = conn.query("select id from source_company where companyId=%s and source=%s and "
                             "(active is null or active!='N')", company["id"], source)
            if len(scs) > 0:

                for sc in scs:
                    sfundings = conn.query("select * from source_funding where sourceCompanyId =%s and "
                                           "fundingDate>='%s-01-01' and fundingDate <'%s-01-01'", sc["id"], year,
                                           endYear
                                           )

                    if len(sfundings) >= 1:
                        # logger.info(sfundings[0])
                        company[sname] = "Y"

        if company["xiniuInvestor"] == "Y" or company["itjuziInvestor"] == "Y" or company["kr36Investor"] == "Y":
            logger.info("%s/%s/%s/%s", company["code"], company["xiniuInvestor"], company["itjuziInvestor"],
                        company["kr36Investor"])

            num += 1

            if company["locationId"] is not None:
                lc = conn.get("select * from location where locationId=%s", company["locationId"])
                if lc is not None:
                    location = lc["locationName"]
                else:
                    location = None
            else:
                location = None

            company_tags = conn.query('''
        select t.name from company_tag_rel r 
        join tag t on t.id=r.tagId
        where (r.active is null or r.active='Y') and r.companyId=%s
        and (t.active is null or t.active='Y')
        and t.type in (11100,11012)
        ''',
                                      company["id"])

            if company is None: continue

            roundDesc = " "
            if company["corporateId"] is None: continue

            corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
            if corporate is None: continue

            rounda = corporate["round"]
            roundDesc = rmap[int(rounda)] if (rounda is not None and rmap.has_key(int(rounda))) else " "

            # vinfo = getinfo(company["id"], company["corporateId"])

            # if vinfo != "都verify":
            if 1:
                num2 += 1

                # fundings = conn.query("select * from funding where (active is null or active='Y')"
                #                       " and corporateId=%s and round in (1105,1110)", company["corporateId"])
                # companies = conn.query("select * from company where (active is null or active='Y')"
                #                        " and corporateId=%s", company["corporateId"])
                # yitai = True if len(fundings) == 0 and len(companies) == 1 and (
                #     company['active'] is None or company['active'] == 'Y') else False
                tasksMap[company["corporateId"]] = {'yitai': 1}
                tasksCom.append(company['id'])
                # print 'status:',company['companyStatus'],company["code"]
                # lineList = [company["name"], company["code"],
                #             company["id"], roundDesc,
                #             company["brief"] if (
                #                 company["brief"] is not None and company["brief"].strip() != "") else " ",
                #             company["xiniuInvestor"],
                #             company["itjuziInvestor"],
                #             company["kr36Investor"],
                #             vinfo, company['establishDate'],
                #             'http://www.xiniudata.com/file/%s/product.png' % company['logo'],
                #             company['website'],
                #             company['description'],
                #             company['fullName'],
                #             location,
                #             companyStatusMap.get(company['companyStatus']),
                #             ','.join([i['name'] for i in company_tags])
                #
                #             ]

                # results.append(lineList)
                # fp.write(line)

    # import pandas as pd
    #
    # df = pd.DataFrame(results, columns=['name', 'companyCode', 'id', 'round', 'brief', 'xiniuInvestor', 'itjuziInvestor',
    #                                     'kr36Investor',
    #                                     'verify', 'establishDate',
    #                                     'logo', 'website',
    #                                     'description', 'fullName', 'locationName', 'companyStatus','tagVOs'])
    #
    # for c in df.columns:
    #     def illegal(row):
    #         import re
    #         content = row[c]
    #         if content is not None:
    #             ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    #             # print 'content:',c,content
    #             try:
    #                 content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
    #             except:
    #                 pass
    #         return content
    #
    #     # print 'c:',c
    #     df[c] = df.apply(illegal, axis=1)
    #
    # df.to_excel('export.xlsx', index=0,
    #             columns=["companyCode", "name", "establishDate", "logo", "website", "description", "fullName", "round",
    #                      "locationName", "companyStatus", "tagVOs", "xiniuInvestor", "itjuziInvestor", "kr36Investor",
    #                      "gongshangInvestor", "brief", "fullNames", "RepeatWith", "verify"])


    conn.close()
    logger.info("num: %s/%s", num2, num)
    logger.info("End.")
