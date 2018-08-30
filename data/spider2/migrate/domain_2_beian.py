# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db
import name_helper

#logger
loghelper.init_logger("domain_2_beian", stream=True)
logger = loghelper.get_logger("domain_2_beian")

#mongo
mongo = db.connect_mongo()
collection = mongo.info.beian


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    domains = conn.query("select * from domain")
    for domain in domains:
        if domain["beianhao"] is None:
            continue
        logger.info(domain["domain"])
        domain.pop("id")
        domain.pop("companyId")
        domain.pop("createUser")
        domain.pop("modifyUser")
        domain.pop("confidence")
        domain.pop("verify")
        domain.pop("active")

        beian = collection.find_one({"domain":domain["domain"],"organizer":domain["organizer"]})
        if beian is None:
            collection.insert(domain)
        #break

    domains = conn.query("select * from source_domain")
    for domain in domains:
        if domain["beianhao"] is None:
            continue
        logger.info(domain["domain"])
        domain.pop("id")
        domain.pop("sourceCompanyId")
        domain.pop("verify")

        beian = collection.find_one({"domain":domain["domain"],"organizer":domain["organizer"]})
        if beian is None:
            collection.insert(domain)
        #break

    conn.close()

    logger.info("End.")