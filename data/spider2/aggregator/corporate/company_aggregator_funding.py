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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../funding'))
import funding_aggregator


#logger
loghelper.init_logger("company_aggregator_funding", stream=True)
logger = loghelper.get_logger("company_aggregator_funding")


def aggregate_funding(company_id, sc, test=False):
    conn = db.connect_torndb()
    sfs = conn.query("select * from source_funding where sourceCompanyId=%s", sc["id"])
    for sf in sfs:
        funding_flag = funding_aggregator.aggregate1(sf,sc,company_id,test)
        if funding_flag:
            if not test:
                conn = db.connect_torndb()
                conn.update("update source_funding set processStatus=2 where id=%s", sf["id"])
                conn.close()


    # update company stage
    if not test:
        funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                           company_id)
        if funding is not None:
            conn.update("update company set round=%s, roundDesc=%s where id=%s",
                        funding["round"],funding["roundDesc"],company_id)
        else:
            conn.update("update company set round=null, roundDesc=null where id=%s", company_id)
    conn.close()



