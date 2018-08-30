# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util

#logger
loghelper.init_logger("company_aggregator_footprint", stream=True)
logger = loghelper.get_logger("company_aggregator_footprint")


def aggregate_footprint(company_id, source_company_id):
    logger.info("aggregate_footprint")
    conn = db.connect_torndb()
    sfs = list(conn.query("select * from source_footprint where sourceCompanyId=%s", source_company_id))
    for sf in sfs:
        f = conn.get("select * from footprint where companyId=%s and description=%s limit 1", company_id, sf["description"])
        if f is None:
            logger.info(sf["description"])
            aggregator_db_util.insert_footprint(company_id, sf)
    conn.close()



