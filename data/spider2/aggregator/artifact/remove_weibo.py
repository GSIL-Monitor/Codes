# -*- coding: utf-8 -*-
import sys, os

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper
import datetime

# logger
loghelper.init_logger("remove_weibo", stream=True)
logger = loghelper.get_logger("remove_weibo")

# id code name return ids  4010

deletedArtifact = []


def getWeiboArtifact():
    conn = db.connect_torndb()
    results = conn.query('''select distinct a.link,a.domain,a.type,a.name from artifact a join company c on c.id=a.companyId where c.id=133457 and a.type in (4040,4050)
                                and (a.active='Y' or a.active is null) and (c.active='Y' or c.active is null)
          ''')  # todo
    conn.close()

    weiboArtifact = []
    for r in results:
        # print r, r['name']
        weiboArtifact.append(r['domain'])
    return weiboArtifact


def getCompany(domain='weibo.com', type=4010):
    conn = db.connect_torndb()
    results = conn.query('''select distinct c.id,c.code,c.name,a.link,a.domain from artifact a join company c on c.id=a.companyId where (a.domain=%s ) and a.type=%s
                            and (a.active='Y' or a.active is null)
                             and (c.active='Y' or c.active is null)
      ''',
                         domain, type)  # TODO
    conn.close()

    ids = []
    for artifact in results:
        if artifact['id'] == 133457: continue
        # if artifact['domain'] is None:
        #     flag, domain = url_helper.get_domain(artifact['link'])
        # else:
        #     domain = artifact['domain']
        # if domain == 'weibo.com':
        if 1:
            print artifact['id'], artifact['code'], artifact['name'], artifact['link']
            ids.append(artifact['id'])
    return set(ids)


def remove_weibo(ids):
    weiboArtifact = getWeiboArtifact()
    totalCnt, totoalDelCnt = 0, 0

    for companyId in ids:
        conn = db.connect_torndb()
        results = conn.query('''select a.id, c.name as companyName,a.link,a.domain,a.type,a.name from artifact a join company c on c.id=a.companyId where c.id=%s and a.type in (4040,4050)
                                    and (a.active='Y' or a.active is null  ) and (c.active='Y' or c.active is null)
              ''', companyId)
        conn.close()

        cnt = 0
        for artifact in results:
            totalCnt += 1
            if artifact['domain'] in weiboArtifact:
                cnt += 1
                totoalDelCnt += 1
                conn = db.connect_torndb()
                conn.update('''UPDATE artifact SET active='N' where id = %s''', artifact['id'])

                logger.info('delete %s: %s|%s|%s', artifact['companyName'], artifact['id'], artifact['name'],
                            artifact['link'])
                deletedArtifact.append(artifact['id'])

        if len(results) == 0: continue
        logger.info('%s|%s : totally %s artifacts, %s to be deleted', companyId, results[0]['companyName'],
                    len(results), cnt)

    logger.info('total: totally %s artifacts, %s to be deleted', totalCnt, totoalDelCnt)


def transfer(ids):
    for companyId in ids:
        conn = db.connect_torndb()
        results = conn.query('''select a.id,c.name as companyName,a.link,a.domain,a.type,a.name from artifact a join company c on c.id=a.companyId where c.id=%s and a.type in (4010)
                                and a.domain='weibo.com'     and (a.active='Y' or a.active is null ) and (c.active='Y' or c.active is null)
                ''', companyId)  # TODO
        conn.close()

        for artifact in results:
            conn = db.connect_torndb()
            conn.update('''UPDATE artifact SET active='N' where id = %s''', artifact['id'])

            deletedArtifact.append(artifact['id'])
            logger.info('delete %s: %s|%s|%s', artifact['companyName'], artifact['id'], artifact['name'],
                        artifact['link'])

            results = conn.query('''select a.id,c.name as companyName,a.link,a.domain,a.type,a.name from artifact a join company c on c.id=a.companyId where c.id=%s and a.type in (4030)
                                             and (a.active='Y' or a.active is null ) and (c.active='Y' or c.active is null)
                            ''', companyId)

            if len(results) == 0:
                # weiboName = artifact['name'] if len(artifact['name']) > 0 else artifact['companyName']
                if len(artifact['name'].strip()) > 0 and artifact['name'].lower().find('sina') < 0:
                    weiboName = artifact['name']
                else:
                    weiboName = artifact['companyName']
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.insert('''INSERT INTO artifact (companyid, type,name,link,createtime,modifytime)
                                VALUES (%s,%s,%s,%s,%s,%s)''', companyId, 4030, weiboName, artifact['link'], now, now)
                conn.close()


