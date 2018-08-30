# -*- coding: utf-8 -*-
import os, sys, re, json, time, datetime
from bson.objectid import ObjectId
from lxml import html
from pyquery import PyQuery as pq
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper
import db

# logger
loghelper.init_logger("score_util", stream=True)
logger = loghelper.get_logger("score_util")


def getCompanyScore(companyId):
    '''
序列	维度	评分
1	有产品	4 d
2	最近活跃（今日活跃、7日内活跃）	2 d
3	工商16年之后	3
4	工商13年之后	2
5	工商13年之前	1
6	招聘职位	1
7	拉勾是否认证	1
8	成员	1
9	logo	1
    '''
    score = 0

    gongshang = find_gongshang_by_companyid(companyId)
    if gongshang == -1: return -1

    gongshangScore = 0
    for g in gongshang:
        logger.info('gongshang:%s',g['name'])
        establishTime = g['establishTime'] if g.has_key('establishTime') else None
        if establishTime is not None and isinstance(establishTime,datetime.datetime):
            if establishTime.year >= 2016:
                gongshangPlus = 3
            elif establishTime.year >= 2013:
                gongshangPlus = 2
            elif establishTime.year < 2013:
                gongshangPlus = 1
            else:
                print 'here:', establishTime
                exit()
        else:
            gongshangPlus = 0
        if gongshangPlus > gongshangScore: gongshangScore = gongshangPlus
    score += gongshangScore

    # artifact cnt
    conn = db.connect_torndb()
    sql = '''select count(distinct a.id) cnt from artifact a where companyid=%s and (a.active = 'Y' or a.active is null)
             and type in (4010,4040,4050)'''
    if conn.query(sql, companyId)[0]['cnt'] >= 1: score += 4

    # lagou dimension
    lagouId = conn.query('''select * from source_company where companyid=%s''', companyId)[0]['sourceId']
    logger.info('lagouId:%s', lagouId)
    mongo = db.connect_mongo()
    lagouCompany = mongo.job.company.find_one({'source':13050,'sourceId': lagouId})

    if lagouCompany is None:
        print 'lagouId:%s job.company is None' % (lagouId)
        # return -1
    else:
        # if lagouCompany['fullName'] is not None and lagouCompany['fullName'].strip() != '': score += 2
        if lagouCompany['logo'] is not None and lagouCompany['logo'].strip() != '': score += 1
        # if len(lagouCompany['artifacts']) > 0: score += 2
        if len(lagouCompany['members']) > 0: score += 1

    lagouHtml = list(mongo.raw.projectdata.find({'source': 13050, 'key': lagouId}).sort('date', pymongo.DESCENDING))
    if len(lagouHtml) == 0 or isinstance(lagouHtml[0]['content'], dict):
        logger.info('lagouId:%s html got some problem', lagouId)
    else:
        d = pq(html.fromstring(lagouHtml[0]['content'].decode("utf-8")))
        lastLogin = d('.company_data li:nth-child(5) strong').text()
        headCnt = d('.company_data li:nth-child(1) strong').text()
        identity = d('.company_main .company_word').prev().attr('title')
        logger.info('%s -> %s -> %s',lastLogin,headCnt,identity)
        if lastLogin.find('今天') >= 0 or lastLogin.find('昨天') >= 0 or lastLogin.find('7天内') >= 0: score += 2
        if headCnt is not None and headCnt.strip()!='' and headCnt is not None and headCnt.find('暂无')  < 0: score += 1
        if headCnt is not None and headCnt.strip()!='' and identity is not None and identity.find('未认证') < 0: score += 1

    conn.close()
    mongo.close()

    return score

def checkjob(companyId):

    score = 0
    conn = db.connect_torndb()

    # lagou dimension
    lagouId = conn.query('''select * from source_company where companyid=%s''', companyId)[0]['sourceId']
    logger.info('lagouId:%s', lagouId)
    mongo = db.connect_mongo()

    lagouHtml = list(mongo.raw.projectdata.find({'source': 13050, 'type':36001, 'key': lagouId}).sort('date', pymongo.DESCENDING))
    if len(lagouHtml) == 0 or isinstance(lagouHtml[0]['content'], dict):
        logger.info('lagouId:%s html got some problem', lagouId)
    else:
        d = pq(html.fromstring(lagouHtml[0]['content'].decode("utf-8")))
        headCnt = d('.company_data li:nth-child(1) strong').text()
        identity = d('div.company_main> a> span').prev().attr('title')
        if headCnt is not None and headCnt.strip()!='' and headCnt is not None and headCnt.find('暂无')  < 0: score += 1
        if identity is not None and identity.find('资质认证') >= 0: score += 1
    conn.close()
    mongo.close()

    return score


def find_gongshang_by_companyid(companyId):
    conn = db.connect_torndb()
    sql = '''
    select distinct ca.name,ca.gongshangCheckTime
    from corporate_alias ca join company c on c.corporateId=ca.corporateId
    where (ca.active = 'Y' or ca.active is null)
    and c.id = %s
    '''
    result = conn.query(sql, companyId)

    # 只要任意一个fullname还没check过工商，return -1
    for g in result:
        gongshangCheckTime = g['gongshangCheckTime']

        if gongshangCheckTime is not None:
            if gongshangCheckTime > (datetime.datetime.now() + datetime.timedelta(hours=-1)):
                return -1
        else:
            return -1

    fullNames = [i['name'] for i in result]
    conn.close()

    mongo = db.connect_mongo()
    collection = mongo.info.gongshang
    gongshangs = list(collection.find({'name': {'$in': fullNames}}))
    mongo.close()

    return gongshangs


