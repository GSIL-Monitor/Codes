# -*- coding: utf-8 -*-
# 删除无金额和投资人的记录
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
    mongo = db.connect_mongo()
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

    desc = mongo.company.modify.find_one({'companyId': companyId, 'sectionName': 'desc'})
    if desc is None:  verfyinfo += "简介 "

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

    # specific users
    string = '''userId	username
    222	周海明
    224	魏巍
    225	沁慈
    875	龙梓豪
    3142	周玉彬
    3341	赵毅
    4831	刘金铜'''
    uids = []
    for row in string.split('\n')[1:]:
        uids.append(int(row.split()[0].strip()))

    # split yitai and xiniu
    # len([i for i in tasksMap if tasksMap[i]['yitai']==True])
    # tasksYitai = [i for i in tasksMap if tasksMap[i]['yitai'] == True][:int(len(tasksMap) / 2)]
    tasksYitai = [i for i in tasksMap if tasksMap[i]['yitai'] == True][:int(4329 / 2)]
    tasksYitai = []

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
                                   "memo": tasksMap[coid]['vinfo'],
                                   'mark':'2017融资任务'
                                   })

            # db.homework_company.aggregate([{'$match':{"createTime": {'$gt':ISODate("2017-12-25T0:44:24.994Z")}}},{$group:{_id:'$assignee',cnt:{$sum:1}}}])
            # db.homework_company.aggregate([{'$match':{'mark':'2017融资任务'}},{$group:{_id:'$assignee',cnt:{$sum:1}}}])


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


if __name__ == '__main__':
    logger.info("Begin...")
    year = 2015
    endYear = 2017
    num = 0
    num2 = 0
    conn = db.connect_torndb()
    icompanies = conn.query("select * from company where (active is null or active !='N')")
    results = []
    tasksMap = {}
    for company in icompanies:
        if company["id"] is None or company["corporateId"] is None: continue

        company["xiniuInvestor"] = "N"
        company["itjuziInvestor"] = "N"
        company["kr36Investor"] = "N"

        # fundings = conn.query("select * from funding where (active is null or active='Y')"
        #                       " and fundingDate>='%s-01-01' and fundingDate <'%s-01-01'"
        #                       " and corporateId=%s", year, endYear, company["corporateId"])
        fundings = conn.query("select * from funding where (active is null or active='Y')"
                              " and "
                              "((publishDate is not null and publishDate>='%s-01-01')"
                              " or "
                              "(publishDate is null and fundingDate>='%s-01-01'))"
                              "and ((publishDate is not null and publishDate<'%s-01-01')"
                              " or "
                              "(publishDate is null and fundingDate<'%s-01-01'))"
                              " and corporateId=%s", year, year, endYear, endYear, company["corporateId"])
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

            vinfo = getinfo(company["id"], company["corporateId"])

            if vinfo != "都verify":
                num2 += 1

                fundings = conn.query("select * from funding where (active is null or active='Y')"
                                      " and corporateId=%s and round in (1105,1110)", company["corporateId"])
                companies = conn.query("select * from company where (active is null or active='Y')"
                                       " and corporateId=%s", company["corporateId"])
                yitai = True if len(fundings) == 0 and len(companies) == 1 and (
                    company['active'] is None or company['active'] == 'Y') else False
                if vinfo.find(u'基本信息') < 0 and vinfo.find(u'融资') < 0 and vinfo.find(u'简介') < 0: yitai = False

                tasksMap[company["corporateId"]] = {'vinfo': vinfo, 'yitai': yitai}
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

    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection = mongo.task.homework_company

    # remove duplicate tasks
    coids = [coid for coid in tasksMap]
    dupCoids = list(collection.find({'corporateIds': {'$in': coids}}))
    dupCoids = [i['corporateIds'][0] for i in dupCoids]
    len(coids) - len(dupCoids)
