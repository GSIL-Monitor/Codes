# -*- coding: utf-8 -*-
import os, sys, re, json, time
import datetime
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import amac_util
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper
import db

import find_investor_alias

#logger
loghelper.init_logger("fof_find", stream=True)
logger = loghelper.get_logger("fof_find")

# investor_alias amacType amacId
# investor_alias_candidate amacType amacId

DATE = None

if __name__ == "__main__":
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE:
            # init
            # time.sleep(30*60)
            DATE = datestr

            conn = db.connect_torndb()
            clists = conn.query("select * from fof where (active is null or active='Y')")
            for investor in clists:
            # investors = conn.query("select * from famous_investor where (active is null or active='Y') and investorId=4518")
            # for investor in investors:
                logger.info("********Checking :%s, %s", investor["name"], investor["id"])
                investor["investorId"] = int(investor["id"])
                amac_util.check_amacType_fof(investor["investorId"])
                amac_util.find_fof_alias_by_fund(investor["investorId"])
                amac_util.find_fof_alias_by_manager(investor["investorId"])

                amac_util.find_fof_alias(investor["investorId"])

            conn.close()



        time.sleep(60*60)
