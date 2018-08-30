# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db

#logger
loghelper.init_logger("repair_company_fullname", stream=True)
logger = loghelper.get_logger("repair_company_fullname")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()

    conn.close()

    logger.info("End.")