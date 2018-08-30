# -*- coding: utf-8 -*-
import sys, os

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper
import datetime

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../company'))
import company_aggregator_baseinfo

# logger
loghelper.init_logger("remove_weibo", stream=True)
logger = loghelper.get_logger("remove_weibo")

# id code name return ids  4010

deletedArtifact = []


def getCompany(link='weixin.qq.com', type=4010, ):
    conn = db.connect_torndb()
    link = '%%' + link + '%%'
    sql = '''select distinct c.id,c.code,c.name,a.link,a.domain from artifact a join company c on c.id=a.companyId where (a.link like '%s') and a.type=%s
                            and (a.active='Y' or a.active is null)
                             and (c.active='Y' or c.active is null)
      ''' % (link, type)

    # print sql

    results = conn.query(sql)  # TODO
    conn.close()
    # exit()
    # print len(results)

    ids = []
    for artifact in results:
        if artifact['id'] == 17609 or artifact['id'] == 156154: continue
        # if artifact['domain'] is None:
        #     flag, domain = url_helper.get_domain(artifact['link'])
        # else:
        #     domain = artifact['domain']
        # if domain == 'weibo.com':
        if 1:
            # print artifact['id'], artifact['code'], artifact['name']  # , artifact['link']
            ids.append(artifact['id'])
    return set(ids)


def remove_wechat(ids):
    totalCnt, totoalDelCnt = 0, 0

    for companyId in ids:
        # '''website set none'''
        conn = db.connect_torndb()
        # print companyId
        sql = '''select c.id, c.name as companyName,c.website from company c  where c.id=%s
              ''' % companyId
        results = conn.query(sql)
        conn.close()

        # print len(results)

        for company in results:
            totalCnt += 1
            # print company['website']
            if company['website'] is not None and company['website'].find('weixin.qq.com') > 0:
                totoalDelCnt += 1
                conn = db.connect_torndb()
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.update('''UPDATE company SET website=null,modifytime=%s  where id = %s''', now, company['id'])

                logger.info('set %s|%s %s to null', company['companyName'], company['id'], company['website'])
                # deletedArtifact.append(artifact['id'])

    logger.info('total: totally %s company, %s to be deleted', totalCnt, totoalDelCnt)


def transfer(ids):
    for companyId in ids:
        conn = db.connect_torndb()
        sql = '''select a.id,c.name as companyName,a.link,a.domain,a.type,a.name from artifact a join company c on c.id=a.companyId where c.id=%s and a.type in (4010)
                                        and a.link like '%s'   and (a.active='Y' or a.active is null ) and (c.active='Y' or c.active is null)
                        ''' % (companyId, '%%' + 'weixin.qq.com' + '%%')
        results = conn.query(sql)  # TODO
        conn.close()

        for artifact in results:
            conn = db.connect_torndb()
            conn.update('''UPDATE artifact SET active='N' where id = %s''', artifact['id'])

            deletedArtifact.append(artifact['id'])
            logger.info('delete %s: %s|%s|%s', artifact['companyName'], artifact['id'], artifact['name'],
                        artifact['link'])

            results = conn.query('''select a.id,c.name as companyName,a.link,a.domain,a.type,a.name from artifact a join company c on c.id=a.companyId where c.id=%s and a.type in (4020)

                                     ''', companyId)

            # print 'has 4020',len(results)
            if len(results) == 0:
                # weiboName = artifact['name'] if len(artifact['name']) > 0 else artifact['companyName']
                if len(artifact['name'].strip()) > 0 and artifact['name'].lower().find('wechat') < 0:
                    wechatName = artifact['name']
                else:
                    wechatName = artifact['companyName']
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.insert('''INSERT INTO artifact (companyid, type,name,link,createtime,modifytime)
                                VALUES (%s,%s,%s,%s,%s,%s)''', companyId, 4020, wechatName, artifact['link'], now, now)
                conn.close()
            else:
                logger.info('%s|%s already has 4020', artifact['companyName'], companyId)

            # trans source_artifact too
            sas = conn.query("select id, link, domain from source_artifact where "
                             "type=4010 and extended is null "
                             "and sourceCompanyId in ("
                             "select id from source_company where (active is null or active='Y') and companyId=%s"
                             ") order by id desc",
                             companyId)

            for sa in sas:
                if sa['link'] == artifact['link']:
                    conn.update('''UPDATE source_artifact SET type=4020 where id = %s''', sa['id'])
                    logger.info('trans source_artifact %s: %s|%s', artifact['companyName'], sa['id'], sa['link'])


def run():
    ids = getCompany()
    # ids = [143748]

    remove_wechat(ids)
    transfer(ids)

    for company_id in ids:
        company_aggregator_baseinfo.patch_website(company_id)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_object = open('remove_wechat_%s.txt' % now, 'w')
    for i in ids:
        file_object.write(str(i) + '\n')
    file_object.close()

    # logger.info('totally deleted %s artifacts!!!' % len(deletedArtifactifact))


if __name__ == "__main__":
    # logger.info("Start...")
    # print len(set(getCompany()))
    # print getWeiboArtifact()
    # print url_helper.get_domain('https://www.zhihu.com/question/49602855')[1]
    run()
