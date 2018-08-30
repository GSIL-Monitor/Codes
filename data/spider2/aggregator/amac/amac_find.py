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
loghelper.init_logger("amac_find", stream=True)
logger = loghelper.get_logger("amac_find")

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
            mongo = db.connect_mongo()
            # collection = mongo.investor.checklist
            # clists = list( collection.find({ "crossChecked": True}))
            clists = conn.query("select * from investor where active is null or active !='N'")
            # clists = conn.query("select * from investor where id=358")
            logger.info('start preparing')
            AllcorIds = [i['corporateId'] for i in find_investor_alias.get_all_funded_company()]
            AllfullNames = find_investor_alias.get_companyFullNames(AllcorIds)
            Allgongshangs, _ = find_investor_alias.get_investors_by_name(AllfullNames)
            logger.info('finish preparing')


            for investor in clists:
            # investors = conn.query("select * from famous_investor where (active is null or active='Y') and investorId=4518")
            # for investor in investors:
                logger.info("********Checking :%s, %s", investor["name"], investor["id"])
                investor["investorId"] = int(investor["id"])
                amac_util.check_amacType(investor["investorId"])
                amac_util.find_investor_alias_by_fund(investor["investorId"])
                amac_util.find_investor_alias_by_manager(investor["investorId"])

                amac_util.find_investor_alias(investor["investorId"])

                find_investor_alias.method1(investor["investorId"],investor["name"])
                find_investor_alias.method2(investor["investorId"],investor["name"],Allgongshangs,len(AllfullNames))
            # amac_util.find_investor_alias_by_fund(114)

            mongo.close()
            conn.close()

        logger.info('end')



        time.sleep(60*60)
