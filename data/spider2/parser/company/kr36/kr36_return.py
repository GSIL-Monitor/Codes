# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from kr36_location import kr36_cities


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, db
import util, name_helper, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("36kr_company_parser", stream=True)
logger = loghelper.get_logger("36kr_company_parser")

SOURCE = 13020  #36kr
TYPE = 36001    #公司信息

#mongo
mongo = db.connect_mongo()
collection = mongo.raw.projectdata

if __name__ == "__main__":
    conn = db.connect_torndb()
    ids = conn.query("select * from source_company where companyId is null and processStatus=2 and (active is null or active='Y') and source=13020")
    for id in ids:
        sourceId = id["sourceId"]
        logger.info(type(sourceId))
        logger.info("sourceId: %s", sourceId)
        collection.update({"source": SOURCE, "type": 36001, "key_int": int(sourceId)}, {"$set": {"processed": False}})
        exit()
