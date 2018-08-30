# -*- coding: utf-8 -*-
import os, sys
import time
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("corporate_migrate", stream=True)
logger = loghelper.get_logger("corporate_migrate")


if __name__ == "__main__":
    mongo = db.connect_mongo()
    mongo.task.corporate_decompose.update_one({ "_id" :ObjectId("58ef4775f871663c0485bf4e")},
                                          {"$set":{"replacement":[ { "oldCompanyId" : 26447, "newCompanyId" : 229500 } ]}})
    mongo.close()