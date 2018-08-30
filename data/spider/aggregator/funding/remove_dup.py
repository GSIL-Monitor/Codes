# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("funding_remove_dup", stream=True)
logger = loghelper.get_logger("funding_remove_dup")

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select id from company order by id")
    for c in cs:
        logger.info(c["id"])
        '''
        fs = conn.query("select * from funding where companyId=%s and (active is null or active='Y') order by round,fundingDate",c["id"])
        round = None
        fundingDate = None
        for f in fs:
            logger.info("%s - %s - %s",f["id"],f["round"],f["fundingDate"])
            c_round = f["round"]
            c_fundingDate = f["fundingDate"]
            if round == c_round and fundingDate == c_fundingDate:
                logger.info("remove %s", f["id"])
                conn.update("update funding set active='N' where id=%s", f["id"])
            else:
                round =c_round
                fundingDate = c_fundingDate

        '''
        
        fs = conn.query("select * from funding where companyId=%s and (active is null or active='Y') order by round,id",c["id"])
        round = None
        for f in fs:
            logger.info("%s - %s",f["id"],f["round"])
            c_round = f["round"]
            if round == c_round:
                logger.info("remove %s", f["id"])
                conn.update("update funding set active='N' where id=%s", f["id"])
            else:
                round =c_round

        fs = conn.query("select * from funding where companyId=%s and (active is null or active='Y') order by fundingDate, round",c["id"])
        fundingDate = None
        for f in fs:
            logger.info("%s - %s",f["id"],f["fundingDate"])
            if f["fundingDate"] is None:
                continue
            c_fundingDate = f["fundingDate"] - datetime.timedelta(days=f["fundingDate"].day-1)
            if fundingDate == c_fundingDate:
                logger.info("remove %s", f["id"])
                conn.update("update funding set active='N' where id=%s", f["id"])
            else:
                fundingDate =c_fundingDate

    conn.close()
    logger.info("End.")





