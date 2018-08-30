# -*- coding: utf-8 -*-
import os, sys
import time
import find_company
import company_aggregator
import company_info_expand
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

import corporate_util


#logger
loghelper.init_logger("company_decompose", stream=True)
logger = loghelper.get_logger("company_decompose")



if __name__ == '__main__':

    logger.info("python company_decompose")
    while True:
        mongo = db.connect_mongo()

        collection = mongo.task.corporate_decompose

        tasks = list(collection.find({"processStatus":0}))
        for t in tasks:
            logger.info("decompose: %s", t["newCorporateIds"])
            corporate_util.decompose(t["oldCorporateId"], t["newCorporateIds"], t["replacement"])

            collection.update_one({"_id": t["_id"]},{"$set":{"processStatus":1}})

        mongo.close()

        time.sleep(60)

