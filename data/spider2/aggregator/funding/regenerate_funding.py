# -*- coding: utf-8 -*-
#重新聚合融资信息
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import funding_aggregator

#logger
loghelper.init_logger("regenerate_funding", stream=True)
logger = loghelper.get_logger("regenerate_funding")


def process(company_id):
    logger.info("company id: %s", company_id)
    #delete all funding
    conn = db.connect_torndb()
    fs = conn.query("select id from funding where companyId=%s", company_id)
    for f in fs:
        funding_id = f["id"]
        conn.execute("delete from funding_investor_rel where fundingId=%s", funding_id)
        conn.execute("delete from funding where id=%s", funding_id)

    #
    scs = conn.query("select id from source_company where companyId=%s and (active is null or active='Y')", company_id)
    for sc in scs:
        source_company_id = sc["id"]
        logger.info("source company id: %s", source_company_id)
        sfs = conn.query("select * from source_funding where sourceCompanyId=%s", source_company_id)
        for sf in sfs:
            logger.info("source funding id: %s",sf["id"])
            funding_aggregator.aggregate(sf)
    conn.close()

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select id from company where active is null or active='Y' order by id")
    #cs = conn.query("select id from company where id=18871")
    conn.close()
    for c in cs:
        company_id= c["id"]
        process(company_id)

    logger.info("End.")