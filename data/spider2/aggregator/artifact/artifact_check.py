# -*- coding: utf-8 -*-
# TODO
# 当 artifact 数量超过 10个时
# 没有排名的网站, 没有评分的IOS, 下载量小于1000 的 artifact 不显示
import sys, os
import datetime, time
import json, re
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper


#logger
loghelper.init_logger("artifact_trends_update", stream=True)
logger = loghelper.get_logger("artifact_trends_update")

cnt = 0

def get_artifact(companies):
    global cnt
    conn = db.connect_torndb()
    conn_crawler = db.connect_torndb_crawler()

    for company in companies:
        companyId = company['id']
        artifacts = conn.query("select * from artifact where companyId = %s", companyId)

        # logger.info(artifacts)

        if len(artifacts) > 10:
            company_index = conn_crawler.get("select * from company_index where companyId = %s", companyId)

            if company_index is not None:
                # logger.info(company_index)
                for artifact in artifacts:
                    # logger.info(artifact)
                    type = artifact['type']
                    artifactId = artifact['id']
                    trend_data = None
                    if type == 4010:
                        if artifact['domain'] is not None:
                            if company_index['alexa'] is not None:
                                sql = "select * from alexa"+str(company_index['alexa'])+" where companyId = %s  and artifactId = %s order by date desc limit 1"
                                alexa_data = conn_crawler.get(sql, companyId, artifactId)
                                if alexa_data is not None:
                                        if alexa_data['rankGlobal'] is not None and alexa_data['rankGlobal'] > 0:
                                            trend_data = alexa_data['rankGlobal']

                    if type == 4020:
                        pass

                    if type == 4030:
                        pass

                    if type == 4040:
                        if company_index['ios'] is not None:
                            sql = "select * from ios"+str(company_index['ios'])+" where companyId = %s  and artifactId = %s order by date desc limit 1"
                            ios_data = conn_crawler.get(sql, companyId, artifactId)
                            if ios_data is not None:
                                if ios_data['comment'] is not None:
                                    trend_data = ios_data['comment']

                    if type == 4050:
                        if company_index['android'] is not None:
                            sql = "select * from android"+ str(company_index['android'])+" where companyId = %s  and artifactId = %s  and type=16040 order by date desc limit 1"
                            android_data = conn_crawler.get(sql, companyId, artifactId)
                            if android_data is not None:
                                if android_data['download'] is not None:
                                    if android_data['download'] > 1000:
                                        trend_data = android_data['download']

                    logger.info(trend_data)
                    if trend_data is not None:
                        logger.info("artifactId = %s", artifactId)
                        if artifact['verify'] != 'N':
                            update_sql = "update artifact set rank =%s, active='Y', modifyTime=now() where id=%s"
                            conn.update(update_sql, int(trend_data), int(artifactId))
                    else:
                        if type == 4020 or type == 4030:
                            update_sql = "update artifact set active='Y', modifyTime=now() where id=%s"
                            conn.update(update_sql, int(artifactId))
                        else:
                            update_sql = "update artifact set active='N', modifyTime=now() where id=%s"
                            conn.update(update_sql, int(artifactId))



    conn.close()
    conn_crawler.close()
    cnt += 1000
    begin()



def begin():
    global cnt
    conn = db.connect_torndb()

    companies = conn.query("select * from company limit %s,1000", cnt)
    logger.info('Done count = %s', cnt)
    if len(companies) == 0:
        logger.info("Finish.")
        exit()
    get_artifact(companies)
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    begin()