def save_score(cid, score):
    conn = db.connect_torndb()
    # sql = '''select * from company_scores
    #          where companyId=%s and type=37040'''
    #
    score_old = get_score(cid)
    if score_old is None:
        sql = '''
            insert company_scores (companyId,score,type,createTime,modifyTime)\
                           values(%s,%s,37040,now(),now())
        '''
        csid = conn.insert(sql, cid, score)
    else:
        if int(score_old) != int(score):
            conn.update('''update company_scores set score=%s,modifyTime=now() where companyId=%s and type=37040''',
                        score, cid)
    conn.close()


def get_score(cid):
    conn = db.connect_torndb()
    sql = '''select * from company_scores
             where companyId=%s and type=37040 order by score desc'''
    scores = conn.query(sql, cid)
    if len(scores) == 0:
        score = None
    else:
        score = scores[0]["score"]
    conn.close()
    return score

def get_score_all():
    conn = db.connect_torndb()
    sql = '''
           select c.id,c.code,count(distinct sc.id) cnt1,count(distinct case when sc.source=13050 then sc.id end) cnt2
           from company c join source_company sc on c.id=sc.companyId
           where (c.active = 'P' or c.active='A')
           and (sc.active !='N' or sc.active is null)
           group by c.id
           having cnt1=1 and cnt1=cnt2
           '''
    result = conn.query(sql)
    conn.close()
    ccids = [i['id'] for i in result]
    logger.info('%s cids left', len(ccids))
    while len(ccids) > 0:
        ccid = ccids.pop(0)
        logger.info('cid: %s', ccid)
        score = getCompanyScore(ccid)
        logger.info('cid: %s| score:%s', ccid, score)
        if score == -1:
            ccids.append(ccid)
            continue

        save_score(ccid, score)

def deleteRubbish():
    def getinfo(companyId, corporateId):
        info = ""
        verfyinfo = ""
        conn = db.connect_torndb()
        cor = conn.query("select * from corporate where (active is null or active='Y')"
                         " and verify='Y' and id=%s", corporateId)
        if len(cor) > 0: verfyinfo += "corporate "
        comp = conn.query("select * from company where (active is null or active='Y')"
                          " and verify='Y' and id=%s", companyId)
        if len(comp) > 0: verfyinfo += "基本信息 "
        fundings = conn.query("select * from funding f left join corporate c on f.corporateId=c.id "
                              "where f.corporateId=%s and (c.active is null or c.active='Y')  and "
                              "(f.active is null or f.active='Y') and f.verify='Y'", corporateId)
        if len(fundings) > 0: verfyinfo += "融资 "
        artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                               "and verify='Y'", companyId)
        if len(artifacts) > 0: verfyinfo += "产品 "
        members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                             "where cmr.companyId=%s and m.verify='Y' and "
                             "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                             "(cmr.active is null or cmr.active='Y')", companyId)
        if len(members) > 0: verfyinfo += "团队 "
        comaliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')"
                                " and verify='Y' and type=12020", companyId)
        if len(comaliases) > 0: verfyinfo += "产品线短名 "
        corpaliaes = conn.query("select * from corporate_alias where (active is null or active='Y') "
                                "and verify='Y'  and corporateId=%s", corporateId)
        if len(corpaliaes) > 0: verfyinfo += "corporate公司名 "
        comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                             "(active is null or active='Y') and verify='Y'", companyId)
        if len(comrecs) > 0:  verfyinfo += "招聘 "

        conn.close()
        if len(verfyinfo) > 0:
            info = verfyinfo + "已verify"
        else:
            info = " "
        logger.info("company: %s->%s", companyId, info)
        return info

    def deleteCompany(companyId, corporateId):
        conn = db.connect_torndb()
        if len(conn.query('select * from company where corporateid=%s', corporateId)) > 1:
            logger('coid:%s has more than 1 corporate, check', corporateId)
            return
        else:
            conn.update('''update company set active='P' , modifyUser=875 , modifyTime=now() where id=%s''',
                        companyId)
            conn.update('''update corporate set active='P' , modifyUser=875 , modifyTime=now()  where id=%s''',
                        corporateId)
        conn.close()

    conn = db.connect_torndb()
    sql = '''
           select cs.companyid from company_scores cs
           join company c on cs.companyid=c.id  
           where cs.type=37040 and cs.score<2
           and c.active!='P'
           '''
    result = conn.query(sql)
    cids = [i['companyid'] for i in result]
    logger.info('%s cids left', len(cids))

    for cid in cids:
        company = conn.get('select * from company where id=%s limit 1', cid)
        if getinfo(cid, company['corporateId']) != " ":
            logger.info('%s verified, dunt delete', company['code'])
            # break
        else:
            deleteCompany(cid, company['corporateId'])

    conn.close()


if __name__ == "__main__":
    conn = db.connect_torndb()
    sql = '''
       select c.id,c.code,count(distinct sc.id) cnt1,count(distinct case when sc.source=13050 then sc.id end) cnt2
       from company c join source_company sc on c.id=sc.companyId
       where (c.active = 'Y' or c.active is null or c.active='A')
       and (sc.active = 'Y' or sc.active is null)
       and c.id not in
       (select companyid from company_scores where type=37040)
       group by c.id
       having cnt1=1 and cnt1=cnt2
       '''
    result = conn.query(sql)
    conn.close()
    cids = [i['id'] for i in result]
    logger.info('%s cids left',len(cids))

    while len(cids) > 0:
        cid = cids.pop(0)
        logger.info('cid: %s', cid)
        score = getCompanyScore(cid)
        logger.info('cid: %s| score:%s', cid, score)
        if score == -1:
            cids.append(cid)
            continue

        save_score(cid, score)