def remove_dup_weibo():
    ids = [159872, 17558, 13603, 157699, 112133, 17093, 69133, 13329, 112455, 19478, 112297, 19485, 19486, 120497,
           11819, 142258, 168939, 20147, 9781, 6712, 124255, 19006, 10303, 13889, 15938, 15943, 117367, 100225, 143442,
           192161, 49679, 11872, 27748, 127083, 13427, 20585, 73341, 8830, 4736, 25729, 152195, 36492, 11918, 13457,
           14995, 17556, 2712, 11929, 151996, 11932, 134817, 123555, 138353, 4264, 120492, 79533, 112925, 12979, 17588,
           4807, 146120, 67753, 120529, 7888, 6521, 8927, 19169, 172262, 112082, 152304, 5361, 17651, 10504, 136825,
           15626, 8462, 142096, 13585, 17246, 18217, 9522, 124213, 110404, 11077, 113905, 15178, 17232, 153425, 17248,
           149904, 12646, 5999, 143217, 18067, 20542, 3968, 18817, 114051, 105111, 7490, 45968, 156143, 14243, 120049,
           5033, 145835, 15682, 19378, 10676, 20412, 5962, 19908, 12743, 75379, 10200, 13790, 17234, 20463, 31315,
           19960, 80377, 20479, 153598, 18985, 8545, 170218, 10821, 7623, 5731, 130671, 157544, 7797, 168612, 121767,
           87927, 142055, 77890, 150835, 141617, 46409, 117785, 168590, 111461, 1896, 122767, 18338, 127416, 16315,
           122004, 169073, 18940, 151531, 7189, 46033, 127542, 14424, 45689, 71701, 14978, 15007, 6315, 12986, 112245,
           20682, 143092, 20725, 66433, 136407, 15631, 42115, 54552, 169056, 16165, 19295, 7031, 14201, 171406, 18068,
           13232, 11710, 18378, 11776, 13344, 16489, 12906, 111728, 20105, 3727, 20137, 17636, 60189, 19248, 17631,
           50531, 14239, 62897, 153331, 19400, 6093, 78804, 92128, 12615, 13292, 18242, 3583, 15385, 2206, 10440, 9399,
           19653, 12998, 43167, 12022, 19191, 54570, 11479, 10543, 13280, 11614, 88420, 14202, 11650, 6024, 145322,
           58322, 3122, 19554, 143496, 2199, 72040, 15106, 123375, 10562, 121714, 13916, 16477, 80111, 169524, 10670,
           83921, 4357, 142131, 18234, 11603, 23199, 5075, 19269, 12124, 74547, 33843, 30602, 140890, 8073, 155977,
           6523, 7659, 44153, 20695, 112854, 7210, 69854, 11313, 5499, 170943, 3488, 20523, 112500, 111890, 135549,
           127505, 13138, 10741, 11525, 12713, 12555, 146154, 116613, 127939, 111203, 13276, 170902]
    for companyId in ids:
        conn = db.connect_torndb()
        results = conn.query('''select a.id, c.name as companyName,a.link,a.domain,a.type,a.name,a.createtime from artifact a join company c on c.id=a.companyId where c.id=%s and a.type in (4030)
                                           and (a.active='Y' or a.active is null  )
                     ''', companyId)
        conn.close()

        if len(results) > 1:
            for weibo in results:
                if weibo['createtime'] is None:
                    conn = db.connect_torndb()
                    conn.update('''UPDATE artifact SET active='N' where id = %s''', weibo['id'])
                    logger.info('delete %s: %s|%s|%s', weibo['companyName'], weibo['id'], weibo['name'],
                                weibo['link'])
                    conn.close()
        elif len(results) == 1:
            weibo = results[0]
            logger.info('%s has only 1 weibo,update its time', weibo['companyName'])

            if weibo['createtime'] is None:
                conn = db.connect_torndb()
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.update('''UPDATE artifact SET createtime=%s,modifytime=%s where id = %s''', now, now, weibo['id'])
                conn.close()

def recover_weibo():
    ids=[416525,813105,813106,813107,813108,813109,813110,813111,813112,813113,813114,813115,813116,813117,813118,813119,813120,813121,813122,813123,813124,813125,813126,813127,813128,813129,813130,813131,813132,813134,813135,813136,813137,813138,813139,813140,813141,813142,813143,813144,813145,813146,813147,825722,894176,980691,1017331,1017332,1132786]
    for artifact in ids:
        conn = db.connect_torndb()
        conn.update('''UPDATE artifact SET active='Y' where id = %s''', artifact)
        conn.close()

def run():
    ids = getCompany()
    # ids = [78804]
    transfer(ids)
    remove_weibo(ids)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_object = open('remove_weibo_%s.txt' % now, 'w')
    for i in deletedArtifact:
        file_object.write(str(i) + '\n')
    file_object.close()

    logger.info('totally deleted %s artifacts!!!' % len(deletedArtifact))


if __name__ == "__main__":
    # logger.info("Start...")
    # print len(set(getCompany()))
    # print getWeiboArtifact()
    # print url_helper.get_domain('https://www.zhihu.com/question/49602855')[1]
    # run()
    # remove_dup_weibo()
    recover_weibo()
