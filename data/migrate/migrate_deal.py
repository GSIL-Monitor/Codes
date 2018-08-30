# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("migrate_deal", stream=True)
logger = loghelper.get_logger("migrate_deal")


def migrate():
    conn = db.connect_torndb()
    deals =  conn.query("select * from deal "\
                      " where status > 19000 ")
    for deal in deals:
        id = deal['id']
        orgId = deal['organizationId']
        status = deal['status']
        portfolioStatus = deal['portfolioStatus']
        # print orgId
        # print status
        # print portfolioStatus

        stages = conn.query("select * from deal_stage_defination where organizationId = %s", orgId)
        if len(stages) == 0:
            print 'init stages'
            init_stages = []
            init_stages.append({'name': 'New Deal', 'sort': 0, 'type': 19010, 'portfolio': 'N'})
            init_stages.append({'name': 'Active Deal', 'sort': 10, 'type': 19020,  'portfolio': 'N'})
            init_stages.append({'name': 'DD', 'sort': 20, 'type': 19030, 'portfolio': 'N'})
            init_stages.append({'name': 'TS', 'sort': 30, 'type': 19040, 'portfolio': 'N'})
            init_stages.append({'name': 'Portfolio', 'sort': 40, 'type': 19050, 'portfolio': 'Y'})

            init_stages.append({'name': '正常发展', 'sort': 0, 'type': 50010, 'portfolio': 'Y'})
            init_stages.append({'name': '资金紧张', 'sort': 10, 'type': 50020, 'portfolio': 'Y'})
            init_stages.append({'name': '融资中', 'sort': 20, 'type': 50030, 'portfolio': 'Y'})
            init_stages.append({'name': '融完下轮', 'sort': 30, 'type': 50040, 'portfolio': 'Y'})
            init_stages.append({'name': '退出', 'sort': 40, 'type': 50050, 'portfolio': 'Y'})
            init_stages.append({'name': '清算', 'sort': 50, 'type': 50060, 'portfolio': 'Y'})

            for init in init_stages:
                conn.insert("insert deal_stage_defination(name, sort, organizationId, type, portfolio, "
                            "createTime, createUser, modifyTime, modifyUser, active )"
                            " values (%s, %s, %s, %s, %s, now(), 0, now(), 0, 'Y' )"
                            ,init['name'], init['sort'], orgId, type, init['portfolio'])
            stages = conn.query("select * from deal_stage_defination where organizationId = %s", orgId)

        print 'updating stageId, portfolioStageId'
        stageId = None
        portfolioStageId = None
        for stage in stages:
            if stage['type'] == status:
                stageId = stage['id']
            if stage['type'] == portfolioStatus:
                portfolioStageId = portfolioStatus

        print 'updating id: %s ' % id,
        conn.update("update deal set stageId = %s, portfolioStageId=%s where id = %s" ,
                    stageId, portfolioStageId, id)

    # conn.update("update deal_stage_defination set type = 0 where type < 50000 and id > 0")
    # conn.update("update deal_stage_defination set type = 1 where type > 50000 and id > 0")

    conn.close()


if __name__ == '__main__':
    migrate()