# -*- coding: utf-8 -*-
#删除无金额和投资人的记录
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("remove_empty_funding", stream=True)
logger = loghelper.get_logger("remove_empty_funding")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    fs = conn.query("select * from funding where active is null or active='Y' and investment=0 order by id")
    num = 0
    for f in fs:
        firs = conn.query("select * from funding_investor_rel where fundingId=%s", f["id"])
        if len(firs) == 0:
            num += 1
            logger.info("delete funding: %s", f["id"])
            conn.update("update funding set active='N' where id=%s", f["id"])

    conn.close()
    logger.info("num: %s", num)
    logger.info("End.")